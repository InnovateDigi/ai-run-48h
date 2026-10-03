#!/usr/bin/env python3
"""Revenue-run monitor: marketplace sales (optional), Stripe payments and inbox activity for you@example.com.
Prints one JSON object. `--verbose` adds message previews and buyer and sender addresses, so do not paste that output anywhere public.
Never prints secrets. Run it every 10 minutes from cron or any scheduler; it keeps no loop of its own.

Scheduled wake-ups, run/wakeups.json: a list of {"id", "at", "note"}, with "at" in UTC as YYYY-MM-DDTHH:MM:SSZ. An entry is reported
as SCHEDULED WAKE once its time has passed and its id is not in run/wakeups_done.txt. An entry more than STALE_HOURS past its time is
reported as stale and not fired, so a schedule left over from an earlier run cannot fire all at once: edit or delete it.

Setup: copy .env.local.example to .env.local in your project root and fill in the keys, then replace the
YOUR_... placeholders below. Set PROJECT_ROOT if you run the script from somewhere else."""
import json, os, sys, urllib.request, urllib.parse, urllib.error, base64, time, datetime

ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())
if not os.path.exists(f"{ROOT}/.env.local"):
    sys.exit(f"no .env.local in {ROOT}: copy .env.local.example there and fill it in (or set PROJECT_ROOT)")


def load_env(path):
    """KEY=VALUE lines. Also accepts `export KEY=value`, spaces around the = and one pair of quotes around the value."""
    env = {}
    for line in open(path, encoding="utf-8-sig"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key.startswith("export "):
            key = key[7:].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[key] = value
    return env


ENV = load_env(f"{ROOT}/.env.local")
FROM_ADDRESS = "you@example.com"
ACCOUNT = "YOUR_ZOHO_ACCOUNT_ID"
CONN = "YOUR_CONNECTED_ACCOUNT_ID"
USER = "YOUR_COMPOSIO_USER_ID"
SPAM_FOLDER = "YOUR_SPAM_FOLDER_ID"
SENT_FOLDER = "YOUR_SENT_FOLDER_ID"
# Optional marketplace check. Set MARKETPLACE_TOKEN in .env.local and point this at your marketplace's sales API.
# The field names used below (success, sales, price, refunded) follow one marketplace's API; adapt them to yours.
# The check is skipped while this still starts with https://YOUR_ or the token is a placeholder.
MARKETPLACE_SALES_URL = "https://YOUR_MARKETPLACE_API/v2/sales"
# Baseline: handover time (ms since epoch). Messages received before this were audited by hand and are ignored.
BASELINE_MS = 0
# Sender fragments to treat as automated mail rather than a human reply. Add the services and newsletters that email your mailbox.
AUTOMATED = ("noreply", "no-reply", "donotreply")
# A scheduled wake-up this many hours past its time is reported as stale instead of firing.
STALE_HOURS = 36

def http(url, method="GET", headers=None, data=None, timeout=40):
    req = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        out = {"_error": f"HTTPError: HTTP Error {e.code}: {e.reason}"}
        if e.headers.get("x-vercel-mitigated"):  # bot challenge in front of the API: do not retry into it
            out["_blocked"] = e.headers.get("x-vercel-id") or True
        return out
    except Exception as e:  # report, don't crash the watcher
        return {"_error": f"{type(e).__name__}: {str(e)[:160]}"}

def composio(slug, args):
    key = ENV.get("COMPOSIO_API_KEY", "")
    if not key or key.startswith("YOUR_"):
        return {"_error": "COMPOSIO_API_KEY is missing, or still a placeholder, in .env.local"}
    body = json.dumps({"connected_account_id": CONN, "user_id": USER, "version": "latest", "arguments": args}).encode()
    return http(f"https://backend.composio.dev/api/v3/tools/execute/{slug}", "POST",
                {"x-api-key": key, "Content-Type": "application/json"}, body)

def list_mail(extra=None, limit=40):
    args = {"account_id": ACCOUNT, "limit": limit, "region": "eu"}
    if extra: args.update(extra)
    r = composio("ZOHO_MAIL_MESSAGES_LIST_EMAILS", args)
    d = r.get("data", {})
    d = d.get("data", d) if isinstance(d, dict) else d
    err = r.get("_error") or r.get("error")
    if r.get("_blocked"):
        err = f"{err} [composio blocked by Vercel bot challenge]"
    return (d if isinstance(d, list) else []), err

def mail_state(readable, blocked):
    path = f"{ROOT}/run/logs/monitor_state.json"
    try: st = json.load(open(path))
    except Exception: st = {}
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if readable:
        st["last_mail_ok"] = now
        st.pop("mail_unreadable_since", None)
    else:
        st.setdefault("mail_unreadable_since", now)
    st["blocked_by_bot_challenge"] = bool(blocked)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        json.dump(st, open(path, "w"))
    except Exception:
        pass
    return {k: st[k] for k in ("last_mail_ok", "mail_unreadable_since") if k in st}

def main():
    verbose = "--verbose" in sys.argv
    out, errors = {}, []

    mt = ENV.get("MARKETPLACE_TOKEN", "")
    if mt and not mt.startswith("YOUR_"):  # optional: skipped until you set a real token
        if MARKETPLACE_SALES_URL.startswith("https://YOUR_"):
            errors.append("marketplace: MARKETPLACE_TOKEN is set but MARKETPLACE_SALES_URL in monitor.py is still the placeholder, so the check was skipped")
        else:
            g = http(MARKETPLACE_SALES_URL, headers={"Authorization": f"Bearer {mt}"})
            if g.get("success"):
                sales = g.get("sales", [])
                out["marketplace_sales"] = len(sales)
                out["marketplace_gross_pence"] = sum(int(s.get("price", 0)) for s in sales if not s.get("refunded"))
                if verbose:
                    out["marketplace_detail"] = [{"at": s.get("created_at"), "product": s.get("product_name"), "price": s.get("formatted_total_price") or s.get("price"),
                                                  "email": s.get("email"), "refunded": s.get("refunded")} for s in sales[:10]]
            else:
                errors.append(f"marketplace: {g.get('_error') or g.get('message')}")

    sk = ENV.get("STRIPE_SECRET_KEY") or os.environ.get("STRIPE_SECRET_KEY")
    if sk and not sk.startswith("YOUR_"):
        auth = "Basic " + base64.b64encode(f"{sk}:".encode()).decode()
        s = http("https://api.stripe.com/v1/charges?limit=20", headers={"Authorization": auth})
        if "data" in s:
            paid = [c for c in s["data"] if c.get("paid") and not c.get("refunded") and c.get("created", 0) * 1000 >= BASELINE_MS]
            out["stripe_paid"] = len(paid)
            out["stripe_gross_pence"] = sum(c.get("amount", 0) for c in paid)
            if verbose:
                out["stripe_detail"] = [{"at": c.get("created"), "amount": c.get("amount"), "email": (c.get("billing_details") or {}).get("email"),
                                         "desc": c.get("description")} for c in paid]
        else:
            errors.append(f"stripe: {s.get('_error') or (s.get('error') or {}).get('message')}")

    msgs, err = list_mail()
    if err: errors.append(f"mail: {err}")
    blocked = bool(err and "blocked by Vercel" in str(err))
    if blocked:  # single probe per run; skip the second call rather than push more traffic at the challenge
        spam = []
        errors.append("spam: skipped (composio blocked)")
    else:
        spam, err2 = list_mail({"folder_id": SPAM_FOLDER}, 15)
        if err2: errors.append(f"spam: {err2}")
    out["mail_readable"] = not any(e.startswith(("mail:", "spam:")) for e in errors)
    out.update(mail_state(out["mail_readable"], blocked))
    seen, human, bounces = set(), [], []
    for m in msgs + spam:
        mid = str(m.get("messageId"))
        if mid in seen: continue
        seen.add(mid)
        try: t = int(m.get("receivedTime", 0))
        except Exception: t = 0
        if t < BASELINE_MS: continue
        if str(m.get("folderId")) == SENT_FOLDER: continue
        frm = (m.get("fromAddress") or "").lower()
        if frm == FROM_ADDRESS.lower(): continue
        item = {"id": mid, "folder": m.get("folderId"), "from": m.get("fromAddress"), "subject": (m.get("subject") or "")[:120],
                "at": time.strftime("%m-%d %H:%MZ", time.gmtime(t / 1000))}
        if verbose: item["summary"] = (m.get("summary") or "")[:300]
        if "mailer-daemon" in frm or "postmaster" in frm:
            bounces.append(item)
        elif not any(a in frm for a in AUTOMATED):
            human.append(item)
    out["inbox_new"] = human
    out["bounces"] = bounces
    # scheduled wake-ups (run/wakeups.json); handled ones are listed in run/wakeups_done.txt
    due, pending = [], []
    try:
        done = set(open(f"{ROOT}/run/wakeups_done.txt").read().split()) if os.path.exists(f"{ROOT}/run/wakeups_done.txt") else set()
        now = datetime.datetime.now(datetime.timezone.utc)
        for w in json.load(open(f"{ROOT}/run/wakeups.json")):
            at = datetime.datetime.strptime(w["at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            if at > now: continue
            due.append(w["id"])
            if w["id"] in done: continue
            late = (now - at).total_seconds() / 3600
            if late > STALE_HOURS:
                errors.append(f"wakeups: {w['id']} is {late:.0f} hours past its time, so it was not fired. Edit its time or delete it in run/wakeups.json")
            else:
                pending.append(f"SCHEDULED WAKE {w['id']}: {w['note']}")
    except FileNotFoundError:
        pass
    except Exception as e:
        errors.append(f"wakeups: {type(e).__name__}: {str(e)[:80]}")
    n_real_errors = len(errors)
    if errors or pending: out["errors"] = errors + pending
    out["fingerprint"] = "|".join([
        f"k{out.get('marketplace_sales', '?')}", f"s{out.get('stripe_paid', '?')}",
        "m" + ",".join(sorted(i["id"] for i in human)), "b" + ",".join(sorted(i["id"] for i in bounces)),
        "e" + str(n_real_errors)]) + (f"|w{len(due)}" if due else "")
    print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()

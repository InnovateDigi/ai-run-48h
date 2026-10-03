#!/usr/bin/env python3
"""Mailer for you@example.com via Composio -> Zoho Mail (EU).

Library:  send(to, subject, body, kind="outreach", meta=None, html=False) -> dict
          is_suppressed(address) -> bool
CLI:      mailer.py send --to X --subject S --body-file F [--kind K]
          mailer.py queue run/outreach/queue.json [--min-gap 240 --max-gap 420] [--limit N] [--dry-run]
Every send is appended to run/outreach/sent_log.jsonl. Plain text only. One recipient per message. Never prints secrets.

Queue items are {"to", "subject", "body"} plus an optional "kind", "meta" and "hold" (true = skip for now).
--limit N stops after N sends (leave it out for no limit). --dry-run prints what would be sent and sends nothing.

Suppression list, run/outreach/suppression.txt: UTF-8 text with one or more entries per line, separated by spaces, commas or semicolons.
An entry is an address, `Name <address>`, `mailto:address`, `name @ domain` (spaces around the @), `@domain.com`, `*@domain.com`,
`*.domain.com`, `domain.com`, `domain.com.` or `https://www.domain.com/page`. A domain entry covers the whole domain, subdomains
included, and a leading `www.` is ignored. A `#` starts a comment, and plain words after an entry are read as a note.
The file is re-read before every send. A line with no address or domain in it, or with a piece that is neither, raises
SuppressionError: the gate fails and nothing is sent until the line is fixed. A line is never skipped silently.

Setup: replace the YOUR_ placeholders and the sender address below. COMPOSIO_API_KEY is read from .env.local in the project root."""
import json, os, re, sys, time, random, argparse, urllib.request, urllib.error, datetime

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
ACCOUNT = "YOUR_ZOHO_ACCOUNT_ID"
CONN = "YOUR_CONNECTED_ACCOUNT_ID"
USER = "YOUR_COMPOSIO_USER_ID"
FROM = "you@example.com"
LOG = f"{ROOT}/run/outreach/sent_log.jsonl"
SUPPRESS = f"{ROOT}/run/outreach/suppression.txt"
EMAIL = re.compile(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _check_config():
    todo = [n for n, v in (("ACCOUNT", ACCOUNT), ("CONN", CONN), ("USER", USER)) if v.startswith("YOUR_")]
    if todo or "example.com" in FROM:
        sys.exit("replace the YOUR_ placeholders and the sender address at the top of mailer.py first" + (f" ({', '.join(todo)})" if todo else ""))


def _composio(slug, args, timeout=60):
    key = ENV.get("COMPOSIO_API_KEY", "")
    if not key or key.startswith("YOUR_"):
        sys.exit("COMPOSIO_API_KEY is missing, or still a placeholder, in .env.local")
    body = json.dumps({"connected_account_id": CONN, "user_id": USER, "version": "latest", "arguments": args}).encode()
    req = urllib.request.Request(f"https://backend.composio.dev/api/v3/tools/execute/{slug}", method="POST", data=body,
                                 headers={"x-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"successful": False, "error": f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}"}
    except Exception as e:
        return {"successful": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}


def _address(text):
    """The bare lower-case address in 'addr' or 'Name <addr>' form, or '' if there is none."""
    m = re.search(r"<([^<>]+)>", text)
    m = EMAIL.search(m.group(1) if m else text)
    return m.group(0).lower() if m else ""


class SuppressionError(Exception):
    """suppression.txt holds a line this script cannot read. Raised so that nothing is sent against a half-read opt-out list."""


DOMAIN = re.compile(r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[a-z]{2,}|xn--[a-z0-9-]+)")
SIMPLE = re.compile(r"(?P<addr>[a-z0-9._%+'-]+@[a-z0-9.-]+\.[a-z]{2,})|@?(?P<dom>(?:[a-z0-9-]+\.)+[a-z]{2,})")   # the common one-entry line


def _entry(token):
    """One piece of a suppression line, in lower case: ('address', a), ('domain', d), ('word', None) for a plain note word or ('bad', None)."""
    t = token.strip('"<>()[]')
    if t.startswith("mailto:"):
        t = t[7:]
    m = re.match(r"[a-z][a-z0-9+.-]*://([^/?#]*)", t)           # a web address: keep the host only
    if m:
        t = re.sub(r":\d+$", "", m.group(1).rsplit("@", 1)[-1])
    if "/" in t and "@" not in t:
        t = t.split("/", 1)[0]                                   # example.co.uk/about
    t = t.rstrip(".")                                            # a trailing dot
    if t.startswith("*@"):
        t = t[1:]
    elif t.startswith("*."):
        t = t[2:]
    if EMAIL.fullmatch(t):
        return "address", t
    host = t[1:] if t.startswith("@") else t
    if host.startswith("www."):
        host = host[4:]
    if DOMAIN.fullmatch(host):
        return "domain", host
    if re.fullmatch(r"[\w'\u2019-]+[:!?]*", t):                   # a plain word: part of a note
        return "word", None
    return "bad", None


def _parse_line(line):
    """(addresses, domains) for one comment-free, lower-case, stripped line, or None if the line is not understood."""
    m = SIMPLE.fullmatch(line)
    if m:
        if m.group("addr"):
            return [m.group("addr")], []
        d = m.group("dom")
        return [], [d[4:] if d.startswith("www.") else d]
    addrs, domains, bad = [], [], False
    for token in re.split(r"[\s,;]+", re.sub(r"(?<=\S)\s+@\s+(?=\S)", "@", line)):   # 'name @ domain' becomes 'name@domain'
        if not token:
            continue
        kind, value = _entry(token)
        if kind == "address":
            addrs.append(value)
        elif kind == "domain":
            domains.append(value)
        elif kind == "bad":
            bad = True
    return None if bad or not (addrs or domains) else (addrs, domains)


def suppressed():
    """(addresses, domains) from suppression.txt; see the docstring for what an entry can look like.
    Raises SuppressionError, naming the line numbers, if the file is not UTF-8 or any line cannot be read."""
    addrs, domains, bad = set(), set(), []
    if not os.path.exists(SUPPRESS):
        return addrs, domains
    try:
        with open(SUPPRESS, encoding="utf-8-sig") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        raise SuppressionError("run/outreach/suppression.txt is not UTF-8 text. Save it as plain UTF-8 text. Nothing is sent until it is fixed.") from None
    for number, line in enumerate(text.split("\n"), 1):
        line = line.split("#", 1)[0].strip().lower()
        if not line:
            continue
        parsed = _parse_line(line)
        if parsed is None:
            bad.append(number)
        else:
            addrs.update(parsed[0]); domains.update(parsed[1])
    if bad:
        raise SuppressionError(f"run/outreach/suppression.txt: {len(bad)} line{'' if len(bad) == 1 else 's'} not understood (line {', '.join(map(str, bad[:20]))}"
                               f"{', ...' if len(bad) > 20 else ''}). Use an address, @domain or domain on each line and put notes after a #. Nothing is sent until it is fixed.")
    return addrs, domains


def is_suppressed(to):
    """True if the address, or its domain, is on the list. Raises SuppressionError if the list cannot be read."""
    addrs, domains = suppressed()
    a = _address(to) or to.strip().lower()
    host = a.rsplit("@", 1)[-1]
    return a in addrs or any(host == d or host.endswith("." + d) for d in domains)


def already_sent():
    if not os.path.exists(LOG):
        return set()
    out = set()
    for l in open(LOG):
        try:
            r = json.loads(l)
            if r.get("ok") and r.get("kind") != "test":
                out.add(r["to"].lower())
        except Exception:
            pass
    return out


def send(to, subject, body, kind="outreach", meta=None, html=False):
    to = to.strip()
    if is_suppressed(to):
        return {"ok": False, "skipped": "suppressed", "to": to}
    _check_config()
    args = {"accountId": ACCOUNT, "fromAddress": FROM, "toAddress": to, "subject": subject, "content": body,
            "mailFormat": "html" if html else "plaintext", "region": "eu", "askReceipt": "no"}
    res = _composio("ZOHO_MAIL_MESSAGES_SEND_EMAIL", args)
    ok = bool(res.get("successful"))
    rec = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "to": to, "subject": subject, "kind": kind, "ok": ok,
           "error": None if ok else str(res.get("error"))[:300], "meta": meta or {}}
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def run_queue(path, min_gap, max_gap, limit, dry):
    queue = json.load(open(path, encoding="utf-8"))
    done, sent = already_sent(), 0
    for item in queue:
        if limit is not None and sent >= limit:
            break
        to = item["to"].strip()
        if to.lower() in done or is_suppressed(to) or item.get("hold"):
            continue
        if dry:
            print(f"DRY -> {to} | {item['subject']}")
            sent += 1
            continue
        rec = send(to, item["subject"], item["body"], kind=item.get("kind", "outreach"), meta=item.get("meta"))
        print(f"{rec['ts']} {'OK ' if rec['ok'] else 'ERR'} {to} {rec.get('error') or ''}", flush=True)
        if not rec["ok"]:
            # stop on the first hard failure so a blocked mailbox is not hammered
            print("STOPPING: send failed; investigate before continuing", flush=True)
            sys.exit(2)
        sent += 1
        done.add(to.lower())
        time.sleep(random.randint(min_gap, max_gap))
    print(f"queue finished: {sent} {'would be ' if dry else ''}sent", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send"); s.add_argument("--to", required=True); s.add_argument("--subject", required=True)
    s.add_argument("--body-file", required=True); s.add_argument("--kind", default="manual")
    q = sub.add_parser("queue"); q.add_argument("path"); q.add_argument("--min-gap", type=int, default=240)
    q.add_argument("--max-gap", type=int, default=420); q.add_argument("--limit", type=int, default=None); q.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        if a.cmd == "send":
            print(json.dumps(send(a.to, a.subject, open(a.body_file).read(), kind=a.kind)))
        else:
            if a.min_gap < 0 or a.max_gap < a.min_gap:
                ap.error("--min-gap must be 0 or more and not above --max-gap")
            if a.limit is not None and a.limit < 1:
                ap.error("--limit must be at least 1 (leave it out for no limit)")
            run_queue(a.path, a.min_gap, a.max_gap, a.limit, a.dry_run)
    except SuppressionError as e:
        sys.exit(f"STOPPED, nothing was sent: {e}")

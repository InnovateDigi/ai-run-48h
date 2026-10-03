#!/usr/bin/env python3
"""Builds the Saturday send queue (run/outreach/queue_saturday.json) and a reserve queue (queue_reserve.json).

Sources: run/prospects/westmids.csv + run/outreach/westmids_hooks.csv   (prospects in the region your dated hook lands first)
         run/prospects/agents.csv   + run/outreach/agent_hooks.csv      (specialist prospects across the country)
         run/outreach/queue_partners.json                               (optional: output of build_partner_queue.py)
Every recipient is a Ltd/LLP with a generic address published on its own website. Reply-first offer.

CSV columns used (save as CSV or CSV UTF-8; a byte-order mark is fine)
  westmids.csv:       email, email_type, company_name, town, manages_hmos, priority_rank, saturday_open, email_source_url
  agents.csv:         email, city, verification, company_name, saturday_open, email_source_url
  *_hooks.csv:        email, short_name, hook_sentence, confidence

The email wording below is generic template text written for this kit, with YOUR_ placeholders where your own offer goes.
The run's own emails and offer terms are not included. start_wave.sh refuses any email that still contains a YOUR_ or
<UPPER_CASE> token, that lacks its disclaimer text or its reply "no" line, or that has a malformed or placeholder recipient.
"""
import csv, json, html, re, os

ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())
URL = "https://YOUR_USER.github.io/YOUR_REPO/"
SIG = ("YOUR_TRADING_NAME\nyou@example.com\n"
       "YOUR_TRADING_NAME is a private business that is not affiliated with any public body.")
# --- the offer: replace all of these. In OFFER_BRANDED, {short} is the prospect's short name and {poss} its possessive form. ---
SUBJECT = "YOUR_SUBJECT_LINE"
PRODUCT = "YOUR_PRODUCT_IN_ONE_PHRASE"
WHAT_IT_DOES = "YOUR_ONE_OR_TWO_SENTENCES_ON_WHAT_IT_DOES."
EXTRA_SPECIALIST = " YOUR_EXTRA_SENTENCE_FOR_SPECIALIST_PROSPECTS."
EXTRA_OTHER = " YOUR_EXTRA_SENTENCE_FOR_OTHER_PROSPECTS."
WHY_NOW = "YOUR_DATED_REASON_THE_READER_CARES."           # the dated hook, from a primary source
WHY_FOR_THEM = "YOUR_ONE_SENTENCE_ON_WHAT_THIS_MEANS_FOR_THIS_READER."
ASK = "YOUR_ONE_LINE_ASK."                                  # what you want the reader to do next
OFFER_BRANDED = "YOUR_ONE_SENTENCE_ON_THE_OFFER_FOR_{short}."
OPT_OUT = 'If you would rather not hear from me, reply "no" and I will not write again.'   # the gate wants reply "no" in every email
# The dated hook can land on a different date in each region; staging by region follows from that.
FIRST_REGION = "West Midlands"                            # where the hook lands first: its prospects go first
EARLY_REGIONS = ("East of England", "East Midlands")      # next in line
OPEN = dict.fromkeys(["West Midlands", "East of England", "East Midlands", "South East", "Yorkshire and Humber",
                      "North West", "North East", "London", "South West"], "YOUR_DATE")
CITY_REGION = {"birmingham": "West Midlands", "coventry": "West Midlands", "stoke-on-trent": "West Midlands",
               "cambridge": "East of England", "norwich": "East of England",
               "nottingham": "East Midlands", "derby": "East Midlands", "leicester": "East Midlands", "lincoln": "East Midlands",
               "portsmouth": "South East", "southampton": "South East", "brighton": "South East", "oxford": "South East", "reading": "South East",
               "hull": "Yorkshire and Humber", "leeds": "Yorkshire and Humber", "sheffield": "Yorkshire and Humber",
               "manchester": "North West", "liverpool": "North West", "newcastle": "North East", "durham": "North East",
               "bristol": "South West", "bath": "South West", "plymouth": "South West", "exeter": "South West"}
EXCLUDE_NAME = ("Example Exempt Provider",)      # name prefixes to skip, e.g. an exempt provider that is not a fit for this email


def poss(name):
    return name + ("'" if name.endswith("s") else "'s")


def region_of(city):
    c = city.lower()
    if c.startswith("london"):
        return "London"
    for k, v in CITY_REGION.items():
        if c.startswith(k):
            return v
    return None


def clean(t):
    t = html.unescape(t or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", t).strip()


def rank_of(row):
    try:
        return int(row.get("priority_rank") or 99)
    except ValueError:
        return 99                                          # a non-numeric rank sorts last


def body(short, hook, region, specialist):
    place = "London" if region == "London" else f"the {region}"
    when = f"{WHY_NOW} In {place} the date is {OPEN[region]}."
    extra = EXTRA_SPECIALIST if specialist else EXTRA_OTHER
    offer = OFFER_BRANDED.replace("{short}", short).replace("{poss}", poss(short))
    return f"""Hi {short} team,

{hook}

{when} {WHY_FOR_THEM}

I've built {PRODUCT}. {WHAT_IT_DOES}{extra}

{ASK}

{offer}

More detail: {URL}

{OPT_OUT}

{SIG}"""


def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig", newline=""))) if os.path.exists(path) else []


def main():
    items, skipped = [], []
    # --- prospects in the first region ---
    hooks = {r["email"].strip().lower(): r for r in load(f"{ROOT}/run/outreach/westmids_hooks.csv")}
    for r in load(f"{ROOT}/run/prospects/westmids.csv"):
        e = r["email"].strip(); h = hooks.get(e.lower())
        if not h: skipped.append((e, "no hook")); continue
        if r["email_type"] != "generic": skipped.append((e, "not generic")); continue
        short, hook = clean(h["short_name"]), clean(h["hook_sentence"])
        specialist = (r.get("manages_hmos") or "").lower().startswith(("yes", "stu"))
        items.append({"to": e, "subject": f"{SUBJECT} for {short}", "body": body(short, hook, FIRST_REGION, specialist),
                      "kind": "agent", "meta": {"list": "westmids", "name": r["company_name"], "region": FIRST_REGION, "town": r["town"],
                                                 "rank": rank_of(r), "sat": (r.get("saturday_open") or "").lower()[:3],
                                                 "hook_conf": h["confidence"], "email_source_url": r["email_source_url"]}})
    # --- specialist prospects across the country ---
    hooks = {r["email"].strip().lower(): r for r in load(f"{ROOT}/run/outreach/agent_hooks.csv")}
    for r in load(f"{ROOT}/run/prospects/agents.csv"):
        e = r["email"].strip(); h = hooks.get(e.lower()); v = r.get("verification", "")
        region = region_of(r["city"])
        if not h: skipped.append((e, "no hook")); continue
        if "Companies House lookup only" in v or "does not show status Active" in v: skipped.append((e, "legal form not evidenced on own site")); continue
        if any(r["company_name"].startswith(x) for x in EXCLUDE_NAME): skipped.append((e, "excluded: not a fit")); continue
        if not region: skipped.append((e, f"no region for {r['city']}")); continue
        short, hook = clean(h["short_name"]), clean(h["hook_sentence"])
        items.append({"to": e, "subject": f"{SUBJECT} for {short}", "body": body(short, hook, region, True),
                      "kind": "agent", "meta": {"list": "agents", "name": r["company_name"], "region": region, "town": r["city"], "rank": 50,
                                                 "sat": (r.get("saturday_open") or "").lower()[:3], "hook_conf": h["confidence"],
                                                 "email_source_url": r["email_source_url"]}})
    partners_path = f"{ROOT}/run/outreach/queue_partners.json"
    partners = json.load(open(partners_path)) if os.path.exists(partners_path) else []

    def P(prefix):
        m = [p for p in partners if p["meta"]["name"].startswith(prefix)]
        return m[:1]

    wm = sorted([i for i in items if i["meta"]["region"] == FIRST_REGION], key=lambda i: (i["meta"]["sat"] != "yes", i["meta"]["rank"]))
    early = sorted([i for i in items if i["meta"]["region"] in EARLY_REGIONS], key=lambda i: (i["meta"]["sat"] != "yes", i["meta"]["region"]))
    rest = [i for i in items if i["meta"]["region"] != FIRST_REGION and i["meta"]["region"] not in EARLY_REGIONS]
    rest.sort(key=lambda i: (i["meta"]["sat"] != "yes", list(OPEN).index(i["meta"]["region"])))
    top_partners = P("Example Association") + P("Example Accountants") + P("Example Electrical Testing") + P("Example Publisher")
    other_partners = [p for p in partners if p not in top_partners]
    # Saturday: wave 1 = 14 best first-region prospects + 4 best partners; then the remaining first-region prospects, partners, then early-region prospects
    saturday = wm[:14] + top_partners + wm[14:34] + other_partners[:12] + early[:10]
    seen, sat_final = set(), []
    for i in saturday:
        k = i["to"].lower()
        if k not in seen: seen.add(k); sat_final.append(i)
    reserve = [i for i in (wm[34:] + other_partners[12:] + early[10:] + rest) if i["to"].lower() not in seen]
    os.makedirs(f"{ROOT}/run/outreach", exist_ok=True)
    json.dump(sat_final, open(f"{ROOT}/run/outreach/queue_saturday.json", "w"), indent=1, ensure_ascii=False)
    json.dump(reserve, open(f"{ROOT}/run/outreach/queue_reserve.json", "w"), indent=1, ensure_ascii=False)
    print(f"saturday queue: {len(sat_final)} (first region {sum(1 for i in sat_final if i['meta'].get('region')==FIRST_REGION and i['kind']=='agent')}, "
          f"partners {sum(1 for i in sat_final if i['kind']=='partner')}, other regions {sum(1 for i in sat_final if i['kind']=='agent' and i['meta'].get('region')!=FIRST_REGION)}) | reserve: {len(reserve)}")
    if sat_final:
        wc = sorted(len(i["body"].split()) for i in sat_final)
        print(f"word counts min/median/max: {wc[0]}/{wc[len(wc)//2]}/{wc[-1]} | skipped: {len(skipped)}")
    for e, why in skipped: print("  skipped", e, "->", why)
    dup = len(sat_final) - len({i['to'].lower() for i in sat_final})
    print("duplicates in saturday queue:", dup)


if __name__ == "__main__":
    main()

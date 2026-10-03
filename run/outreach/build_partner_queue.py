#!/usr/bin/env python3
"""Builds run/outreach/queue_partners.json from hand-written, per-prospect first lines.

Every recipient is tier-1/2 in run/prospects/partners.csv with outreach_gate B2B-OK (Ltd/LLP evidenced) and a generic
address published on its own website. Hook lines only state what your research recorded on the prospect's own pages;
they never claim you read, watched or used something.

partners.csv columns used: name, outreach_gate, email_type, verify_status, contact_email, email_source_url, priority_rank
(save it as CSV or CSV UTF-8; a byte-order mark is fine)

The email wording below is generic template text written for this kit, with YOUR_ placeholders where your own offer goes.
The run's own emails and offer terms are not included. start_wave.sh refuses any email that still contains a YOUR_ or
<UPPER_CASE> token, that lacks its disclaimer text or its reply "no" line, or that has a malformed or placeholder recipient."""
import csv, json, os, sys

ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())
URL = "https://YOUR_USER.github.io/YOUR_REPO/"
SIG = ("YOUR_TRADING_NAME\nyou@example.com\n"
       "YOUR_TRADING_NAME is a private business that is not affiliated with any public body.")
# --- the offer: replace all of these. In an OFFER_ line, {short} is the prospect's short name and {poss} its possessive form. ---
SUBJECT = "YOUR_SUBJECT_LINE"
PRODUCT = "YOUR_PRODUCT_IN_ONE_PHRASE"
WHAT_IT_DOES = "YOUR_ONE_OR_TWO_SENTENCES_ON_WHAT_IT_DOES."
WHY_NOW = "YOUR_DATED_REASON_THE_READER_CARES."        # the dated hook, from a primary source
OFFER_ASSOCIATION = "YOUR_OFFER_FOR_{short}_AND_ITS_MEMBERS."
OFFER_PUBLISHER = "YOUR_OFFER_FOR_{short}_AND_ITS_AUDIENCE."
OFFER_FIRM = "YOUR_OFFER_FOR_{short}_AND_ITS_CLIENTS."
ASK = "YOUR_ONE_LINE_ASK."                              # what you want the reader to do next
OPT_OUT = 'If you would rather not hear from me, reply "no" and I will not write again.'   # the gate wants reply "no" in every email
# Optional: a different dated line per region. Keys must match the region given to a firm() entry in P below.
DATE_BY_REGION = {"Region A": "YOUR_DATE_A", "Region B": "YOUR_DATE_B"}


def poss(name):
    return name + ("'" if name.endswith("s") else "'s")


def fill(text, p):
    return text.replace("{short}", p["short"]).replace("{poss}", poss(p["short"]))


def assoc(p):
    return (f"{SUBJECT} for {p['short']} members",
f"""Hi {p['short']} team,

{p['hook']}

I've built {PRODUCT}. {WHAT_IT_DOES}

{fill(OFFER_ASSOCIATION, p)}

{ASK}

More detail: {URL}

{OPT_OUT}

{SIG}""")


def publisher(p):
    return (f"{SUBJECT} for your {p['audience']}",
f"""Hi {p['short']} team,

{p['hook']}

{WHY_NOW} I've built {PRODUCT}. {WHAT_IT_DOES}

{fill(OFFER_PUBLISHER, p)}

{ASK}

More detail: {URL}

{OPT_OUT}

{SIG}""")


def firm(p):
    region = p.get("region")
    when = f"{WHY_NOW} In {region} the date is {DATE_BY_REGION[region]}." if region else WHY_NOW
    return (f"{SUBJECT} for {poss(p['short'])} clients",
f"""Hi {p['short']} team,

{p['hook']}

{when}

I've built {PRODUCT}. {WHAT_IT_DOES}

{fill(OFFER_FIRM, p)}

{ASK}

More detail: {URL}

{OPT_OUT}

{SIG}""")


P = [
 # The real run had 20 entries. Each hook was a single true, dated fact from the prospect's own website (held in the
 # research file with a URL and a verbatim quote). These invented entries show the three kinds of entry only.
 # --- associations ---
 dict(key="Example Association", short="Example Association", kind=assoc,
      hook="Your <DATE> post about <TOPIC> covers the ground this email is about."),
 dict(key="Example Landlords Group", short="Example Landlords", kind=assoc,
      hook="<TOPIC> came up on your <PAGE_NAME> page, which is why I am writing."),
 # --- publishers, communities, educators ---
 dict(key="Example Publisher", short="Example Publisher", kind=publisher, audience="readers",
      hook="Your <SECTION_NAME> section lists tools for <AUDIENCE>, so this may fit."),
 dict(key="Example Property Course", short="Example Course", kind=publisher, audience="students",
      hook="Your <DATE> article about <TOPIC> made me think of your students."),
 # --- professional firms with clients who are affected ---
 dict(key="Example Accountants", short="Example Accountants", kind=firm, region="Region A",
      hook="Your <PAGE_NAME> page says you act for <TYPE_OF_CLIENT>, and <CHANGE> will touch them."),
 dict(key="Example Electrical Testing", short="Example Electrical", kind=firm, region="Region A",
      hook="<CERTIFICATE_TYPE> certificates come up in <CHANGE>, and you issue them."),
 dict(key="Example Mortgage Broker", short="Example Mortgages", kind=firm, region="Region B",
      hook="Your <GUIDE_NAME> guide, last updated <DATE>, covers <TOPIC>."),
]

path = f"{ROOT}/run/prospects/partners.csv"
if not os.path.exists(path):
    sys.exit(f"missing {path}: see the docstring above for the columns it needs")
rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
need = {"name", "outreach_gate", "email_type", "verify_status", "contact_email", "email_source_url", "priority_rank"}
if rows and need - set(rows[0]):
    sys.exit(f"partners.csv is missing columns: {sorted(need - set(rows[0]))}")
queue, problems = [], []
for p in P:
    match = [r for r in rows if r["name"].startswith(p["key"])]
    if len(match) != 1:
        problems.append(f"{p['key']}: {len(match)} matches"); continue
    r = match[0]
    if not r["outreach_gate"].startswith("B2B-OK") or r["email_type"] != "generic" or not r["verify_status"].startswith("PASS"):
        problems.append(f"{p['key']}: gate={r['outreach_gate'][:20]} type={r['email_type']} verify={r['verify_status'][:20]}"); continue
    subject, body = p["kind"](p)
    queue.append({"to": r["contact_email"].strip(), "subject": subject, "body": body, "kind": "partner",
                  "meta": {"list": "partners", "name": r["name"], "template": p["kind"].__name__, "region": p.get("region"),
                           "email_source_url": r["email_source_url"], "rank": r["priority_rank"]}})
os.makedirs(f"{ROOT}/run/outreach", exist_ok=True)
json.dump(queue, open(f"{ROOT}/run/outreach/queue_partners.json", "w"), indent=1, ensure_ascii=False)
print(f"queued {len(queue)} partner emails; problems: {problems or 'none'}")
for q in queue:
    words = len(q["body"].split())
    print(f"  {q['meta']['rank']:>2} {q['to']:44s} {q['meta']['template']:9s} {words} words | {q['subject']}")

#!/usr/bin/env bash
# Send gate + background sender for the 48h revenue run.
# usage: run/start_wave.sh <limit> <logname> [--send|--dry-run] [queue.json]
# SAFE BY DEFAULT: nothing is sent unless the third argument is exactly --send.
# (The first version sent unless it saw --dry-run. A mistyped flag during a dry run sent one real email.)
# Needs bash, curl, python3 and pgrep. Written on Linux; where setsid is missing (macOS) it falls back to nohup.
set -u
ROOT=${PROJECT_ROOT:-$PWD}
cd "$ROOT" || { echo "cannot enter PROJECT_ROOT: $ROOT"; exit 1; }
ROOT=$PWD; export PROJECT_ROOT="$ROOT"      # absolute, so that mailer.py reads the same folder
LIMIT=${1:?limit}; NAME=${2:?logname}; MODE=${3:---dry-run}; QUEUE=${4:-run/outreach/queue_saturday.json}; export QUEUE
case "$LIMIT" in ''|*[!0-9]*) echo "limit must be a whole number above 0 (got '$LIMIT')"; exit 1;; esac
LIMIT=$((10#$LIMIT)); [ "$LIMIT" -ge 1 ] || { echo "limit must be a whole number above 0"; exit 1; }
case "$NAME" in ''|*/*) echo "logname must be a plain name, not a path (got '$NAME')"; exit 1;; esac
LOG=run/logs/$NAME.log
if [ "$MODE" != "--send" ] && [ "$MODE" != "--dry-run" ]; then echo "note: '$MODE' is not --send, so this is a dry run"; fi
[ -f "$QUEUE" ] || { echo "queue file not found: $QUEUE"; exit 1; }
[ -f .env.local ] || { echo ".env.local not found in $ROOT (copy .env.local.example)"; exit 1; }
for f in run/download_token.txt run/stripe_standard_link.txt run/stripe_whitelabel_link.txt; do
  [ -s "$f" ] || { echo "missing or empty: $f (see the README, set-up step 2)"; exit 1; }
done
BASE=https://YOUR_USER.github.io/YOUR_REPO; DL=$(cat run/download_token.txt)
case "$BASE" in *YOUR_*) echo "set BASE at the top of start_wave.sh: it still holds a YOUR_ placeholder"; exit 1;; esac
mkdir -p run/logs
# One gate at a time. Two gates started together could each find no sender running and each start one, and every address would be mailed twice.
# An exclusive flock on run/logs/.gate.lock is held until this script exits. The sender is started without the descriptor, so it does not keep the lock.
exec 9> run/logs/.gate.lock || { echo "cannot open run/logs/.gate.lock"; exit 1; }
python3 -c 'import fcntl, sys
try: fcntl.flock(9, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError: sys.exit(3)
except OSError: sys.exit(4)'
case $? in
  0) ;;
  3) echo "GATE FAILED: another gate is running (run/logs/.gate.lock is held). Nothing sent."; exit 1;;
  *) echo "GATE FAILED: could not take the lock run/logs/.gate.lock. Nothing sent."; exit 1;;
esac
DISCLAIMER_TEXT="is not affiliated with"; export DISCLAIMER_TEXT   # text every email must contain (part of your own disclaimer line)
fail=0; chk() { if [ "$2" = "200" ]; then echo "  ok   $1"; else echo "  FAIL $1 (HTTP $2)"; fail=1; fi; }
echo "== send gate $(TZ=Europe/London date '+%a %H:%M UK') =="
chk "landing page" "$(curl -s -m 25 -o /dev/null -w '%{http_code}' $BASE/)"
chk "download page" "$(curl -s -m 25 -o /dev/null -w '%{http_code}' $BASE/d/$DL/)"
# keep this list the same as DELIVERABLES in deploy_site.py
for f in Compliance-Tracker.xlsx Quick-Start-Guide.pdf Landlord-Guide.pdf Test-Log.pdf; do chk "file $f" "$(curl -s -m 40 -o /dev/null -w '%{http_code}' $BASE/d/$DL/$f)"; done
chk "thanks page" "$(curl -s -m 25 -o /dev/null -w '%{http_code}' $BASE/thanks.html)"
# These are your own payment links. Some checkouts refuse curl's default User-Agent, so the check sends a browser-style one.
# It only loads your own page to see that it answers. It is not a way round anyone's bot protection.
for l in run/stripe_standard_link.txt run/stripe_whitelabel_link.txt; do chk "stripe $(basename $l .txt)" "$(curl -s -m 25 -L -o /dev/null -w '%{http_code}' -A 'Mozilla/5.0' "$(cat $l)")"; done
set -a; . ./.env.local; set +a
echo "  stripe descriptor: $(curl -s -m 25 https://api.stripe.com/v1/account -u "$STRIPE_SECRET_KEY:" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['settings']['payments']['statement_descriptor'],'| prefix:',d['settings']['card_payments'].get('statement_descriptor_prefix'),'| name:',d['business_profile'].get('name'),'| charges_enabled:',d['charges_enabled'])" 2>/dev/null || echo 'could not read the account settings')"
python3 - <<'PY' || fail=1
import json, os, re, sys
sys.path.insert(0, "run")
try:
    q = json.load(open(os.environ["QUEUE"], encoding="utf-8"))
    assert isinstance(q, list) and all(isinstance(i, dict) and {"to", "subject", "body"} <= set(i) for i in q)
except Exception as e:
    print(f"  FAIL queue unreadable ({type(e).__name__}): it must be a JSON list of objects with to, subject and body"); sys.exit(1)
try:
    from mailer import is_suppressed          # the same rules the sender applies: addresses and whole domains
except BaseException as e:
    print(f"  FAIL could not load run/mailer.py: {str(e)[:120]}"); sys.exit(1)
try:
    is_suppressed("")                         # reads the whole suppression file: a line the sender cannot read stops the gate here
except Exception as e:
    print(f"  FAIL {type(e).__name__}: {str(e)[:300]}"); sys.exit(1)
need = os.environ["DISCLAIMER_TEXT"]
leftover = re.compile(r"\{|YOUR_|<[A-Z_]+>")                      # a template brace, a YOUR_ placeholder or an <UPPER_CASE> token
address = re.compile(r"^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$")
placeholder_host = re.compile(r"@(example\.(com|net|org)|[^@]*\.(test|invalid|example|localhost))$", re.I)
reasons, bad = {}, 0
for i in q:
    why = []
    if need not in i["body"]: why.append("disclaimer text missing")
    if 'reply "no"' not in i["body"].lower(): why.append('opt-out line (reply "no") missing')
    if leftover.search(i["body"]) or leftover.search(i["subject"]): why.append("placeholder left in subject or body")
    to = i["to"].strip()
    if not address.match(to) or placeholder_host.search(to) or leftover.search(to): why.append("recipient is malformed or a placeholder")
    for w in why: reasons[w] = reasons.get(w, 0) + 1
    bad += bool(why)
print(f"  queue: {len(q)} emails, {bad} failing content checks, {sum(1 for i in q if is_suppressed(i['to']))} suppressed (will be skipped)")
for w, n in reasons.items(): print(f"    {n} x {w}")
sys.exit(1 if bad or not q else 0)
PY
if ! command -v pgrep > /dev/null 2>&1; then echo "  FAIL pgrep not found, so a running sender cannot be detected"; fail=1
elif pgrep -f "mailer.py queue" > /dev/null 2>&1; then echo "  FAIL a sender is already running"; fail=1; fi
[ $fail -ne 0 ] && { echo "GATE FAILED: nothing sent"; exit 1; }
if [ "$MODE" != "--send" ]; then
  echo "DRY RUN (pass --send as the third argument to send):"
  out=$(python3 run/mailer.py queue "$QUEUE" --limit "$LIMIT" --dry-run 2>&1); rc=$?
  echo "$out" | tail -3
  exit $rc
fi
if command -v setsid > /dev/null 2>&1; then START="setsid nohup"; else START="nohup"; fi
$START python3 run/mailer.py queue "$QUEUE" --limit "$LIMIT" --min-gap 200 --max-gap 330 > "$LOG" 2>&1 < /dev/null 9>&- &
sleep 2
PIDS=$(pgrep -f "mailer.py queue" | tr '\n' ' ')
if [ -z "$PIDS" ]; then
  if grep -q "queue finished" "$LOG" 2> /dev/null; then echo "GATE PASSED: the sender has already finished (nothing left to send), log $LOG"; tail -2 "$LOG"; exit 0; fi
  echo "GATE PASSED, BUT THE SENDER IS NOT RUNNING. Read $LOG:"; tail -5 "$LOG"; exit 1
fi
echo "GATE PASSED: sender started (limit $LIMIT), log $LOG, pid $PIDS"

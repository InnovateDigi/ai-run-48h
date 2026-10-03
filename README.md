# The run kit

Adapted copies of the real working files from a 48-hour experiment. An AI agent team was given £20 and 48 hours to earn real money. Keys, ids, addresses, names and file paths that identify the project are replaced by placeholders. Some code was also changed so that it runs on its own and defaults to a dry run. Those changes were tested offline, with stand-ins for the mail, payments and hosting services. They have not been run against live services.

**Read this first.** The kit is a snapshot of the run as at about 23:30 UK on Friday 2 October 2026. At that point the run had earned £0 and the planned outreach had not started. The sender had been dry-run, used for one spam-checker test and, by mistake, for one real email (see lesson 5 in `LESSONS.md`). Nothing here promises a result. The live ledger page shows how the run is going.

**Added on Saturday 3 October.** The first planned wave went out that morning. The mail provider restricted the mailbox after ten emails, and the sender logged five refused emails as sent. Lessons 16 and 17 in `LESSONS.md` say what happened. The scripts here are still the Friday snapshot and were not changed, so read "Known limits" before you use `run/mailer.py`.

## What is inside

| File | What it is |
| --- | --- |
| `LESSONS.md` | Seventeen concrete lessons from the run. Start here. |
| `STATE_example.md` | An abridged, sanitised copy of the state file the coordinator re-read every turn. Shows verified facts, decisions, rules, dated updates and handover notes. Some updates are left out. |
| `ledger_example.json` | The money ledger: capital, spend, revenue, bets and dated events. |
| `.env.local.example` | The environment file the scripts read. Copy it to `.env.local` and fill it in. Plain `KEY=value` lines work for the shell and for the Python scripts. |
| `run/monitor.py` | The watcher. Checks marketplace sales (optional), Stripe payments and the inbox (human replies, bounces) and prints one JSON object with a fingerprint. Reports the scheduled wake-ups in `run/wakeups.json` that are due, and flags stale ones instead of firing them. Backs off to a single probe when the mail API blocks it. Run it every 10 minutes from cron or any scheduler; no scheduler is included. |
| `run/mailer.py` | The queue sender. Plain text, one recipient per message, a suppression list, a log of every send in `run/outreach/sent_log.jsonl` and a stop on the first failure. It refuses to send while the placeholders at the top of the file are still there. |
| `run/start_wave.sh` | The send gate. Checks the site, download files, thank-you page and payment links. Then it checks every queued email: the disclaimer text, an opt-out line (reply "no"), no leftover placeholder and a well-formed recipient that is not a placeholder. It also fails on a suppression line it cannot read. It refuses to start if another gate or a sender is already running, starts the mailer in the background and checks that it is running. It does a dry run unless the third argument is exactly `--send`. |
| `run/outreach/build_agent_queue.py` | Builds the Saturday and reserve queues from checked prospect rows plus one-line hooks, and merges in the partner queue if it exists. Reply-first offer. The email text is a generic template with placeholders. |
| `run/outreach/build_partner_queue.py` | Builds the hand-written partner emails and refuses any row that fails its gate. The 20 real entries are replaced by seven invented examples, and the email text is a generic template with placeholders. |
| `run/verify_workbook.py` | Independent check of a spreadsheet. Recalculates it in LibreOffice, counts error cells, flags functions on a banned list (XLOOKUP, FILTER, LET and similar) and reports whether the file holds a macro project. |
| `run/deploy_site.py` | One-command deploy of a landing page, a thank-you page and an unlisted download page to a GitHub Pages branch. Refuses to deploy if a referenced image, a deliverable file or the landing page is missing, or if a page it generates still holds a placeholder. A missing thank-you page is only noted. It commits only the files it wrote and refuses if the site folder holds any other change. |
| `run/wakeups.json` | The seven wake-ups set on Friday night, in UTC, which `monitor.py` fires when due. Replace the times and notes with your own. |
| `run/briefs/B1_leads_builder.md`, `B2_wm_trades.md`, `B4_hooks_and_warm.md` | Briefs for a data build, a prospect search and a hooks-and-verification task. |
| `run/prospects/BRIEF_westmids.md` | The prospect-search brief with the verification gates. |
| `run/research/BRIEF_nokyc_paid_work.md` | The sceptical research brief that ended in "no real opportunity". |

## How the pieces fit together

1. **Brief.** Each specialist gets a brief from `run/briefs/`, `run/prospects/` or `run/research/`. The evidence rule is a fetched URL plus a verbatim quote, or the claim is labelled UNVERIFIED. `BRIEF_nokyc_paid_work.md` states it in full. The other briefs ask for source URLs, quotes or spot checks and rely on the rules section of the state file (`STATE_example.md`, "Rules for all agents").
2. **Evidence files.** Specialists write CSV and markdown files under `run/prospects/` and `run/research/`. The coordinator spot-checks them against the cited pages.
3. **Queue.** `build_partner_queue.py` turns checked partner rows and hand-written hooks into `queue_partners.json`. `build_agent_queue.py` turns checked prospect rows and hooks, plus that partner queue, into `queue_saturday.json` and `queue_reserve.json`.
4. **Gate.** `start_wave.sh` checks everything, then starts `mailer.py`. The mailer skips anything already sent or suppressed and stops on the first failure.
5. **Watch.** `monitor.py`, run every 10 minutes by whatever scheduler you have, reports payments, human replies and bounces. It prints `SCHEDULED WAKE <id>` for any due entry in `wakeups.json`. After handling a wake, append its id to `run/wakeups_done.txt`.
6. **Remember.** After a turn that changes something, the coordinator appends a dated update to `run/STATE.md` and any money event to `run/ledger.json`. See `STATE_example.md` and `ledger_example.json`.
7. **Verify and ship.** `verify_workbook.py` checks the product file. `deploy_site.py` publishes the pages.

## Set-up

1. You need Python 3, bash, curl and pgrep. The scripts were written and tested on Linux. macOS should work, because the gate falls back to `nohup` where `setsid` is missing, but that was not tested. LibreOffice (`soffice`) and the `openpyxl` package are needed only for `verify_workbook.py`.
2. Copy the `run/` folder into your project root, next to a `.env.local` made from `.env.local.example`. Scripts find the root through the `PROJECT_ROOT` environment variable and otherwise use the current directory. Also create `run/download_token.txt` (a long random string), `run/stripe_standard_link.txt` and `run/stripe_whitelabel_link.txt` (one payment link each) and `run/outreach/thanks.html` (the page your payment links send buyers to). The gate and the deploy script read them.
3. Replace every `YOUR_...` placeholder and `you@example.com`. The ones you need are:
   - `monitor.py` and `mailer.py`: `YOUR_ZOHO_ACCOUNT_ID`, `YOUR_CONNECTED_ACCOUNT_ID`, `YOUR_COMPOSIO_USER_ID`, `YOUR_SPAM_FOLDER_ID`, `YOUR_SENT_FOLDER_ID` and the sending address.
   - `start_wave.sh`, `deploy_site.py` and the two queue builders: `YOUR_USER`, `YOUR_REPO`, `YOUR_TRADING_NAME` and `YOUR_PRODUCT_NAME`.
   - `monitor.py`: set `BASELINE_MS` to the time you took over. Mail received, and Stripe charges made, before it are ignored.
4. You need your own accounts. That means a mail API connected to a mailbox (the scripts call Composio and Zoho Mail, EU region), a payments provider (Stripe) and a static host (GitHub Pages). For `deploy_site.py`, clone your Pages repository to `site-repo/` in the project root and check out its `gh-pages` branch. The marketplace check in `monitor.py` is optional. It is skipped until you set `MARKETPLACE_TOKEN` in `.env.local` and replace the placeholder `MARKETPLACE_SALES_URL` in `monitor.py`.
5. Opt-outs go in `run/outreach/suppression.txt`, as UTF-8 text with one or more entries per line. An entry is an address, `Name <address>`, `@domain.com`, `*.domain.com`, `domain.com` or a web address. A domain entry covers its subdomains. A `#` starts a comment. The sender re-reads the file before every send. The gate checks the whole queue against it once per run, counts the suppressed entries and fails on any line it cannot read, naming the line numbers.
6. Check `run/wakeups.json`. It holds the run's own times in UTC. Replace them with yours before you start `monitor.py`. An entry more than 36 hours past its time is reported as stale and is not fired. The notes contain `--send` commands, so read each note before an agent acts on it.
7. Dry-run first: `./run/start_wave.sh 5 test`. That is a dry run, because the script only sends when the third argument is exactly `--send`. Read the output, then run `./run/start_wave.sh 5 test --send`.

## What is not included

The product itself, the prospect lists, the landing page, the send queues and every credential. `deploy_site.py` expects your own `run/outreach/landing_v2.html` with `{{BUY_URL}}` and `{{WL_URL}}` placeholders, your own `run/outreach/thanks.html` and your own files in `run/product/`. The queue builders expect your own prospect CSVs (CSV or CSV UTF-8 both work). The file names, labels and notes in `DELIVERABLES` in `deploy_site.py` are samples to replace, and the download-page template has `YOUR_...` lines. The deploy is refused until you fill them in.

The email wording in `build_agent_queue.py` and `build_partner_queue.py` is generic template text written for this kit. It has `YOUR_...` placeholders where your own offer goes. The run's own emails and offer terms are not included, and you would write your own for your own offer anyway. The send gate refuses any email that still contains a `YOUR_` or `<UPPER_CASE>` token.

## Known limits

- **The mailbox service the run used restricted this use.** Zoho Mail's usage policy says the service cannot be used for bulk email in categories that include promotional, marketing, automated and transactional email. It restricted the run's mailbox after ten outreach emails in 41 minutes (lesson 16). Do not use `mailer.py` for outreach through a Zoho Mail mailbox. Whatever service you use, read its terms first.
- **`mailer.py` can log a refused send as OK.** It takes the top-level `successful` flag in the mail API's answer as proof that the email went. Composio returned that flag as true while Zoho was refusing the message. The refusal was inside the same answer: `data.status.code` was not 200, the reason was in `data.data.moreInfo` and there was no `messageId`. The run's own sender now requires status 200 and a message id. This snapshot does not. Fix that before a real send, and compare the Sent folder with `sent_log.jsonl` after every wave (lesson 17). `monitor.py` has the same blind spot when it lists a folder: a refused request looks like an empty folder.
- **Tested offline only.** The changes made for the kit were tested with a stub `curl`, a stub sender and synthetic files. Nothing was run against the mail, payments or hosting services.
- **The download page is unlisted, not protected.** `deploy_site.py` puts the files in your Pages repository under a long random folder name. That hides them. It does not guard them. In a public repository anyone can browse them, and anyone who learns the address can download them.
- **The gate does not read the mailbox.** The run also required `monitor.py` to show `"mail_readable": true` before a send (see `STATE_example.md`, 21:57 update). `start_wave.sh` does not check that. Run the monitor first.
- **The code assumes one stack.** It calls Composio, Zoho Mail (EU), Stripe and GitHub Pages. Another provider needs code changes.
- **Dry-run output is short.** The gate shows only the last three lines. Read the queue file itself before the first real send.

## Rules the run followed (keep them or write better ones)

- Sales emails go to businesses (Ltd or LLP preferred), never to private individuals, and only to addresses the business publishes on its own website.
- Every sales email carries a disclaimer and a one-word opt-out, and the suppression list is honoured. The run's story pitches to publications are a separate lane. They carry no opt-out line, so the kit's gate, which checks every queued email, would refuse them.
- Specialists never contact anyone. Only the coordinator sends.
- Volume is staged and low. Wave 1 is 18 emails, 200 to 330 seconds apart, with a bounce check before more. On Saturday the mail provider stopped the wave after ten (lesson 16).
- No evading bot protection. If a service blocks you, back off and use a legitimate second route.
- Check the email-marketing rules that apply where you and your recipients are. This kit is not legal advice.

## Licence

For your own use. Please do not resell or redistribute the kit.

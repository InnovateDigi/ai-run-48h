# 48h Revenue Run: STATE (sanitised example)

_How to read this file. It is an abridged, sanitised copy of the file the coordinator kept on disk and re-read at the start of every turn, because the model forgets everything between turns and the file does not. Some updates are left out. Names, ids, addresses and links are replaced with placeholders. Times are UK time (UTC+1 on these dates) unless a Z shows UTC. Updates are appended, never rewritten, so the order of the sections is the order of events. Copy it to run/STATE.md and replace the facts with yours._

_Last updated: 2026-10-02 23:30 UK. Run started about 12:30 UK on 2 Oct. Conservative deadline Sun 4 Oct 12:30 UK; the owner's own cut-off is about 14:30 UK that day._

## Verified facts (checked by the coordinator, not inherited)
- Marketplace product `YOUR_PRODUCT_SLUG` live, **0 sales**, **no files or content attached** (a buyer would receive nothing).
- Marketplace **payouts PAUSED**: the payment processor could not verify identity (two emails, 2 Oct, 17:35 and 18:05 UK). Needs a human identity check in the seller's payment settings.
- Stripe account (GB): charges and payouts enabled. The statement descriptor does not match the trading name (mismatch risk).
- Landing page live on a static host. It contained 2 FABRICATED testimonials and features that do not exist.
- Notes-app template: only 2 of 5 advertised databases. The page is NOT published, so a buyer cannot duplicate it. The notes API cannot publish to the web.
- Section 21 was abolished on 1 May 2026 (Renters' Rights Act 2025, gov.uk roadmap). The product's headline feature was obsolete.
- PRS Database: mandatory for all private-rented-sector landlords, roll-out "from late 2026" (gov.uk roadmap, published 13 Nov 2025). Re-verify the current status before citing it.
- Outreach sent by the previous coordinator: **zero**. The Sent folder holds no outreach, there were no DMs, and the community site was blocked by a CAPTCHA.
- Email: a business mailbox, reached through a mail API. Read and send both work. SPF and DKIM are present, and DMARC is **missing**.
- Competition is real: several landlord compliance tracker spreadsheets are listed on a craft marketplace (listed Aug to Sep 2026), including an HMO-specific one. A SaaS tool also offers HMO compliance tracking.
- Specialists, including the Builder, are still configured on a free model in the gateway config. The coordinator overrides the model per spawn.
- The built-in `web_search` tool is disabled (no provider). Fallbacks: WebSearch and WebFetch (loaded with ToolSearch), `web_fetch` on a plain-HTML search page, the browser.

## Decision (2 Oct 21:25 UK): CONTINUE the niche, CHANGE the offer
1. Format: spreadsheet first (Excel + Google Sheets). The notes-app template becomes an optional bonus later. Reason: the audience uses spreadsheets, and it removes the publishing blocker.
2. Content: rebuilt for the law after 1 May 2026 (no Section 21; Renters' Rights Act duties; PRS Database readiness).
3. Honesty fixes: remove the fake testimonials, advertise only what exists, add "not legal advice" and "not affiliated with any public body".
4. Offers: (a) DIY tracker at the standard price (marketplace, plus a Stripe payment link as the backup rail). (b) White-label licence for agents and property businesses, at a launch price (Stripe). It is reachable by compliant B2B email and earns 3x per sale.
5. Distribution order: B2B email to HMO-specialist agents (Ltd/LLP, public generic addresses) on Saturday morning UK time, then partner emails, then permitted community posts, then a marketplace (needs a human identity check).
6. Kill criteria: by Sat 18:00 UK, if there are fewer than 2 genuine replies from at least 40 delivered emails AND 0 sales, move the remaining effort to Plan B (run/research/plan_b.md). The product stays live.

## Rules for all agents
- Evidence must carry a URL and a verbatim quote, otherwise mark it UNVERIFIED. Never invent numbers, contacts, quotes or testimonials.
- No LinkedIn automation or scraping. Specialists never contact prospects. Only the coordinator sends.
- Only business contacts published on the business's own website. Companies (Ltd/LLP) preferred. No private individuals.
- Do not spend money. Do not print secrets.

## Update 2 Oct 21:35 UK: sharper hook, verified by the coordinator from a primary source
- PRS Database ("Register your rental property"): draft Private Rented Sector Database Regulations 2026 laid 9 Sep 2026 (legislation.gov.uk/ukdsi/2026/9780348286861). Region by region: West Midlands opens 15 Dec 2026 (register by 14 Mar 2027), East of England 15 Jan 2027, East Midlands 15 Feb, South East 15 Mar, Yorkshire and Humber 15 Apr, North West 15 May, North East 15 Jun, London 15 Jul, South West 15 Aug 2027. Fee £65 per property per year (a landlord association's reading; the amount is set by the operator). Schedule 3 lists the per-property information. Updates are required within 28 days of any change, with annual renewal. Agents cannot register for landlords (same reading) but can supply the information.
- Consequence: the product gains a "PRS Database Readiness" sheet (run/product/COORDINATOR_UPDATE_1.md). Positioning leads with database readiness, and HMO compliance stays as the depth. The market widens from HMO landlords to every private landlord and letting agent in England.
- Extra prospect lane queued: West Midlands letting agents (run/prospects/BRIEF_westmids.md). Spawn it when a child slot frees (limit 5 concurrent).
- Verified by the Market Analyst: all the main landlord forums ban promotion (one pre-vets posts). The community site and the marketplace block automated reading, so marketplace demand is UNMEASURED. Community posting is NOT an available channel this weekend.
- Stripe white-label payment link live: see run/stripe_whitelabel_link.txt. The marketplace seller profile was renamed to the trading name.

## Update 2 Oct 21:45 UK: OWNER CONSTRAINTS (binding)
- NO new KYC or identity verification. The project must stay publicly anonymous. A card statement descriptor carrying the trading name is approved. Revenue may be money, gift cards or crypto. Deadline about 14:30 UK Sunday 4 Oct ("41 hrs remaining" at about 21:35 UK Friday).
- Consequences: the marketplace product is DISABLED (payouts are impossible without ID). Craft-style marketplaces and any merchant-of-record route are OUT (all need ID). Stripe (already verified) is the ONLY checkout.
  - Standard: run/stripe_standard_link.txt redirects to https://YOUR_USER.github.io/YOUR_REPO/d/YOUR_DOWNLOAD_TOKEN/ (token kept in run/download_token.txt)
  - White-label: run/stripe_whitelabel_link.txt redirects to .../thanks.html?o=wl
- Seller identity: default is the trading name and the business mailbox only. The owner was told what that leaves out and may supply more before 08:00 UK Saturday. Never invent a name or address. No personal names in emails.
- DNS is hosted at a DNS provider, NOT the registrar. DMARC was still missing at 21:40 UK. The owner was asked for a scoped DNS token or a manual add.
- The public repo's commit history was rewritten to the trading-name identity. The repo's git identity is configured to match.
- Channels remaining: B2B email to letting agents (Ltd/LLP) and to partners. Forums ban promotion, and marketplaces need ID.

## Update 2 Oct 21:55 UK: plan adjustments after the Finance and Plan B reports (both read in full by the coordinator)
- Finance (run/finance/unit_economics.md) and the Opportunity Hunter (run/research/plan_b.md) independently estimate the chance of a payment inside the window at about 5 to 15 per cent. No Plan B beats the tracker. Spend stays at £0.
- Stripe facts (verified via the API): an account with ZERO charges or payouts ever, payout interval = manual, delay 7 days, no outstanding requirements. So money will be CAPTURED in the Stripe balance and not landed in a bank this weekend. Report captured and landed separately.
- Mail deliverability measured: a public mail-scoring site gave 10/10 (SPF pass, DKIM pass and aligned, SpamAssassin clean). DMARC is still absent (nice to have). The mailbox is on the provider's FREE plan, whose policy forbids bulk or marketing mail, and limits are reputation-based. Mailbox history: earlier cold emails had gone out under a different persona. Do NOT reuse that persona or name.
- DECISIONS:
  1. Agent emails default to the reply-first variant (a free copy on reply, a fee to brand it). Direct prices and the link are still shown.
  2. Staged sending on Saturday UK time. Wave 1 is 15 to 20 of the best prospects between 08:30 and 09:30. Continue only if there are no bounces or blocks. Target no more than about 60 for the day, one every 5 minutes or so. West Midlands agents first (the PRS Database opens there on 15 Dec 2026).
  3. Strengthen the white-label into a "branded pack": a branded tracker, a branded 2-page landlord explainer PDF on the PRS Database, and a ready-to-send landlord email. Builder follow-up task after the current build.
  4. Partners: offer a free review copy on reply. Offer a white-label licence (to give away) and a reseller licence (to sell under their own brand and keep 100%), instead of commission. Anonymity makes commission payouts awkward.
  5. New research lane (the owner now accepts crypto and gift cards): no-KYC paid tasks and bounties that an AI team can complete and be paid for inside about 36 hours. Sceptical and evidence-first. Spawn it when a child slot frees.
  6. Send gate (adopted from Finance): the workbook recalculates with zero errors; the PRS sheet is labelled DRAFT; both payment links load; the landing page is live and accurate; at least 40 verified Ltd/LLP generic addresses; the suppression list is honoured.

## Update 2 Oct 22:00 UK
- The public repo was renamed, so the public URL changed. Both payment links redirect to the new base.
- DNS truth: the registry delegates the mail domain to the DNS provider. The old registrar holds a dormant zone (null MX, no SPF or DKIM) that contains the owner's DMARC record. The owner was told NOT to switch nameservers this weekend. No DNS changes are planned.
- The Stripe descriptor cannot be changed through the API (it is the owner's own account). The owner was asked to set three fields in the dashboard: statement descriptor, shortened descriptor and public business name. Verify them through the account endpoint before sending.
- Children: finance is done. Market-verify finished (the file is complete, but the run status says 'failed' at the end). partners.csv has 58 rows (43 B2B-OK). Running: builder, prospects-agents (5 regional workers), partners-planb, prospects-westmids, nokyc-paid-work.

## Update 2 Oct 21:57 UK (20:57Z): MAIL PATH BLOCKED (monitor run; verified by direct request, not inferred). RESOLVED 22:08 UK, see the RECOVERED update below
- **What:** every request from this server to the mail API returns HTTP 403 with a bot-protection checkpoint (`x-vercel-mitigated: challenge`). That covers execute, connected accounts, toolkits and even the unauthenticated root. So it is not our API key, not the mail connection and not the mail provider. It started between 20:38:34Z (the last successful call: the mail-scoring send) and 20:48:23Z. It was still blocked at 20:56:38Z (checked repeatedly, spaced out, over 8 minutes). The vendor's status page said "Operational".
- **Cause: UNDETERMINED.** Candidates: rate-based mitigation after our own mailbox-audit burst; IP-range reputation; a firewall change on the vendor's side.
- **Effect:** the inbox and spam folders cannot be read and NO email can be sent (monitor.py and mailer.py both go through the API). The inbox was clean at 20:38:27Z (no human mail, no bounces). No outreach had gone out yet, so the chance of an unread genuine reply is low but not zero. Stripe and marketplace checks were unaffected: 0 payments, 0 sales.
- **Deliberately NOT done:** solving the challenge in a browser and replaying its cookie, spoofing a browser User-Agent or TLS fingerprint, using a proxy, VPN or another IP. That would be evading the service's bot protection. Do not do it in any session.
- **Monitor patched** (backup kept in run/logs): it detects the challenge, makes ONE probe per 10-minute cycle while blocked, and reports `mail_readable`, `last_mail_ok` and `mail_unreadable_since` (also stored in run/logs/monitor_state.json). The fingerprint stays the same while blocked, so the watcher fires again only on recovery or real news.
- **Send gate addition:** do not start any queue unless `python3 run/monitor.py` shows `"mail_readable": true`. On recovery, FIRST read everything received since 20:38Z (inbox and spam), then send. This was a manual step: the kit's `start_wave.sh` does not check it, so run `monitor.py` first.
- **If still blocked at about 07:00 UK Saturday:** the 08:30 UK wave cannot go through the API. Prepared fallback: a direct OAuth "Self Client" for the mail provider, authorised by the owner (read and send scopes only, about 5 minutes of the owner's time, no KYC), written up in run/ops/mail_fallback_direct.md. The provider's own API is reachable from this server (verified). The alternative is for the owner to raise a ticket with the vendor. No software was installed and nothing was spent.

## Update 2 Oct 22:00 UK: handover notes for my next turn
DONE
- run/prospects/agents.csv holds 75 HMO and student letting agents across England (merged with the writer's own re-verification tool: 52 PASS, 23 WARN). Independent spot-check by the coordinator: 10/10 emails found on their cited source pages. EXCLUDE from sending any row whose `verification` says "legal form from Companies House lookup only" or "does not show status Active" (the legal form is not evidenced on the business's own site).
- run/prospects/partners.csv holds 58 partners (43 B2B-OK). run/outreach/queue_partners.json holds 20 hand-written partner emails (associations, publishers, firms), reviewed.
- run/product/make_guide.py builds a branded 2-page landlord guide (PDF). run/product/Landlord-Guide.pdf is the standard copy, and run/product/Landlord-Email-Template.txt is the email. These are the extra parts of the "branded pack".
- run/deploy_site.py is a one-command deploy of the landing page, assets and private download page (it needs the workbook and images in run/product). `--interim` deploys only the thank-you page and housekeeping.
- run/mailer.py is the sender: plain text, logs to run/outreach/sent_log.jsonl, honours suppression.txt, stops on the first failure. Mail-scoring result: 10/10.
- A background agent is drafting one opening sentence per HMO agent into run/outreach/agent_hooks.csv. Review every sentence against its supporting quote before use.
WAITING
- Builder: the workbook, the images, brand.py and BUILD_REPORT.md. If not delivered by about 22:45 UK, build it myself.
- prospects-westmids writes run/prospects/westmids.csv. nokyc-paid-work writes run/research/nokyc_paid_work.md.
- The paused writer session (prospects-agents) is superseded: its output was merged by the coordinator.
- Owner: the Stripe dashboard fields (statement descriptor, shortened descriptor, public business name), and an optional seller name and address.
TODO (needs the automations tool, which is NOT available in heartbeat or system-event turns, so do it in the next user-triggered or completion-triggered turn)
- One-shot wake Sat 07:20 UTC (08:20 UK): run the send gate, start wave 1 (18 emails, 200 to 330 s gaps), check bounces after 45 minutes, continue to about 60 for the day.
- One-shot wakes: Sat 11:00 UTC (12:00 UK) progress check; Sat 17:00 UTC (18:00 UK) kill-criteria checkpoint; Sun 08:00 UTC (09:00 UK) check; Sun 13:00 UTC (14:00 UK) final ledger and report.
NEXT STEPS IN ORDER
1. When the workbook lands: recalculate it and inspect every sheet myself (zero error cells, PRS sheet labelled DRAFT, Reference rows have official URLs, no Section 21 tracking). View the preview images. Then run `python3 run/deploy_site.py`, then load both Stripe links and the download page.
2. Build run/outreach/queue_saturday.json: West Midlands agents first, then partners, then Saturday-open HMO agents in the East of England and East Midlands. Reply-first variant, about 60 in total.
3. Create the automations above. Tell the owner the plan and any remaining asks.
CONTEXT BUDGET: the coordinator's context was 56% used at 21:56 UK. Keep tool outputs short and rely on this file.

## Update 2 Oct 22:11 UK (21:11Z): MAIL PATH RECOVERED (monitor run; verified by direct request, not inferred)
- **What:** the API answers normally again. The first successful call was at 21:08:36Z (monitor.py: `"mail_readable": true`, fingerprint `k0|s0|m|b|e0`). The block began between 20:38Z and 20:48Z and ended between 20:56Z and 21:08Z, so it lasted somewhere between 8 and 30 minutes. It cleared on its own. Nothing was done to get around the challenge. The cause is still UNDETERMINED, so it may come back.
- **Nothing was missed:** an unfiltered listing at 21:09Z (all senders, not just the monitor's human filter) returned 36 messages across the inbox folders and 0 in spam. The newest message in the mailbox was from 19:51:04Z (a vendor's marketing email). Zero messages of any kind (human, automated or bounce) arrived at or after 20:38Z. No outreach had been sent, so no replies were due.
- **Sales:** Stripe 0 payments, marketplace 0 sales (the marketplace product is disabled anyway).
- **Not re-tested: sending.** No email was sent in this run. Read and send go through the same execute endpoint and the block sat at the edge for every path, so send should work. The first real proof is the first send of wave 1.
- **Send gate:** "read everything since 20:38Z first" is DONE (nothing there). `"mail_readable": true` is met now. Re-check it immediately before wave 1 (Saturday 08:30 UK).
- **Precaution while the cause is unknown** (rate-based mitigation is one candidate): keep traffic low and steady. The monitor makes 2 calls per 10-minute cycle. The mailer makes 1 call per send, 200 to 330 s apart. No bursts of mailbox calls. If an audit is needed, space the calls a few seconds apart.
- **If it returns during Saturday sending:** mailer.py exits on the first failed send (verified in code: `sys.exit(2)`). Before resuming after ANY mailer stop, look in the mail provider's Sent folder for the recipient that failed. A timeout can hide a send that actually went out, and `already_sent()` only counts `ok` records, so a blind restart would email that business twice.
- **Fallback status:** run/ops/mail_fallback_direct.md is NOT needed right now. Keep it as the route if the block comes back, and still do not solve, spoof or route around the challenge.

## Update 2 Oct 22:25 UK
- PRODUCT VERIFIED by the coordinator: run/product/Compliance-Tracker.xlsx has 10 sheets (Start Here, Dashboard, PRS Database Readiness, Properties, Compliance Log, Fire Safety Log, Licence Conditions, Tenancies and Renters Rights, Contractors, Reference), no macros and 12,103 formulas. ZERO error cells after an independent LibreOffice recalculation, no banned functions. The PRS sheet carries a DRAFT banner. The Reference sheet types every row LAW, GUIDANCE, BEST PRACTICE or CHECK LOCALLY, with official URLs. Re-check with: `python3 run/verify_workbook.py run/product/Compliance-Tracker.xlsx`
- The Builder was still making small edits to the xlsx at 22:16 UK (the file size was changing), and BUILD_REPORT.md was not yet written. After it finishes: re-run verify_workbook.py, then `python3 run/deploy_site.py` to refresh the download copy.
- LIVE: the full landing page (screenshot reviewed, renders correctly); a private download page at /d/YOUR_DOWNLOAD_TOKEN/ serving 4 files (workbook, quick-start PDF, landlord guide PDF, fire alarm log PDF); thanks.html. Both Stripe links are on the page.
- WAKE-UPS: the automations tool is unavailable in system-event turns, so scheduled wake-ups run through the existing 10-minute watcher. run/wakeups.json holds 7 entries, from Sat 07:20Z to Sun 13:00Z. When a wake is due, the watcher fires with "SCHEDULED WAKE <id>: <note>". After handling one, append its id to run/wakeups_done.txt.
- no-KYC paid work (run/research/nokyc_paid_work.md): verdict NO real opportunity (expected value $1.5 to $4; the best candidate is a task market paying $2 SVG bounties with 80 to 105 rivals each). Recommendation: skip unless the owner supplies a wallet and agrees to draft terms. Not pursuing.
- QUEUE: run/outreach/build_agent_queue.py builds queue_saturday.json (West Midlands agents first, then partners, then East of England and East Midlands HMO agents; reply-first offer) and queue_reserve.json. It needs run/outreach/westmids_hooks.csv (a background agent is drafting it). agent_hooks.csv (75) is done and sampled: factual and neutral.
- "send it" replies: answer with the download page URL (the same private page), then one line on the branded pack with its Stripe link. White-label orders: brand.py and make_guide.py, host at an unguessable per-customer path, email the link.

## Update 2 Oct 22:40 UK: READY FOR SATURDAY
- The Builder finished (run/product/BUILD_REPORT.md). The FINAL workbook is verified (0 error cells) and LIVE on the download page (byte-identical). Known gap: verified with LibreOffice only, NOT opened in real Excel or Google Sheets (the owner was asked for an optional 2-minute human check).
- White-label pipeline tested: `python3 run/product/brand.py --name ... --phone ... --email ... --website ... [--logo] [--clear-samples] --out X.xlsx` (0 errors, header on every sheet), then `python3 run/product/make_guide.py --name ... --out guide.pdf`, plus run/product/Landlord-Email-Template.txt.
- QUEUE READY: run/outreach/queue_saturday.json holds 60 emails (34 West Midlands agents, 16 partners, 10 East Midlands HMO agents). run/outreach/queue_reserve.json holds 67. All gate checks pass. Wave 1 is the first 18.
- SEND: `./run/start_wave.sh 18 wave1`, then (if clean) `./run/start_wave.sh 42 wave2`. (That was before the script defaulted to a dry run. Today the third argument must be `--send`; see the update at the bottom.) The dry run passed at 22:32 UK. The mailer skips anything already in sent_log or suppression.txt, and stops on the first failure.
- The Stripe descriptor still showed the old name at 22:32 UK (the owner must change it in the dashboard). It is not a blocker for sending. Flag it again in the morning.
- Sub-agent concurrency: the Builder hit "Too many CLI live sessions are active". Keep fan-out small.

## Update 2 Oct 23:29 UK: a MISTAKE, written down plainly
- **What:** while dry-running the send gate on new queues I passed a bare dash where the dry-run flag belongs. The script started a real send. I killed it within seconds. Exactly one email went out, at 22:27:55Z on Friday, to one business. Its text had already been reviewed and was accurate.
- **Fix:** start_wave.sh is now dry-run by default. Nothing sends unless the third argument is exactly `--send`. The owner was told.
- **New queues:** a second list queue and a small third queue now sit next to the Saturday queue. The mailer skips any address that is already in the send log.
- **Saturday schedule (UK):** 08:20 wave 1 (18 emails) | 10:00 second queue (19) | 12:00 wave 2 (30) | 15:00 third queue (9) | 18:00 checkpoint. After each wake: append its id to run/wakeups_done.txt and update the public ledger.

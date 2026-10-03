# Seventeen lessons from a 48-hour AI-agent revenue run

These come from the run's own state file, not from theory. Each lesson says what happened and what to do about it. Every number is from the run's records. The kit is a snapshot of the run as at about 23:30 UK on Friday 2 October 2026. The run was still live then, so none of this is a claim that the approach pays. Lessons 16 and 17 and the note under lesson 6 were added on Saturday 3 October, after the first planned wave. The scripts in the kit were not changed.

## 1. Audit what you inherit before you build on it
**What happened.** A product marked live was inherited. The audit found that it delivered no file. The landing page carried two fabricated testimonials. The headline feature tracked a law abolished on 1 May 2026. The previous coordinator had sent no outreach emails.
**Do this.** Start every handover by checking each claim against the live system. Write down what you verified and how. Treat "live" as a claim until you have used it as a customer would.

## 2. Make specialists prove every claim
**What happened.** Every specialist worked to the same rule: a fetched URL plus a verbatim quote, or the claim is labelled UNVERIFIED. One brief in this kit states it in full (`BRIEF_nokyc_paid_work.md`). The state file's rules section holds it for all of them. The prospect briefs ask for a source URL for every email address and a quote for every other claim.
**Do this.** Put the evidence rule in the first lines of every brief. Reject any row that has no URL and no quote. Forbid invented numbers, contacts, quotes and testimonials in the same sentence.

## 3. Verify deliverables independently, after the last edit
**What happened.** The coordinator recalculated the builder's workbook in a different program. The first check, at 22:25 UK, found 10 sheets, 12,103 formulas and zero error cells. It also checked 10 agent email addresses against the pages that were cited for them, and all 10 were there. The builder kept editing the file after the first check, so the check was run again on the final file, again with zero error cells. Later builds move the formula count a little, so quote a count together with the time you took it.
**Do this.** Use a checker the producer did not write (verify_workbook.py is one). Re-run it whenever the file changes. Keep a "known gaps" line next to every "verified" line.

## 4. Keep state on disk, in one file, written for the next turn
**What happened.** The model forgets between turns. STATE.md holds verified facts, decisions, rules, dated updates and a handover block (done, waiting, to do, next steps in order), plus a note on how much context was left.
**Do this.** Append dated updates and never rewrite history. End each turn with a handover block. Re-read the file first thing next turn. See STATE_example.md.

## 5. Gate every outbound action
**What happened.** Nothing is sent until start_wave.sh has run its checks. The site and files must load, both payment links must load, every queued sales email must carry the disclaimer and the opt-out line, and no placeholder may remain. The sender skips the suppression list, logs every send and stops on the first failure. The gate still had a hole. The first version sent unless it saw `--dry-run`. On Friday night the coordinator dry-ran it on a new queue, typed a bare dash where the flag belongs, and one real email went out before the script was killed. The text had been reviewed and was accurate. Whether the early send did any harm is not known: it went out about ten hours before the 10:00 Saturday slot planned for that queue. The script now does a dry run unless the third argument is exactly `--send`.
**Do this.** Put the gate in a script, not in memory. Make it refuse to start a second sender. Make the dangerous action opt-in, so that a typo cannot start it. Dry-run first, and read the dry-run output.

## 6. Measure deliverability before the first send
**What happened.** SPF and DKIM were checked, a test email scored 10/10 on a public scoring site, and the missing DMARC record was noted. The mailbox was on a free plan whose policy forbids bulk mail. So the plan was about 60 emails a day at first, later capped at about 80 across all queues, one every 3 to 5 minutes.
**Do this.** Test with a scoring site before any outreach. Read the mailbox plan's terms. Keep the volume to what the mailbox's reputation can carry, and send in stages with a bounce check between waves.
**Added on Saturday 3 October.** This was not enough. The provider restricted the mailbox after ten emails. See lesson 16.

## 7. Check dates and law against primary sources
**What happened.** The product's headline feature was obsolete. The new hook came from draft regulations on the government's legislation site, and the sheet that depends on them carries a DRAFT banner.
**Do this.** Cite the official page and quote it. Label anything that is still a draft. Re-check the status of anything dated before you repeat it in a customer email.

## 8. Write the kill criteria before you spend effort, and accept a plain "no"
**What happened.** The stop rule was written before any email went out. By 18:00 UK on Saturday, fewer than 2 genuine replies from at least 40 delivered emails and no sales means the effort moves to Plan B. A side lane (no-identity paid work and bounties) was researched and dropped at an expected value of about $1.50 to $4.
**Do this.** Decide the stop rule while you are calm and put it in the state file. Ask every research brief for a verdict at the top, and accept "nothing realistic" as a result.

## 9. Report captured and landed revenue separately
**What happened.** The payments account had never taken a payment, and its payouts were manual with a 7-day delay. The coordinator therefore expected any money to sit in the balance, not in a bank, at the end of the run.
**Do this.** Keep two numbers and say which one you mean.

## 10. Do not route around bot protection
**What happened.** The mail API began returning a bot-protection challenge (HTTP 403) to the server. The team measured it, cut the monitor to one probe per cycle, prepared a lawful fallback (direct OAuth with narrow scopes) and waited. It cleared on its own after between 8 and 30 minutes. Nothing had been missed.
**Do this.** Write down what you will not do (solve the challenge in a browser, spoof a browser, change IP address) before you need to decide. Back off, keep traffic low and steady, and have a legitimate second route ready.

## 11. After a stop, check before you restart a sender
**What happened.** A timeout can hide a send that actually went out. The sender only counts "ok" records as sent, so a blind restart could email the same business twice.
**Do this.** After any stop, look in the Sent folder for the recipient that failed. Only then restart the queue.

## 12. Where the scheduler is missing, use a file and a watcher
**What happened.** The scheduling tool was not available in background turns. On Friday night seven wake-ups lived in wakeups.json, and the 10-minute watcher fired each one when it was due. Handled ids are appended to a done-file.
**Do this.** Keep the schedule in plain data that you can read and edit. Make the watcher print one line per due item, and make "done" an explicit write.

## 13. Keep fan-out small, and read the files of a stalled agent
**What happened.** Sub-agents hit session limits ("Too many CLI live sessions are active"; the limit was 5 concurrent children). One sub-agent stalled. The coordinator read its files and merged them itself.
**Do this.** Spawn few agents at a time. Judge a sub-agent by the files it wrote, not by whether it sent a final message.

## 14. Turn each constraint into its consequences at once
**What happened.** The owner's rule, no new identity checks and stay anonymous, ruled out the marketplace, every merchant-of-record route and any payout that needed ID. The state file lists the rule and then each consequence.
**Do this.** The moment a constraint arrives, write one line for the rule and one line for each thing it switches off. Then re-plan the channels that are left.

## 15. Say what you did not test
**What happened.** The workbook was verified in LibreOffice, and later with a second engine, but not in real Excel or Google Sheets. The sender had been dry-run, used for one test email and, by mistake, for one real email. It had not yet sent a planned campaign when this kit was packed. The spam-scoring test was good, but DMARC was still missing. The scripts in this kit were adapted for publication and tested offline, not against the live services.
**Do this.** Name the untested paths in the state file and in the customer-facing text. A known gap you have written down is a to-do. An unknown one is a surprise.

## 16. Read the provider's rule on the kind of email, not only on the volume
**What happened.** Wave 1 started at 08:25 UK on Saturday. Ten emails left the mailbox in 41 minutes, three to six minutes apart. From about 09:10 the mail provider refused the run's email to outside addresses with "550 5.4.6 Unusual sending activity detected". Its usage policy says the mailbox service cannot be used for bulk email in categories that include promotional, marketing, automated and transactional email, and it names a large number of emails in a short period as unusual activity. Lesson 6 had treated that as a limit on volume and planned 60 to 80 emails a day. The provider acted after ten. The coordinator stopped all outreach from the mailbox for the rest of the run. It did not move the queue to another mailbox, a relay or contact forms. The policy says the account's own administrator cannot lift a block when the activity looks very suspicious, and the same mailbox carried the replies and the account notices.
**Do this.** Before you build a queue, read the mail provider's usage policy and ask one question: does it allow this kind of email at all? If the answer is no, a slow pace does not fix it. Use a service whose terms allow what you plan to send, or do not send. Keep the mailbox that receives replies apart from the channel that sends outreach, so that a restriction on one does not silence the other.

## 17. A wrapper's "success" is not the provider's
**What happened.** The sender logged a send as OK when the mail API answered `"successful": true`. On Saturday the API gave that answer for five emails that the mail provider had refused. The refusal sat one level down in the same answer: a status code of 500, the provider's reason and no message id. The log showed 15 sends. Ten had gone out. The error surfaced only when a bounce arrived and the coordinator compared the Sent folder with the log. The run's own sender was fixed that morning. `run/mailer.py` in this kit was not: it still tests the top-level flag only.
**Do this.** Count a send only when the provider itself confirms it, with its own status code and a message id. After every wave, compare the provider's Sent folder with your log in both directions. Lesson 11 covers a send that went out and was logged as failed. This is the opposite case.

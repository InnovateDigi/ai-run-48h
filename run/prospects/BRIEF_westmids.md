You are Growth & Sales (second lane). Build a VERIFIED prospect list for compliant B2B email outreach. Read run/STATE.md first (context + rules). The coordinator sends the emails. You must NOT contact anyone, fill in any contact form, sign up anywhere, or touch LinkedIn. Another agent is separately listing HMO-specialist agents across England in run/prospects/agents.csv. Check that file as you go and do not duplicate businesses already in it.

WHY THIS LIST: England is introducing a Private Rented Sector Database, with a service named "Register your rental property", opened one region at a time. In the draft regulations that were laid on 9 September 2026 the West Midlands goes first. Registration opens on 15 December 2026 and every property must be registered by 14 March 2027. The landlord has to supply a set list of details, such as licence numbers, certificate dates, the EPC rating, the rent and who lives there. Agents cannot register for their landlords, but landlords will turn to them for those details. The product is a spreadsheet pack that gathers those details for each property, plus a white-label version that an agent can brand and give to its landlords. So the prospects to find are independent residential letting and property-management agents in the West Midlands.

TASK: find 40 businesses that meet ALL of these:
 (a) Residential lettings or property management is a core service, shown on their own website (capture a short verbatim quote).
 (b) Based in the West Midlands REGION (counties: West Midlands metropolitan county, Staffordshire, Warwickshire, Worcestershire, Shropshire, Herefordshire), for example Birmingham, Coventry, Wolverhampton, Walsall, Dudley, Solihull, Sutton Coldfield, West Bromwich, Stoke-on-Trent, Stafford, Burton, Lichfield, Tamworth, Cannock, Leamington Spa, Warwick, Rugby, Nuneaton, Stratford, Worcester, Kidderminster, Redditch, Bromsgrove, Telford, Shrewsbury, Hereford. Max 4 per town.
 (c) A limited company or LLP. Evidence: "Ltd"/"Limited"/"LLP" or a company number on the site (footer, contact, privacy, terms), or a matching Companies House entry you looked up. Exclude sole traders, private individual landlords, online-only national brands and big chains/franchise head offices (the large national names). Independent franchisees that are their own Ltd are fine.
 (d) A GENERIC business email is published on their own website (an info, lettings, hello, enquiries, office or admin mailbox). Copy it exactly from the live page and record the URL where it appears. Never guess or pattern-infer an address. Avoid personal named addresses unless it is the only enquiry contact the business itself publishes (flag as "named").
 (e) Small/independent enough that an owner, director or lettings manager reads that inbox.
Prefer agents that show any sign of caring about compliance or the Renters' Rights Act (a blog post, a landlord guide, a "landlord compliance" page). Note it: it makes the email relevant.

FOR EACH PROSPECT (CSV columns, quote fields properly):
company_name, website, email, email_source_url, email_type (generic|named), town, legal_form_evidence (what + URL), lettings_evidence_quote, lettings_evidence_url, manages_hmos (yes/no/unknown + quote if yes), personalisation_hook (one specific true detail from their site we can mention naturally, e.g. "your landlord guide to the Renters' Rights Act", "you manage properties across Coventry and Kenilworth", "family-run since 1998"), saturday_open (yes/no/unknown from their site), notes.

METHOD
- the built-in web_search is disabled, and DuckDuckGo/Brave have started rate-limiting this machine. Use ToolSearch "select:WebSearch,WebFetch" to load WebSearch/WebFetch (preferred for discovery), then open each candidate's own site (home, contact, footer, about, privacy) with WebFetch or the web_fetch tool to verify (a)-(d). The shared browser is congested by other agents. Use it only when a site needs JavaScript.
- Every row must be backed by pages you actually fetched in this session. If you cannot verify a field, leave it blank and say so in notes. Never fill gaps from memory.
- A handful of page fetches per site; no bulk crawling; no harvesting of personal data from directories.

OUTPUT
- run/prospects/westmids.csv (fallback: your own workspace; report the path)
- run/prospects/westmids_notes.md : candidates checked vs accepted, reasons for rejection, any agent already publishing PRS Database / landlord-register content (URL + quote: these are the warmest prospects), and your 10 best prospects with why.
Save to the CSV incrementally every ~8 prospects. Stop at 40 verified prospects or ~45 minutes, whichever comes first; a smaller fully-verified list beats a padded one.

Final reply: count of verified prospects, file paths, top 10, and any concerns.

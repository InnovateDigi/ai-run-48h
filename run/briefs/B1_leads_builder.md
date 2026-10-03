# Brief B1. Builder: a per-city list built from a public register (Companies House data)
Read run/STATE.md (rules). Do not contact anyone, spend money, edit the website repo or print secrets. Do your own work; at most 1 helper (the host hits "too many CLI sessions").

WHY: letting agents, landlord accountants and mortgage brokers want to know which NEW property companies (buy-to-let SPVs, landlord companies) appear in their area. Companies House publishes this; nobody packages it per city. The plan is a one-off list per city, delivered by email.

DATA: Companies House API, key in .env.local as COMPANIES_HOUSE_KEY (HTTP basic auth, key as username, empty password). Verified working tonight:
GET https://api.company-information.service.gov.uk/advanced-search/companies?sic_codes=68209,68100,68320&incorporated_from=2026-09-01&incorporated_to=2026-09-30&location=Manchester&company_status=active&size=20  -> "hits": 205. Respect the rate limit (600 requests / 5 minutes); paginate with size + start_index.

BUILD (in run/leads/):
1. build_leads.py --city NAME --areas M,OL,SK --from 2026-09-01 --to 2026-09-30 : fetch all matches, then KEEP ONLY companies whose registered-office POSTCODE AREA is in --areas (the API "location" text match also returns e.g. "Manchester Road" elsewhere, so filter by postcode). De-duplicate by company number.
2. Company-level fields ONLY (no officers, no personal data lookups): company_name, company_number, incorporation_date, company_type, sic_codes, registered_office_address (one line), post_town, postcode, companies_house_url, category, shared_address_count.
   - category (rule-based, documented in the README): "landlord / property investment" (SIC 68209 or 68100 and name not matching block-management patterns), "letting or managing agent" (SIC 68320 only), "block / residents management company" (name contains MANAGEMENT COMPANY, RESIDENTS, RTM, FREEHOLD, (BLOCK), COURT MANAGEMENT etc.). The last group is NOT a landlord lead and must be labelled so.
   - shared_address_count = how many companies in this month's list share the same registered office (>=3 suggests an accountant or formation agent address). Keep the row but flag it.
3. Output per city: <city>-2026-09.csv (sorted: landlord/property investment first, then by incorporation date) and <city>-2026-09-sample.csv (first 10 landlord rows).
4. summary.json: for each city {total, landlord_property_investment, agents, block_rmc, shared_address_rows, date_range, generated_at_utc}.
5. README.txt (plain, short): what the list is, source ("Companies House public register, used under the Open Government Licence v3.0"), field definitions, how categories are derived, caveats (registered office may be an accountant's address; a new company is not proof of a purchase; no personal data included), date generated.
CITIES and postcode areas: Manchester (M), Leeds (LS), Liverpool (L), Sheffield (S), Newcastle upon Tyne (NE), Bristol (BS), Nottingham (NG), Leicester (LE), Derby (DE), Hull (HU), Southampton (SO), Portsmouth (PO), Brighton (BN), Plymouth (PL), Exeter (EX), Oxford (OX), Reading (RG), Cambridge (CB), Norwich (NR), Lincoln (LN), Bath (BA), Durham (DH), Birmingham (B), Coventry (CV), Stoke-on-Trent (ST). For broad coverage query by postcode area where the API allows, or use several location terms per city and then filter by postcode area.

VERIFY: for 3 cities, open 5 random rows on https://find-and-update.company-information.service.gov.uk/company/<number> (WebFetch or curl) and confirm name, incorporation date and SIC match. Re-run one city and confirm the count is stable. Put the evidence in LEADS_REPORT.md (max 60 lines, short lines).
FINAL REPLY (max 15 lines): the summary table (city, total, landlord rows), file paths, anything odd in the data, and whether you consider the list good enough to sell.

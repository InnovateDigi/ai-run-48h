#!/usr/bin/env python3
"""Deploys the public site (landing page, assets, thank-you page) and an unlisted download page to GitHub Pages.

  deploy_site.py [--no-push] [--interim]

- Landing page source: run/outreach/landing_v2.html ({{BUY_URL}} / {{WL_URL}} filled from run/stripe_*_link.txt).
- Thank-you page source: run/outreach/thanks.html, copied to <repo>/thanks.html. Your payment links send buyers there,
  and start_wave.sh checks that it loads.
- Images: every run/product/*.png listed in ASSETS is copied to <repo>/assets/.
- Download page: <repo>/d/<token>/ with the deliverable files (token in run/download_token.txt, never printed).
  UNLISTED, NOT PROTECTED: the unguessable folder name hides the files, it does not guard them. In a public repository
  anyone can browse them, and anyone who learns the address can download them. For real access control use a delivery service.
- --interim publishes only the thank-you page and housekeeping, not the landing page or the download page.
Refuses to deploy if a referenced image, a deliverable file or the landing page is missing (a missing thank-you page is only noted,
but --interim needs it), or if a page it generates still contains a YOUR_ placeholder, you@example.com or a {{ template token.
It adds and commits only the files it wrote. If git status in site-repo/ shows any other changed or untracked file, before or
after the deploy writes, it refuses and lists them, so a stray file is never published.
Setup: clone your Pages repository to site-repo/ in the project root and check out its gh-pages branch."""
import os, re, shutil, subprocess, sys, html
from urllib.parse import urlparse

ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())
REPO = f"{ROOT}/site-repo"          # local checkout of YOUR_USER/YOUR_REPO (branch gh-pages)
PROD = f"{ROOT}/run/product"
BASE = "https://YOUR_USER.github.io/YOUR_REPO"
ASSETS = ["cover.png", "thumb.png", "preview-1.png", "preview-2.png"]
# files or folders to delete from the repo before each deploy (the run used this to clean up an earlier site)
REMOVE_LEFTOVERS = ()
# words that must not appear on the live page, for example the name of a payment route or brand you have dropped
FORBIDDEN_WORDS = ()
# (file in run/product, label, note), in the order shown on the download page. These are sample values: replace them with your own,
# and keep the file names the same as in the list inside start_wave.sh.
DELIVERABLES = [
    ("Compliance-Tracker.xlsx", "Your compliance tracker (Excel / Google Sheets)", "The tracker. Open in Excel, or upload to Google Drive and open with Google Sheets."),
    ("Quick-Start-Guide.pdf", "Quick-start guide (PDF)", "Setup in Excel and Google Sheets, how the colours work, how to clear the sample data."),
    ("Landlord-Guide.pdf", "A landlord's guide to the new register (PDF)", "A two-page explainer: what the register is, when it starts and which details it asks for."),
    ("Test-Log.pdf", "Weekly fire alarm test log (printable PDF)", "Print one per property and keep it with your fire risk assessment."),
]
LEFTOVER = re.compile(r"YOUR_|you@example\.com|\{\{")


def sh(*cmd, cwd=REPO, strip=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        msg = f"command failed: {' '.join(cmd[:3])}...\n{(r.stderr or r.stdout)[-400:]}"
        sys.exit(re.sub(r"://[^/@\s]+@", "://***@", msg))   # never echo a credential held in a remote URL
    return r.stdout.strip() if strip else r.stdout


def planned(token, interim):
    """The paths this deploy may change in the repository. A name that ends in / is a folder that is removed as a whole."""
    names = ["thanks.html"]
    if not interim:
        names += ["index.html", f"d/{token}/index.html"] + [f"assets/{a}" for a in ASSETS] + [f"d/{token}/{f}" for f, _, _ in DELIVERABLES]
    return names + [j.strip("/") + ("/" if os.path.isdir(f"{REPO}/{j}") else "") for j in REMOVE_LEFTOVERS]


def changed_paths():
    """Every path that git status reports in the site repository, untracked files included."""
    parts, paths, i = sh("git", "status", "--porcelain", "-z", "--untracked-files=all", strip=False).split("\0"), [], 0
    while i < len(parts):
        entry, i = parts[i], i + 1
        if len(entry) < 4:
            continue
        paths.append(entry[3:])
        if entry[0] in "RC" or entry[1] in "RC":      # a rename or copy is followed by the old name
            paths.append(parts[i]); i += 1
    return paths


def refuse_if_stray(paths, allowed, when):
    stray = sorted({p for p in paths if not any(p == a or (a.endswith("/") and p.startswith(a)) for a in allowed)})
    if stray:
        shown = ", ".join(stray[:10]) + (f" and {len(stray) - 10} more" if len(stray) > 10 else "")
        sys.exit(f"site-repo/ {when} changed or untracked files that this deploy did not write: {shown}. Nothing was committed or pushed. "
                 "Commit, move or delete them (see git status in site-repo/), then deploy again.")


def read(path):
    try:
        return open(path, encoding="utf-8").read().strip()
    except FileNotFoundError:
        sys.exit(f"missing file: {path}")


def check_clean(label, text):
    m = LEFTOVER.search(text)
    if m:
        sys.exit(f"the {label} still contains a placeholder ({m.group(0)}). Fix it before deploying.")


def download_page():
    items = []
    for fname, label, note in DELIVERABLES:
        src = f"{PROD}/{fname}"
        if not os.path.exists(src):
            sys.exit(f"missing deliverable: {fname}")
        kb = max(1, os.path.getsize(src) // 1024)
        items.append(f'<li><a class="file" href="{html.escape(fname)}" download>{html.escape(label)}</a> <span class="muted">{kb} KB</span><br><span class="muted">{html.escape(note)}</span></li>')
    # The wording below is a template. Every YOUR_ line must be replaced with your own text, or the deploy is refused.
    page = f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Your download | YOUR_PRODUCT_NAME</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#14213d;background:#f7f8fb;line-height:1.6;margin:0}}
.card{{max-width:700px;margin:48px auto;background:#fff;border:1px solid #e4e7ee;border-radius:12px;padding:34px}}h1{{font-size:1.7rem;margin:0 0 8px}}
ul{{list-style:none;padding:0;margin:18px 0}}li{{padding:14px 0;border-bottom:1px solid #e4e7ee}}a.file{{font-weight:700;color:#0b6e4f;font-size:1.05rem}}
.muted{{color:#5b6475;font-size:.93rem}}.note{{background:#f1f8f5;border:1px solid #cfe6dc;border-radius:8px;padding:12px 14px;margin-top:16px;font-size:.95rem}}</style></head>
<body><div class="card">
<h1>Thank you. Here are your files.</h1>
<p>Save this page's address: it is your download link. We will also email you a copy of it.</p>
<ul>{''.join(items)}</ul>
<div class="note"><strong>Getting started:</strong> YOUR_GETTING_STARTED_LINE Questions or a problem? Email <a href="mailto:you@example.com">you@example.com</a>. YOUR_SUPPORT_AND_REFUND_TERMS</div>
<p class="muted" style="margin-top:18px">YOUR_TRADING_NAME is a private business that is not affiliated with any public body. YOUR_ONE_LINE_PRODUCT_DISCLAIMER Licensed for your own use; please do not redistribute.</p>
</div></body></html>"""
    check_clean("download page", page)
    return page


def write_download_page(token, page):
    d = f"{REPO}/d/{token}"
    os.makedirs(d, exist_ok=True)
    for fname, _, _ in DELIVERABLES:
        shutil.copy2(f"{PROD}/{fname}", f"{d}/{fname}")
    open(f"{d}/index.html", "w", encoding="utf-8").write(page)
    return len(DELIVERABLES)


def main():
    interim = "--interim" in sys.argv
    if not os.path.exists(f"{REPO}/.git"):
        sys.exit("site-repo/ is not a git checkout: clone your Pages repository there and check out gh-pages (see the README)")
    token = read(f"{ROOT}/run/download_token.txt")
    buy, wl = read(f"{ROOT}/run/stripe_standard_link.txt"), read(f"{ROOT}/run/stripe_whitelabel_link.txt")
    for u in (buy, wl):  # edit this check if you use another payments provider
        host = urlparse(u).hostname or ""
        if not (u.startswith("https://") and (host == "stripe.com" or host.endswith(".stripe.com"))):
            sys.exit("a payment link file does not hold an https link on stripe.com")
    allowed = planned(token, interim)
    refuse_if_stray(changed_paths(), allowed, "holds")          # before anything is written or any branch is switched
    sh("git", "checkout", "-q", "gh-pages")
    # Build and check everything in memory first, so a refusal leaves the working tree untouched.
    thanks_src = f"{ROOT}/run/outreach/thanks.html"
    thanks = open(thanks_src, encoding="utf-8").read() if os.path.exists(thanks_src) else None
    if interim and thanks is None:
        sys.exit("--interim publishes the thank-you page: create run/outreach/thanks.html first")
    if thanks is not None:
        check_clean("thank-you page", thanks)
    if not interim:
        page = read(f"{ROOT}/run/outreach/landing_v2.html").replace("{{BUY_URL}}", buy).replace("{{WL_URL}}", wl)
        check_clean("landing page", page)
        if any(w in page.lower() for w in FORBIDDEN_WORDS):
            sys.exit("the landing page contains a word from FORBIDDEN_WORDS")
        used = set(re.findall(r'assets/([A-Za-z0-9._-]+\.png)', page))
        missing = [a for a in used if not (a in ASSETS and os.path.exists(f"{PROD}/{a}")) and not os.path.exists(f"{REPO}/assets/{a}")]
        if missing:
            sys.exit(f"landing page references missing images: {missing}")
        dl = download_page()
        os.makedirs(f"{REPO}/assets", exist_ok=True)
        for a in ASSETS:
            if os.path.exists(f"{PROD}/{a}"):
                shutil.copy2(f"{PROD}/{a}", f"{REPO}/assets/{a}")
        open(f"{REPO}/index.html", "w", encoding="utf-8").write(page + "\n")
        n = write_download_page(token, dl)
        print(f"landing page written; download page built with {n} files")
    if thanks is not None:
        open(f"{REPO}/thanks.html", "w", encoding="utf-8").write(thanks)
        print("thank-you page written")
    else:
        print("note: no run/outreach/thanks.html, so no thank-you page was published (start_wave.sh checks that /thanks.html loads)")
    # remove leftovers that should not be public
    for junk in REMOVE_LEFTOVERS:
        p = f"{REPO}/{junk}"
        if os.path.isdir(p): shutil.rmtree(p)
        elif os.path.exists(p): os.remove(p)
    paths = changed_paths()
    refuse_if_stray(paths, allowed, "now holds")
    if not paths:
        print("nothing to commit"); return
    sh("git", "add", "--", *paths)                                # only the files this deploy wrote, never everything in the folder
    sh("git", "commit", "-q", "-m", "Interim: thank-you page and housekeeping" if interim else "Full landing page, assets and download page", "--", *paths)
    if "--no-push" not in sys.argv:
        sh("git", "push", "-q", "origin", "gh-pages")
        print("pushed to gh-pages ->", BASE + "/")


if __name__ == "__main__":
    main()

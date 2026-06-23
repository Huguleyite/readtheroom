#!/usr/bin/env python3
"""
update-homepage.py
Replaces the RTR "Latest Issues" block and issue count in index.html.
Called by the GitHub Actions workflow on a scheduled publish date.

Usage:
    python scripts/update-homepage.py --issue 7
    python scripts/update-homepage.py --issue 8
"""

import argparse
import re
import sys
from pathlib import Path

# ── Issue data ────────────────────────────────────────────────────────────────

ISSUES = {
    7: {
        "num": "07",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #7 &nbsp;&middot;&nbsp; May 19, 2026",
        "headline": "Your emails are in a government database. No warrant required.",
        "teaser": (
            "The government collects your calls and emails under a law designed for "
            "foreign terrorists. The FBI has run hundreds of thousands of searches "
            "without a warrant. Congress has until June&nbsp;12 to decide if that needs "
            "to change. This week, both sides."
        ),
        "href": "/read-the-room/issue/7/",
        "count": "7 issues published",
    },
    8: {
        "num": "08",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #8 &nbsp;&middot;&nbsp; May 26, 2026",
        "headline": (
            "$1.02 trillion in reduced spending. &ldquo;No cuts.&rdquo; "
            "The CBO and the administration are working from the same numbers."
        ),
        "teaser": (
            "The One Big Beautiful Bill restructured Medicaid in ways the CBO projects "
            "will cost 10.5&nbsp;million people their coverage by 2034. The administration "
            "says federal spending still grows 47&nbsp;percent. Both arguments draw from "
            "the same projections. This week, both sides."
        ),
        "href": "/read-the-room/issue/8/",
        "count": "8 issues published",
    },
    9: {
        "num": "09",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #9 &nbsp;&middot;&nbsp; June 2, 2026",
        "headline": (
            "The 14th Amendment settled birthright citizenship in 1868. "
            "A 2025 executive order says it&rsquo;s been misread ever since. "
            "The Supreme Court is about to rule."
        ),
        "teaser": (
            "Five words &mdash; &ldquo;subject to the jurisdiction thereof&rdquo; &mdash; are at "
            "the center of a constitutional debate that was last settled in 1898. "
            "A ruling is expected before the Court&rsquo;s term ends. An estimated 400,000 "
            "births per year are at stake. This week, both sides."
        ),
        "href": "/read-the-room/issue/9/",
        "count": "9 issues published",
    },
    10: {
        "num": "10",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #10 &nbsp;&middot;&nbsp; June 9, 2026",
        "headline": (
            "A Treasury prototype with Trump&rsquo;s face on a $250 bill. "
            "A 160-year-old law that says no. "
            "The debate about what currency is for."
        ),
        "teaser": (
            "The Bureau of Engraving and Printing has prepared prototypes of a $250 bill "
            "bearing President Trump&rsquo;s portrait. A law passed in 1866 prohibits "
            "the likeness of any living person on U.S. currency. "
            "Both sides, no spin."
        ),
        "href": "/read-the-room/issue/10/",
        "count": "10 issues published",
    },
    11: {
        "num": "11",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #11 &nbsp;&middot;&nbsp; June 16, 2026",
        "headline": (
            "A law requiring proof of citizenship to register to vote. "
            "21 million Americans may not have the document. "
            "A Senate vote that has failed twice."
        ),
        "teaser": (
            "The SAVE America Act passed the House in February. It accepts only three documents: "
            "a passport, a birth certificate, or a naturalization certificate. "
            "Driver&rsquo;s licenses don&rsquo;t qualify. "
            "The Senate has rejected it twice. Both sides, no spin."
        ),
        "href": "/read-the-room/issue/11/",
        "count": "11 issues published",
    },
    12: {
        "num": "12",
        "pub_label": "Read the Room &nbsp;&middot;&nbsp; Issue #12 &nbsp;&middot;&nbsp; June 24, 2026",
        "headline": (
            "Trump called the JCPOA the worst deal ever. "
            "In June 2026, he signed a 14-point memorandum to end the Iran war. "
            "Here is how the two compare."
        ),
        "teaser": (
            "On June 15, 2026, the United States and Iran signed a memorandum of understanding. "
            "The active war ended. The Strait of Hormuz reopened. "
            "A 60-day negotiating window began. "
            "Both sides, no spin."
        ),
        "href": "/read-the-room/issue/12/",
        "count": "12 issues published",
    },
}

# ── RTR block template ────────────────────────────────────────────────────────

RTR_BLOCK_TEMPLATE = """\
  <!-- RTR-LATEST-START -->
  <div class="split-rtr">
    <div class="deco-num deco-num-rtr">{num}</div>
    <p class="split-pub-label split-pub-label-rtr">{pub_label}</p>
    <div class="split-rule split-rule-rtr"></div>
    <h2 class="split-hed split-hed-rtr">{headline}</h2>
    <p class="split-teaser">
      {teaser}
    </p>
    <a href="{href}" class="split-btn split-btn-rtr">Read the full issue &rarr;</a>
  </div>
  <!-- RTR-LATEST-END -->"""

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update RTR homepage latest issue block.")
    parser.add_argument("--issue", type=int, required=True, choices=list(ISSUES.keys()),
                        help="Issue number to promote to homepage latest.")
    args = parser.parse_args()

    issue = ISSUES[args.issue]
    index_path = Path(__file__).parent.parent / "index.html"

    if not index_path.exists():
        print(f"ERROR: index.html not found at {index_path}", file=sys.stderr)
        sys.exit(1)

    html = index_path.read_text(encoding="utf-8")

    # Replace RTR latest block (between sentinel comments)
    rtr_pattern = re.compile(
        r"<!-- RTR-LATEST-START -->.*?<!-- RTR-LATEST-END -->",
        re.DOTALL
    )
    new_block = RTR_BLOCK_TEMPLATE.format(**issue)
    html, n = rtr_pattern.subn(new_block, html)
    if n == 0:
        print("ERROR: RTR-LATEST-START/END sentinels not found in index.html.", file=sys.stderr)
        sys.exit(1)

    # Replace issue count (between count sentinels)
    count_pattern = re.compile(
        r"<!-- RTR-COUNT -->.*?<!-- /RTR-COUNT -->",
        re.DOTALL
    )
    new_count = f"<!-- RTR-COUNT -->{issue['count']}<!-- /RTR-COUNT -->"
    html, m = count_pattern.subn(new_count, html)
    if m == 0:
        print("WARNING: RTR-COUNT sentinels not found. Issue count not updated.", file=sys.stderr)

    index_path.write_text(html, encoding="utf-8")
    print(f"SUCCESS: index.html updated for RTR Issue #{args.issue}.")


if __name__ == "__main__":
    main()

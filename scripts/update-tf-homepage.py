#!/usr/bin/env python3
"""
update-tf-homepage.py
Replaces The Frequency "Latest Issue" block and issue count in index.html.
Called by the GitHub Actions workflow on a scheduled Thursday publish date.

Usage:
    python scripts/update-tf-homepage.py --issue 7
"""

import argparse
import re
import sys
from pathlib import Path

# ── Issue data ────────────────────────────────────────────────────────────────
# Each issue entry needs:
#   num         : zero-padded issue number shown as deco element ("07")
#   pub_label   : label line shown under the deco number
#   headline    : main H2 headline for the issue
#   stories     : list of 5 dicts — each has tag_bg, tag_color, tag_label, text
#   href        : link target for "Read the full issue" button
#   count       : text for the subscriber strip issue count

ISSUES = {
    7: {
        "num": "07",
        "pub_label": "The Frequency &nbsp;&middot;&nbsp; Issue #7 &nbsp;&middot;&nbsp; May 28, 2026",
        "headline": "After Tuesday.",
        "stories": [
            {
                "tag_bg": "#FAECE7", "tag_color": "#993C1D",
                "tag_label": "Elections",
                "text": "Two Left Standing.",
            },
            {
                "tag_bg": "#FAEEDA", "tag_color": "#854F0B",
                "tag_label": "Energy",
                "text": "The July 15 Clock.",
            },
            {
                "tag_bg": "#FAECE7", "tag_color": "#993C1D",
                "tag_label": "Elections",
                "text": "November&rsquo;s On.",
            },
            {
                "tag_bg": "#E6F1FB", "tag_color": "#185FA5",
                "tag_label": "Education",
                "text": "The $250M Question.",
            },
            {
                "tag_bg": "#EEEDFE", "tag_color": "#534AB7",
                "tag_label": "Local Gov.",
                "text": "What the County Settled.",
            },
        ],
        "href": "/the-frequency/issue/7/",
        "count": "7 issues published",
    },
    # ── Add future issues here, e.g.: ────────────────────────────────────────
    # 8: {
    #     "num": "08",
    #     "pub_label": "The Frequency &nbsp;&middot;&nbsp; Issue #8 &nbsp;&middot;&nbsp; June 5, 2026",
    #     "headline": "...",
    #     "stories": [...],
    #     "href": "/the-frequency/issue/8/",
    #     "count": "8 issues published",
    # },
}

# ── TF block template ─────────────────────────────────────────────────────────

def build_stories_html(stories):
    """Render the five tf-mini-item divs from the stories list."""
    lines = []
    for i, s in enumerate(stories, start=1):
        lines.append(
            f'      <div class="tf-mini-item">\n'
            f'        <span class="tf-mini-num">{i:02d}</span>\n'
            f'        <span class="mini-tag" style="background:{s["tag_bg"]};color:{s["tag_color"]};">'
            f'{s["tag_label"]}</span>\n'
            f'        {s["text"]}\n'
            f'      </div>'
        )
    return "\n".join(lines)


TF_BLOCK_TEMPLATE = """\
  <!-- TF-LATEST-START -->
  <div class="split-tf">
    <div class="deco-num deco-num-tf">{num}</div>
    <p class="split-pub-label split-pub-label-tf">{pub_label}</p>
    <div class="split-rule split-rule-tf"></div>
    <h2 class="split-hed split-hed-tf">{headline}</h2>
    <div class="tf-stories-mini">
{stories_html}
    </div>
    <a href="{href}" class="split-btn split-btn-tf">Read the full issue &rarr;</a>
  </div>
  <!-- TF-LATEST-END -->"""

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Update TF homepage latest issue block.")
    parser.add_argument("--issue", type=int, required=True, choices=list(ISSUES.keys()),
                        help="Issue number to promote to homepage latest.")
    args = parser.parse_args()

    issue = ISSUES[args.issue]
    index_path = Path(__file__).parent.parent / "index.html"

    if not index_path.exists():
        print(f"ERROR: index.html not found at {index_path}", file=sys.stderr)
        sys.exit(1)

    html = index_path.read_text(encoding="utf-8")

    # Replace TF latest block (between sentinel comments)
    tf_pattern = re.compile(
        r"<!-- TF-LATEST-START -->.*?<!-- TF-LATEST-END -->",
        re.DOTALL
    )
    stories_html = build_stories_html(issue["stories"])
    new_block = TF_BLOCK_TEMPLATE.format(
        num=issue["num"],
        pub_label=issue["pub_label"],
        headline=issue["headline"],
        stories_html=stories_html,
        href=issue["href"],
    )
    html, n = tf_pattern.subn(new_block, html)
    if n == 0:
        print("ERROR: TF-LATEST-START/END sentinels not found in index.html.", file=sys.stderr)
        sys.exit(1)

    # Replace TF issue count (between count sentinels)
    count_pattern = re.compile(
        r"<!-- TF-COUNT -->.*?<!-- /TF-COUNT -->",
        re.DOTALL
    )
    new_count = f"<!-- TF-COUNT -->{issue['count']}<!-- /TF-COUNT -->"
    html, m = count_pattern.subn(new_count, html)
    if m == 0:
        print("WARNING: TF-COUNT sentinels not found. Issue count not updated.", file=sys.stderr)

    index_path.write_text(html, encoding="utf-8")
    print(f"SUCCESS: index.html updated for The Frequency Issue #{args.issue}.")


if __name__ == "__main__":
    main()

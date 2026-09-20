# Read the Returns — Data Spec (v1)

The contract between the **adapter** (fetches and normalizes Alabama's unofficial election-night results) and the **page** (`/returns/`). The page renders whatever this file describes; it never calls races.

## Where it lives

- Published as a single JSON file from the separate data repo (working name `rtr-returns-data`) by a custom GitHub Actions workflow, about every 10 minutes on an off-minute cron (for example `3,13,23,33,43,53 * * * *`).
- The page's `DATA_URL` constant (top of the script in `returns/index.html`) points at it. While `DATA_URL` is empty, the page shows the pre-election ballot.
- The page appends a cache-busting `?t=<timestamp>` and re-fetches every 3 minutes while the tab is visible.

## Top level

| Field | Type | Notes |
|---|---|---|
| `schema` | `1` | Must be the number `1`, or the page ignores the file. |
| `status` | `"pre"` \| `"live"` \| `"final"` | `pre` = no results yet (page shows the ballot). `live` = counting. `final` = state reports all counties done; still unofficial until certified. |
| `generated_at` | ISO 8601 UTC string | When the adapter last ran successfully. Drives the "Updated" pill and the stale warning (over 30 minutes while `live`). |
| `source` | object, optional | `name` (string), `url` (https link to the state's page), `updated_at` (ISO, the state's own "Last Updated"). |
| `contests` | array | See below. Order = display order for map chips and extra Chambers rows. |

## Contest

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable id. Roster ids the page knows: `gov`, `us-sen`, `us-house-3`, `al-senate-13`, `al-house-38`. Any other id (Lt. Gov., AG, SoS, PSC, amendments, county offices) is added automatically as an extra row on the Chambers card if it has Chambers numbers. |
| `title` | string | Display title. |
| `candidates` | array of `{ id, name, party }` | `party` is `"D"`, `"R"`, other letters, or `""` (amendments, nonpartisan). Order = display order (Democrat first by convention). `id` is unique inside the contest and is the key used in `votes`. |
| `statewide` | object, optional | `votes` (`{candidateId: int}`) and `updated_at`. If present, used for statewide totals; otherwise the page sums `counties`. |
| `counties` | object | Keys are 5-digit FIPS strings (Chambers = `"01017"`). Include only counties the state has posted for this contest. A contest with more than 3 counties becomes a map chip. |

## County entry (inside `counties`)

| Field | Type | Notes |
|---|---|---|
| `votes` | `{candidateId: int}` | Whole numbers. Omit write-ins or fold them out of the candidate list; percentages are of the listed candidates. |
| `boxes_reported`, `boxes_total` | int, optional | Preferred. Shown as "14 of 20 boxes reported". |
| `boxes_pct` | number 0–100, optional | Fallback when the state only gives a percentage. |
| `updated_at` | ISO 8601 UTC string | The state's timestamp for that county if available, else the adapter's. Shown beside every figure. |

A county counts as "fully reporting" when `boxes_reported >= boxes_total`, or `boxes_pct >= 100`.

## Rules the adapter must follow

1. **No race calls.** No `winner`, `called`, or similar fields. The page shows votes and who is ahead.
2. **Unknown is omitted, not zero.** A county with no posted totals is left out of `counties`.
3. **All numbers are integers** (votes, boxes) except `boxes_pct`.
4. **Keep the last good file.** If a fetch or parse fails, do not overwrite the published JSON with partial or empty data. The page's stale warning covers the gap.
5. **Sanity checks before publishing:** every county key is a valid Alabama FIPS (`01001`–`01133`, odd numbers); vote totals never drop from one run to the next by more than a correction margin (log and flag if they do); `generated_at` is the run time.
6. **Text is display text.** The page inserts titles and names as plain text, never HTML.

## Example

```json
{
  "schema": 1,
  "status": "live",
  "generated_at": "2026-11-04T02:43:07Z",
  "source": {
    "name": "Alabama Secretary of State, unofficial election night reporting",
    "url": "https://www2.alabamavotes.gov/electionNight/",
    "updated_at": "2026-11-04T02:40:00Z"
  },
  "contests": [
    {
      "id": "gov",
      "title": "Governor",
      "candidates": [
        { "id": "jones", "name": "Doug Jones", "party": "D" },
        { "id": "tuberville", "name": "Tommy Tuberville", "party": "R" }
      ],
      "counties": {
        "01017": {
          "votes": { "jones": 3100, "tuberville": 5400 },
          "boxes_reported": 14,
          "boxes_total": 20,
          "updated_at": "2026-11-04T02:40:00Z"
        }
      }
    }
  ]
}
```

## Alabama adapter notes (to verify before Nov. 3)

- Source pages: `statewideResultsByContest.aspx?ecode=<code>`, `chooseCounty.aspx?ecode=<code>`, `countyResultsByContest.aspx?cid=<NN>&ecode=<code>` on `www2.alabamavotes.gov/electionNight/`. Each has an "Export Data" button (ASP.NET postback `hlnkExportData`).
- The November `ecode` is unknown until the state posts it. The Aug. 11 special primary (`ecode=1001300`) is the dress-rehearsal source.
- County ids (`cid`) are the state's alphabetical numbering, not FIPS. Chambers is probably `12`, unconfirmed. The adapter needs a `cid` to FIPS table.
- A county with no contests in a given election falls back to another county's page. Validate that the county name on the page matches the requested county.
- Not yet tested: whether AlabamaVotes.gov answers requests from GitHub-hosted runners.
- Not yet confirmed: whether "box" means precinct. The page copy is worded to hold either way.

## Page behavior at a glance

| Feed state | What the page shows |
|---|---|
| `DATA_URL` empty, or `status: "pre"` | Ballot names, "no votes yet", neutral map, "Polls close 7:00 PM Central". After 7 PM CT Nov. 3 with no results: "Polls have closed · Waiting for the first county reports". |
| `live` or `final` | Votes, percentages, who is ahead, boxes reported, per-row update times, colored map. |
| `live` and older than 30 minutes | Same, plus a "may be behind" notice linking to `source.url`. |
| Fetch fails, no earlier data | Ballot view plus "could not be loaded" notice. |
| Fetch fails, earlier data | Last good numbers plus a notice showing their time. |
| `?sample=1` | Built-in placeholder data through the same renderer, "Sample data" ribbon, `noindex`. |

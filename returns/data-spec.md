# Read the Returns — Data Spec (v1)

The contract between the **adapter** (fetches and normalizes Alabama's unofficial election-night results) and the **page** (`/returns/`). The page renders whatever this file describes; it never calls races.

## Where it lives

- Published as a single JSON file from the separate data repo (`Huguleyite/rtr-returns-data`) by a custom GitHub Actions workflow, about every 10 minutes on an off-minute cron (`3,13,23,33,43,53 * * * *`). Feed address: `https://huguleyite.github.io/rtr-returns-data/returns.json`.
- The page's `DATA_URL` constant (top of the script in `returns/index.html`) points at it. While `DATA_URL` is empty, or the feed returns 404, the page shows the pre-election ballot. Other failures (server errors, malformed data) show a "could not be loaded" notice and keep the last good numbers.
- The page appends a cache-busting `?t=<timestamp>` and re-fetches every 3 minutes while the tab is visible.

## Top level

| Field | Type | Notes |
|---|---|---|
| `schema` | `1` | Must be the number `1`, or the page ignores the file. |
| `status` | `"pre"` \| `"live"` \| `"final"` | `pre` = no results yet (page shows the ballot). `live` = counting. `final` = state reports all counties done; still unofficial until certified. |
| `generated_at` | ISO 8601 UTC string | When the adapter last ran successfully. Drives the "Updated" pill and the stale warning (over 30 minutes while `live`). |
| `source` | object, optional | `name` (string), `url` (https link to the state's page), `updated_at` (ISO, the state's own "Last Updated"). The Alabama adapter also carries `counties_reported`, `counties_total`, `ballots_cast`, `registered_voters`, `turnout_pct` from the state's statewide page; the page does not use them yet. |
| `contests` | array | See below. Order = display order for map chips and extra Chambers rows. |

## Contest

| Field | Type | Notes |
|---|---|---|
| `id` | string | Stable id. Roster ids the page knows: `gov`, `us-sen`, `us-house-3`, `al-senate-13`, `al-house-38`. Any other id (Lt. Gov., AG, SoS, PSC, amendments, county offices) is added automatically as an extra row on the Chambers card if it has Chambers numbers. |
| `title` | string | Display title. |
| `scope` | `"statewide"` \| `"district"` \| `"county"` | Optional. Map chips are shown for `statewide` contests; headings read "Statewide," "District total," or "County total." |
| `state_contest_code` | string | Optional. The state's own contest code, for tracing a row back to the export. Ignored by the page. |
| `candidates` | array of `{ id, name, party }` | `party` is `"D"`, `"R"`, other letters, or `""` (amendments, nonpartisan). Order = display order (Democrat, then Republican, then others, each by ballot number). `id` is unique inside the contest and is the key used in `votes`. If the state lists write-ins as a candidate, they pass through as a candidate with party `""`, so percentages match the state's. |
| `statewide` | object, optional | `votes` (`{candidateId: int}`) and `updated_at`. If present, used for statewide totals; otherwise the page sums `counties`. The Alabama adapter omits it, and its county sums match the state's own statewide page candidate for candidate (checked on the Aug. 11 data). |
| `counties` | object | Keys are 5-digit FIPS strings (Chambers = `"01017"`). Include only counties the state has posted for this contest. A contest with more than 3 counties becomes a map chip. |

## County entry (inside `counties`)

| Field | Type | Notes |
|---|---|---|
| `votes` | `{candidateId: int}` | Whole numbers. Omit write-ins or fold them out of the candidate list; percentages are of the listed candidates. |
| `boxes_pct` | number 0–100, optional | What Alabama publishes: "Boxes Reported" as a percentage, per county. |
| `boxes_reported`, `boxes_total` | int, optional | Used instead when a source gives counts. Shown as "14 of 20 boxes reported". |
| `updated_at` | ISO 8601 UTC string | The state's timestamp for that county if available, else the adapter's. Shown beside every figure. |

A county counts as "fully reporting" when `boxes_reported >= boxes_total`, or `boxes_pct >= 100`.

## Rules the adapter must follow

1. **No race calls.** No `winner`, `called`, or similar fields. The page shows votes and who is ahead.
2. **Unknown is omitted, not zero.** A county with no posted totals is left out of `counties`. If a county's boxes value cannot be fetched in one run, the previous run's value is reused.
3. **All numbers are integers** (votes, box counts) except `boxes_pct`.
4. **Keep the last good file.** If a fetch or parse fails, republish the previous JSON unchanged rather than partial or empty data. Its `generated_at` ages, so the page's stale warning covers the gap.
5. **Sanity checks before publishing:** every county key is a valid Alabama FIPS (`01001`–`01133`, odd numbers); a run whose total votes fall more than 5% below the previous run's is held back (override with the workflow's `allow_decrease` input for a real correction); smaller per-county drops are logged as warnings; a candidate number that names two different people is treated as bad data; `generated_at` is the run time.
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

## Alabama adapter notes (verified against the Aug. 11, 2026 special primary, ecode 1001300)

- **Three kinds of request per run, about 69 in all, roughly 4 seconds:** the statewide page (stats, "Last Updated", and the hidden form fields), the page's "Export Data" postback (`__EVENTTARGET=hlnkExportData`, returns `sosEnrExport.xlsx` with every county's votes for every contest in one long table), and one county page per county for "Boxes Reported" and that county's update time.
- **Export columns:** Election Code, Election Title, County Code, County Name, Contest Code, Contest Title, Candidate Number, Candidate Name, Votes, Party Code. Party codes seen: DEM, REP. The adapter refuses any other column layout.
- **County codes (`cid`)** are the state's numbering, not FIPS: Jefferson 01, Mobile 02, Montgomery 03, then alphabetical (St. Clair sorts after Shelby, the reverse of FIPS). All 40 counties in the Aug. 11 export matched the table in `adapter/counties.py`; Chambers is **12 / 01017**. The remaining 27 counties follow by elimination and get re-checked when November's export arrives.
- **Boxes:** the state publishes only a percentage per county (`lblPrecinctsReportedPercent`, labeled "Boxes Reported" on screen). The element's id says "precincts", which points toward box = precinct, but that is still unconfirmed.
- **Timestamps** are Central time and are converted to UTC.
- **Election code:** the November code is not known until the state posts it, and it cannot be guessed: an unpublished code shows either "Results Coming Soon" or "An Error Occurred". Set it as the `ECODE` repository variable in the data repo.
- **County fallback:** a county with no contests in an election gets another county's page, so the adapter checks the county name on the page and ignores a mismatch.
- **Not testable from here:** whether AlabamaVotes.gov answers GitHub-hosted runners. The container this was built in reached it without trouble; the first manual workflow run in the data repo answers it for GitHub.
- **Not confirmed:** exact November contest titles. The adapter matches leniently (U.S. vs state, Senate vs House, district number) and logs a warning listing the titles it saw if any of the five Chambers card contests is missing.

## Page behavior at a glance

| Feed state | What the page shows |
|---|---|
| `DATA_URL` empty, feed 404, or `status: "pre"` | Ballot names, "no votes yet", neutral map, "Polls close 7:00 p.m. local time" (7 p.m. Eastern in parts of Chambers County, 7 p.m. Central elsewhere; results expected after about 8 p.m. Eastern). After 7 PM CT Nov. 3 with no results: "Polls have closed · Waiting for the first county reports". |
| `live` or `final` | Votes, percentages, who is ahead, boxes reported, per-row update times, colored map. |
| `live` and older than 30 minutes | Same, plus the "Our live feed is paused" banner (numbers may be behind) linking to `source.url`, or to AlabamaVotes.gov if none. |
| Fetch fails, no earlier data | Ballot view plus "could not be loaded" notice. |
| Fetch fails, earlier data | Last good numbers plus a notice showing their time. |
| `?sample=1` | Built-in placeholder data through the same renderer, "Sample data" ribbon, `noindex`. |

# Collective Action in Tech — Data Visualization

A data visualization page for [Collective Action in Tech](https://collectiveaction.tech)'s documented reporting database. Every record in the database is one reported instance of collective action by workers in the tech industry.

## Data

`raw_data.csv` — the export from the archive. 232 records, 2014–2026. `build.py` aggregates it into `data.js`; re-run it whenever the CSV changes.

Fields the visualization uses:

| Column | Used for |
|---|---|
| `date` | year, for the per-year bars |
| `struggle_type` | per-year bars, events view (internal / external) |
| `workers` | per-year bars, workers view |
| `actions` | tag graph, actions view |
| `struggles` | tag graph, struggles view |
| `companies` | employer graph |
| everything else | not used yet |

## The visualization

Three graphs on one page. **Every graph is static** — each one shows all recorded observations at once. There is no year filter and no linked interaction between the graphs.

```
┌─────────────────────────────────────────────────┐
│  1 · Per year                                   │
│     (bars, full width, toggle events ⇄ workers) │
├──────────────────────────┬──────────────────────┤
│  2 · Tags                │  3 · Employers       │
│    (circles, toggle      │    (horizontal bars, │
│     actions ⇄ struggles) │     descending)      │
└──────────────────────────┴──────────────────────┘
```

### 1 · Per year — top, full width

One bar per year, 2014 → 2026. Years with no records still get a slot. A toggle switches between two views:

- **Events** — the number of records that year, stacked by `struggle_type`: internal, external, both (tagged `internal,external`), and unspecified (blank).
- **Workers** — the sum of `workers` across that year's records. Only records with a number count (`2500+` counts as 2500); `unknown`, `hundreds`, `thousands` and blanks are skipped. 165 of 232 records give a number.

### 2 · Tags — bottom left

Shows the distribution of `actions` and `struggles`. A toggle switches the view between the two; only one is shown at a time.

In either view, **every tag is a circle**:

- circle **size** = the number of observations carrying that tag
- circle **color** = distinct per tag

Layout reference: circle packing — circles of varying size packed inside a bounding shape, each labeled.

> **Note on totals:** the tag counts sum to more than the total number of observations, because a single observation can carry several actions or struggles. The circles show tag frequency, not a partition of the records.

### 3 · Employers — bottom right

A horizontal bar graph of observation counts per employer, sorted descending so the most-referenced employer sits at the top.

## Roadmap

- **Scrollytelling, year by year.** A separate narrative view that walks through the archive one year at a time.

## Data notes

Things worth knowing before reading anything into the graphs:

- **16 rows have `description` and `date` swapped.** `build.py` takes the date from whichever of the two columns holds one.
- **Dates come in two formats**, `M/D/YYYY` and `YYYY-MM-DD`; both are parsed.
- **`struggle_type` is blank for 29 records**, 28 of them from 2023 on, so the internal/external split thins out in recent years.
- **`workers` is dominated by a few large actions.** The 2014 bar is almost entirely one class-action suit (60,000 plaintiffs).
- **Tag typos are normalized in `build.py`:** `ai ethids` → `ai ethics`; `na` is dropped.
- **Company names are case-folded** (`Google` = `google`). Related names are *not* merged: `google` / `alphabet`, `facebook` / `meta` stay separate.
- **Some records name several employers** in one `companies` cell (e.g. `"google, alphabet"`), so employer counts sum to more than the record count.

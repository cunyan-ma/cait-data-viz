# Collective Action in Tech — Data Visualization

A data visualization page for [Collective Action in Tech](https://collectiveaction.tech)'s documented reporting database. Every record in the database is one reported instance of collective action by workers in the tech industry.

## Data

`Human-editing - for_download.csv` — the raw export from the archive. 488 records with usable dates, spanning 2015–2025.

Fields the visualization uses:

| Column | Used for |
|---|---|
| `published_date` | quarter, for the cumulative line |
| `issue_tags` | tag graph, issue view |
| `action_tags` | tag graph, action view |
| `company_coded` | employer graph |
| `location` | not used yet |
| `n_employees`, `summary` | not used yet |

## The visualization

Three graphs on one page. **Every graph is static** — each one shows all recorded observations at once. There is no year filter and no linked interaction between the graphs.

```
┌─────────────────────────────────────────────────┐
│  1 · Cumulative observations by quarter         │
│     (line graph, full width)                    │
├──────────────────────────┬──────────────────────┤
│  2 · Tags                │  3 · Employers       │
│    (circles, toggle      │    (horizontal bars, │
│     issue ⇄ action)      │     descending)      │
└──────────────────────────┴──────────────────────┘
```

### 1 · Cumulative observations by quarter — top, full width

A line graph running left to right across the full span of the archive, with one point per quarter.

The value at each quarter is the **running total of all observations recorded up to and including that quarter** — not that quarter's own count. So the line only ever rises or stays flat, ending at the total number of observations in the archive.

- x axis: quarters, 2015 Q1 → 2025 Q4 (44 quarters)
- y axis: cumulative observation count, 0 → 488
- Quarters with no observations still appear on the axis; the line runs flat across them rather than skipping them.

Reading the curve: a steep segment means many reports were recorded in a short window, a flat segment means few or none. No breakdown by tag and no legend for now.

### 2 · Tags — bottom left

Shows the distribution of `action_tag` and `issue_tag`. A toggle switches the view between the two; only one is shown at a time.

In either view, **every tag is a circle**:

- circle **size** = the number of observations carrying that tag
- circle **color** = distinct per tag

Layout reference: circle packing — circles of varying size packed inside a bounding shape, each labeled.

> **Note on totals:** the tag counts sum to more than the total number of observations, because a single observation can carry several tags. The 488 records produce 779 issue-tag assignments (211 records carry more than one). The circles show tag frequency, not a partition of the records.

### 3 · Employers — bottom right

A horizontal bar graph of observation counts per employer, sorted descending so the most-referenced employer sits at the top.

## Roadmap

- **Scrollytelling, year by year.** A separate narrative view that walks through the archive one year at a time.

## Data notes

Things worth knowing before reading anything into the graphs:

- **`action_tags` is sparse.** Only 38 of 488 records carry an action tag, and none after 2019. The action view of the tag graph reflects a small, time-limited slice of the archive, not the whole thing.
- **`issue_tags` is nearly complete.** 484 of 488 records tagged, 22 distinct tags.
- **`gov_filing` and `gov-filing` are the same tag** entered two ways, and need normalizing to avoid splitting one category in two.
- **The archive is concentrated on a few employers.** 70 distinct employers appear; Google accounts for 254 of the mentions.
- **Some records name several employers** in one `company_coded` cell (e.g. `"Google, Amazon"`), so employer counts also sum to more than the record count.
- **Recording is very uneven over time.** 5 of the 44 quarters have no observations at all, and 2018 Q2–Q4 alone accounts for 126 of the 488 records. On a cumulative line this shows up as a long flat start, a near-vertical rise through 2018, and a gradual taper after 2022.
- **The dates are publication dates, not event dates.** The line tracks when reporting entered the archive, which is not the same as when the organizing happened.

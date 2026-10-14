# Collective Action in Tech — Data Visualization

A data visualization page for [Collective Action in Tech](https://collectiveaction.tech)'s documented reporting database. Every record in the database is one reported instance of collective action by workers in the tech industry.

The data tells the story of tech workers organizing from political issues to labor problems.

## Data

`raw_data.csv` — the export from the archive. 232 records, 2014–2026. `build.py` aggregates it into `data.js`; re-run it whenever the CSV changes.

Fields the visualization uses:

| Column | Used for |
|---|---|
| `date` | timeline position (quarter) |
| `struggles` | each event's theme (timeline + employer colours), matrix columns |
| `actions` | matrix rows |
| `companies` | employer graph |
| everything else | not used yet |


### Theme

Every event gets one theme, derived from its `struggles` (always filled, unlike `struggle_type`):

- **ethics & politics** (green) — ethics, discrimination, political speech, government/military contracts, climate, racial/gender equity, AI ethics
- **workplace & labour** (red) — working conditions, pay and benefits, unfair labor practices, job security, retaliation, layoffs, wages, union activity, union busting
- **both / other** (grey) — struggles from both groups, or neither

The grouping is the `ETHICS` / `LABOUR` sets in `build.py`. Colours are `THEME` and `C` at the top of the script in `index.html`.

### 1 · Timeline — top, full width

Each dot is one event, stacked in its quarter's column (2014 Q1 → 2026). Column height is that quarter's count; labour dots sit at the bottom of each stack so the shift over time reads as a rising band. The five labelled moments are hand-written in `MOMENTS` in `index.html`.

### 2 · How workers act, by cause — bottom left

Rows are the six most common `actions`, columns the six most common `struggles` (ethics columns first). Each cell counts events tagged with both. Shading is by count, in the column's theme colour.

> **Note on totals:** an event with two actions and two struggles counts in four cells, so the matrix shows co-occurrence, not a partition of the records.

### 3 · Where — bottom right

Events per employer, top 10, each bar split by theme. `alphabet` is merged into `google` and `meta` into `facebook`; an event naming both counts once.

## Roadmap

- **Scrollytelling, year by year.** A separate narrative view that walks through the archive one year at a time.

## Data notes

Things worth knowing before reading anything into the graphs:

- **16 rows have `description` and `date` swapped.** `build.py` takes the date from whichever of the two columns holds one.
- **Dates come in two formats**, `M/D/YYYY` and `YYYY-MM-DD`; both are parsed.
- **Records from 2023 on were added in a later pass** (no old `id`) and are coded more sparsely: `struggle_type` and `online` are mostly blank. That's why theme comes from `struggles`.
- **`workers` is not visualized.** 27% of records have no number, missingness grows over time, and the values mix signatories, bargaining units and lawsuit plaintiffs.
- **Counts reflect archiving effort, not all organizing.** Fewer dots after 2022 likely means less documentation, not less activity. 2026 is a partial year.
- **Tag typos are normalized in `build.py`:** `ai ethids` → `ai ethics`; `na` is dropped.
- **Company names are case-folded** (`Google` = `google`).
- **Some records name several employers** in one `companies` cell (e.g. `"google, alphabet"`), so employer counts sum to more than the record count.

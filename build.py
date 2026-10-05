"""CSV -> data.js  (aggregates only; re-run whenever the CSV changes)"""
import csv, json, re, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(ROOT, 'raw_data.csv')
OUT  = os.path.join(ROOT, 'data.js')

DATE = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})$|^(\d{4})-(\d{2})-(\d{2})$')
ALIAS = {'ai ethids': 'ai ethics'}                  # typos in the source
DROP  = {'na', ''}

def iso(cell):
    m = DATE.match((cell or '').strip())
    if not m: return None
    if m.group(3): return f'{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}'
    return '-'.join(m.group(4, 5, 6))

def items(cell):
    out = []
    for t in (cell or '').split(','):
        t = ALIAS.get(t.strip().lower(), t.strip().lower())
        if t not in DROP and t not in out: out.append(t)
    return out

rows = []
for r in csv.DictReader(open(CSV, encoding='utf-8-sig')):
    # some rows have description and date swapped
    d = iso(r['date']) or iso(r['description'])
    if d: rows.append({**r, 'date': d})

# --- 1. per year: events by struggle_type, and workers involved ----------
def stype(r):
    s = set(items(r['struggle_type']))
    if s == {'internal', 'external'}: return 'both'
    if s in ({'internal'}, {'external'}): return s.pop()
    return 'unspecified'

def nworkers(cell):
    m = re.fullmatch(r'(\d[\d,]*)\+?', (cell or '').strip())
    return int(m.group(1).replace(',', '')) if m else None

TYPES = ['internal', 'external', 'both', 'unspecified']
y0, y1 = min(int(r['date'][:4]) for r in rows), max(int(r['date'][:4]) for r in rows)
years = {y: {'year': y, 'n': 0, **{t: 0 for t in TYPES}, 'workers': 0, 'counted': 0}
         for y in range(y0, y1 + 1)}
for r in rows:
    yr = years[int(r['date'][:4])]
    yr['n'] += 1
    yr[stype(r)] += 1
    w = nworkers(r['workers'])
    if w is not None:
        yr['workers'] += w
        yr['counted'] += 1

# --- 2. actions / struggles ----------------------------------------------
def tally(field):
    c = collections.Counter()
    for r in rows:
        for t in items(r[field]): c[t] += 1
    return [{'tag': t, 'n': n} for t, n in c.most_common()]

# --- 3. employers --------------------------------------------------------
emp, label = collections.Counter(), {}
for r in rows:
    for name in (x.strip() for x in (r['companies'] or '').split(',')):
        k = name.lower()
        if not name or k in ('unnamed', 'unknown', 'error'): continue
        emp[k] += 1
        if k not in label or name.islower(): label[k] = name   # prefer the lower-case spelling

data = {
    'years':     list(years.values()),
    'types':     TYPES,
    'actions':   tally('actions'),
    'struggles': tally('struggles'),
    'employers': [{'name': label[k], 'n': v} for k, v in emp.most_common()],
    'meta': {'total': len(rows), 'from': str(y0), 'to': str(y1)},
}
with open(OUT, 'w') as f:
    f.write('const DATA = ' + json.dumps(data, separators=(',', ':')) + ';\n')

print(f"{OUT}  {os.path.getsize(OUT)} bytes")
print(f"  {data['meta']['total']} records  {data['meta']['from']}-{data['meta']['to']}")
print(f"  types: " + ', '.join(f"{t} {sum(y[t] for y in years.values())}" for t in TYPES))
print(f"  workers: {sum(y['workers'] for y in years.values())} across "
      f"{sum(y['counted'] for y in years.values())} records with a count")
print(f"  {len(data['actions'])} actions, {len(data['struggles'])} struggles, {len(data['employers'])} employers")

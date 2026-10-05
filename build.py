"""CSV -> data.js  (aggregates only; re-run whenever the CSV changes)"""
import csv, json, re, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(ROOT, 'Human-editing - for_download.csv')
OUT  = os.path.join(ROOT, 'data.js')

def tags(cell):
    out = []
    for t in re.findall(r"[a-z][a-z_\-]+", (cell or '').lower()):
        t = t.replace('_', '-')                     # gov_filing == gov-filing
        if t in ('nan', 'issue-tags', 'action-tags') or t in out:
            continue
        out.append(t)
    return out

rows = [r for r in csv.DictReader(open(CSV))
        if re.match(r'^\d{4}-\d{2}-\d{2}$', (r['published_date'] or '').strip())]

# --- 1. cumulative observations by quarter -------------------------------
def qkey(d): return (int(d[:4]), (int(d[5:7]) - 1)//3 + 1)
per_q = collections.Counter(qkey(r['published_date'].strip()) for r in rows)
lo, hi = min(per_q), max(per_q)
span, y, q = [], *lo
while (y, q) <= hi:
    span.append((y, q))
    q += 1
    if q == 5: q, y = 1, y + 1
quarters, run = [], 0
for (y, q) in span:
    run += per_q[(y, q)]
    quarters.append({'label': f'{y} Q{q}',
                     'date': f'{y}-{3*(q-1)+1:02d}-01',
                     'n': per_q[(y, q)], 'cum': run})

# --- 2. tags -------------------------------------------------------------
def tally(field):
    c = collections.Counter()
    for r in rows:
        for t in tags(r[field]): c[t] += 1
    return [{'tag': t, 'n': n} for t, n in c.most_common()]

# --- 3. employers --------------------------------------------------------
emp = collections.Counter()
for r in rows:
    for name in (x.strip() for x in (r['company_coded'] or '').split(',')):
        if name and name.lower() not in ('unnamed', 'error', 'company-coded', 'company_coded'):
            emp[name] += 1

data = {
    'quarters':  quarters,
    'issues':    tally('issue_tags'),
    'actions':   tally('action_tags'),
    'employers': [{'name': n, 'n': v} for n, v in emp.most_common()],
    'meta': {'total': len(rows),
             'from': rows and min(r['published_date'] for r in rows)[:4],
             'to':   rows and max(r['published_date'] for r in rows)[:4]},
}
with open(OUT, 'w') as f:
    f.write('const DATA = ' + json.dumps(data, separators=(',', ':')) + ';\n')

print(f"{OUT}  {os.path.getsize(OUT)} bytes")
print(f"  {data['meta']['total']} records  {data['meta']['from']}-{data['meta']['to']}")
print(f"  {len(quarters)} quarters, cum ends at {quarters[-1]['cum']}")
print(f"  {len(data['issues'])} issue tags, {len(data['actions'])} action tags, {len(data['employers'])} employers")

"""CSV -> data.js  (aggregates only; re-run whenever the CSV changes)"""
import csv, json, re, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(ROOT, 'raw_data.csv')
OUT  = os.path.join(ROOT, 'data.js')

DATE = re.compile(r'^(\d{1,2})/(\d{1,2})/(\d{4})$|^(\d{4})-(\d{2})-(\d{2})$')
ALIAS = {'ai ethids': 'ai ethics'}                  # typos in the source
DROP  = {'na', ''}
ACTION_GROUP = {'union drive':          'union drive / representation',
                'union representation': 'union drive / representation'}

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
    if not d: continue
    # merged actions count once per event, even if it carried both originals
    acts = ','.join(ACTION_GROUP.get(a, a) for a in items(r['actions']))
    rows.append({**r, 'date': d, 'actions': acts})

# --- 1. actions / struggles ----------------------------------------------
def tally(field):
    c = collections.Counter()
    for r in rows:
        for t in items(r[field]): c[t] += 1
    return [{'tag': t, 'n': n} for t, n in c.most_common()]

# --- 2. theme ------------------------------------------------------------
# each event's theme, read from `struggles` (always filled, unlike struggle_type).
# this grouping is a judgement call — edit the two sets to change it.
ETHICS = {'ethics', 'discrimination', 'political speech', 'government contract',
          'military contract', 'climate', 'racial equity', 'gender equity', 'ai ethics'}
LABOUR = {'working conditions', 'pay and benefits', 'unfair labor practices', 'job security',
          'retaliation', 'layoffs', 'wages', 'union activity', 'union busting'}
EMP_GROUP = {'alphabet': 'google', 'meta': 'facebook'}
EMP_LABEL = {'google': 'google / alphabet', 'facebook': 'facebook / meta'}

def theme(r):
    s = set(items(r['struggles']))
    e, l = bool(s & ETHICS), bool(s & LABOUR)
    return 'both' if e and l else 'ethics' if e else 'labour' if l else 'other'

events = sorted([r['date'], theme(r)] for r in rows)

# --- 3. timeline, action x struggle matrix, employers -------------------
top_a = [d['tag'] for d in tally('actions')[:5]]
top_s = [d['tag'] for d in tally('struggles')[:6]]
top_s.sort(key=lambda s: s not in ETHICS)                  # ethics columns first, order kept
matrix = {'actions': top_a, 'struggles': top_s,
          'group': ['ethics' if s in ETHICS else 'labour' for s in top_s],
          'n': [[sum(1 for r in rows if a in items(r['actions']) and s in items(r['struggles']))
                 for s in top_s] for a in top_a]}

emp = collections.defaultdict(collections.Counter)
for r in rows:
    names = {EMP_GROUP.get(k, k) for k in (x.strip().lower() for x in (r['companies'] or '').split(','))
             if k and k not in ('unnamed', 'unknown', 'error')}
    for k in names: emp[k][theme(r)] += 1
employers = sorted(({'name': EMP_LABEL.get(k, k), 'n': sum(c.values()), **c}
                    for k, c in emp.items()), key=lambda d: -d['n'])

years = [int(r['date'][:4]) for r in rows]
data = {
    'events':    events,
    'matrix':    matrix,
    'employers': employers,
    'once':      sum(1 for d in employers if d['n'] == 1),
    'meta': {'total': len(rows), 'from': str(min(years)), 'to': str(max(years))},
}
with open(OUT, 'w') as f:
    f.write('const DATA = ' + json.dumps(data, separators=(',', ':')) + ';\n')

print(f"{OUT}  {os.path.getsize(OUT)} bytes")
print(f"  {data['meta']['total']} records  {data['meta']['from']}-{data['meta']['to']}")
print("  themes: " + ', '.join(f"{t} {n}" for t, n in collections.Counter(e[1] for e in events).most_common()))
print(f"  {len(employers)} employers, {data['once']} in only one event")

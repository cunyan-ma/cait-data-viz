import csv, json, re, sys, collections, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geo import state_paths, albers_usa
from places import PLACES, LOCMAP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, 'Human-editing - for_download.csv')
US_TOPO = os.path.join(ROOT, 'build', 'us-states-10m.json')

def tags(cell):
    out = []
    for t in re.findall(r"[a-z][a-z_\-]+", (cell or '').lower()):
        t = t.replace('_', '-')                       # gov_filing == gov-filing
        if t in ('nan', 'issue-tags', 'action-tags') or t in out:
            continue
        out.append(t)
    return out

records, unmapped = [], collections.Counter()
for r in csv.DictReader(open(CSV)):
    d = (r['published_date'] or '').strip()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', d):
        continue
    loc = (r['location'] or '').strip()
    if loc not in LOCMAP:
        unmapped[loc] += 1
    company = (r['company_coded'] or '').strip()
    companies = [c.strip() for c in company.split(',') if c.strip()] or ['unnamed']
    companies = [c for c in companies if c.lower() not in ('error', 'company_coded')]
    records.append({
        'y': int(d[:4]), 'd': d,
        'i': tags(r['issue_tags']), 'a': tags(r['action_tags']),
        'c': companies or ['unnamed'],
        'p': LOCMAP.get(loc, []), 'l': loc,
        's': (r['summary'] or '').strip()[:180],
    })

if unmapped:
    print('UNMAPPED LOCATIONS:', unmapped.most_common(), file=sys.stderr)

years = sorted({r['y'] for r in records})
places = {}
for k, (lat, lon, label, scope) in PLACES.items():
    x, y = albers_usa(lon, lat)
    entry = {'label': label, 'scope': scope}
    if scope in ('city', 'region'):
        entry['x'], entry['y'] = round(x, 1), round(y, 1)
    places[k] = entry

payload = {
    'years': years,
    'records': records,
    'places': places,
    'states': state_paths(US_TOPO),
    'meta': {
        'total': len(records),
        'issue_tagged': sum(1 for r in records if r['i']),
        'action_tagged': sum(1 for r in records if r['a']),
        'located': sum(1 for r in records if any(p != 'US' for p in r['p'])),
        'us_only': sum(1 for r in records if r['p'] == ['US']),
        'unplaced': sum(1 for r in records if not r['p']),
    },
}
out = os.path.join(ROOT, 'build', 'data.json')
json.dump(payload, open(out, 'w'), separators=(',', ':'))
print('wrote', out, os.path.getsize(out), 'bytes')
print(payload['meta'])

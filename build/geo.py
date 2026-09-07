import json, math

RAD = math.pi/180

def conic_equal_area(parallels, rotate_lon, center):
    p0, p1 = [p*RAD for p in parallels]
    sy0 = math.sin(p0)
    n = (sy0 + math.sin(p1))/2
    C = 1 + sy0*(2*n - sy0)
    r0 = math.sqrt(C)/n
    def raw(lam, phi):
        r = math.sqrt(C - 2*n*math.sin(phi))/n
        return (r*math.sin(lam*n), r0 - r*math.cos(lam*n))
    cx, cy = raw(center[0]*RAD, center[1]*RAD)
    def proj(lon, lat, k, tx, ty):
        x, y = raw((lon + rotate_lon)*RAD, lat*RAD)
        return (tx + k*(x-cx), ty - k*(y-cy))
    return proj

K, TX, TY = 1070.0, 480.0, 250.0
_lower48 = conic_equal_area([29.5, 45.5], 96, [-0.6, 38.7])
_alaska  = conic_equal_area([55, 65], 154, [-2, 58.5])
_hawaii  = conic_equal_area([8, 18], 157, [-3, 19.9])

def albers_usa(lon, lat):
    """Returns (x, y) in a 960x500 frame, or None if outside all three insets."""
    if 51 <= lat <= 72 and -172 <= lon <= -130:                       # Alaska
        return _alaska(lon, lat, K*0.35, TX - 0.307*K, TY + 0.201*K)
    if 18 <= lat <= 23 and -161 <= lon <= -154:                       # Hawaii
        return _hawaii(lon, lat, K, TX - 0.205*K, TY + 0.212*K)
    return _lower48(lon, lat, K, TX, TY)

def topo_rings(topo, obj_name):
    """Decode a quantized TopoJSON object into lon/lat rings."""
    sx, sy = topo['transform']['scale']
    dx, dy = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for px, py in arc:
            x += px; y += py
            pts.append((x*sx+dx, y*sy+dy))
        arcs.append(pts)
    def resolve(i):
        return list(reversed(arcs[~i])) if i < 0 else list(arcs[i])
    def ring(idxs):
        out = []
        for i in idxs:
            pts = resolve(i)
            out.extend(pts if not out else pts[1:])
        return out
    for g in topo['objects'][obj_name]['geometries']:
        polys = [g['arcs']] if g['type'] == 'Polygon' else g['arcs']
        yield g.get('properties', {}).get('name', '?'), [[ring(r) for r in p] for p in polys]

def simplify(pts, tol):
    """Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    keep = [False]*len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts)-1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx-ax, by-ay
        d2 = dx*dx + dy*dy
        best, bi = -1.0, -1
        for i in range(a+1, b):
            px, py = pts[i]
            if d2 == 0:
                dist = (px-ax)**2 + (py-ay)**2
            else:
                t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy)/d2))
                dist = (px-(ax+t*dx))**2 + (py-(ay+t*dy))**2
            if dist > best:
                best, bi = dist, i
        if best > tol*tol:
            keep[bi] = True
            stack.append((a, bi)); stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]

def state_paths(topo_path, tol=0.7):
    topo = json.load(open(topo_path))
    out = {}
    for name, polys in topo_rings(topo, 'states'):
        d = []
        for poly in polys:
            for ring in poly:
                proj = [albers_usa(lon, lat) for lon, lat in ring]
                proj = simplify(proj, tol)
                if len(proj) < 3:
                    continue
                d.append('M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in proj) + 'Z')
        if d:
            out[name] = ''.join(d)
    return out

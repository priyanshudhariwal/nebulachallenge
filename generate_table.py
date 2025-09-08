W, H = 8, 4  # mesh dimensions
N, E, S, WDIR, L = 0, 1, 2, 3, 4
# Assign shortcut ports
shortcut_ports = {
    (0, 31): 5,
    (7, 24): 6,
    (12, 20): 7,
    (4, 28): 8
}

def id2coord(i): return (i % W, i // W)

def xy_next_hop(src, dst):
    sx, sy = id2coord(src)
    dx, dy = id2coord(dst)
    if src == dst: return L
    if dx > sx: return E
    if dx < sx: return WDIR
    if dy > sy: return S
    return N

for s in range(W*H):
    row = []
    for d in range(W*H):
        # Check if shortcut applies
        assigned = False
        for (a, b), port in shortcut_ports.items():
            if (s == a and d == b) or (s == b and d == a):
                row.append(port)
                assigned = True
                break
        if not assigned:
            row.append(xy_next_hop(s, d))
    print(" ".join(map(str, row)))

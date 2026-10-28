# Writes partials/figures/swing-sweep.svg and -narrow.svg: one test swing run 45 ways, as the
# engine's sweep runs it (5 aims along the limb x 3 across, for bones a little weaker, as tuned,
# and a little stronger), with made-up results tallied against the study's "sometimes".
# The three blocks sit under three equal columns of HTML headings (.viz-heads), so their centres
# are at 1/6, 3/6 and 5/6 of the width. The middle block (bones as tuned) plays first, then the
# weaker and stronger blocks together, as the steps tell it.
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "partials", "figures")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


COLS, ROWS = 5, 3  # aims along the limb, aims across it
WEAKER, TUNED, STRONGER = 0, 1, 2


def broke(block, i, j):
    """Made-up results: a blow near the middle breaks the bone more often, weaker bones more."""
    d = abs(i - 2)
    if block == WEAKER:
        return d <= 1
    if block == TUNED:
        return (d <= 1 and j == 1) or d == 0
    return d <= 1 and j == 1 and i != 3


RUN0, RUN_STEP, PAUSE = 450, 45, 120  # first run, gap between runs, pause before step 2 (ms)


def build(name, cls, W, cell, gap, top, tally_y, tally_x0, tally_x1, badge_r, end_font_gap):
    bw = COLS * cell + (COLS - 1) * gap
    bh = ROWS * cell + (ROWS - 1) * gap
    centers = [W / 6, W / 2, 5 * W / 6]
    H = tally_y + 12 + end_font_gap + 6
    L = []
    a = L.append
    a(f'<svg class="{cls}" viewBox="0 0 {W} {f(H)}">')
    cells = {}
    for b, cx in enumerate(centers):
        bx = cx - bw / 2
        a(f'  <g class="fade" style="--at: {100 + b * 80}ms; --dur: 300ms">')
        for j in range(ROWS):
            for i in range(COLS):
                x, y = bx + i * (cell + gap), top + j * (cell + gap)
                cells[(b, i, j)] = (x, y)
                a(f'    <rect class="sw-slot" x="{f(x)}" y="{f(y)}" width="{f(cell)}" height="{f(cell)}" rx="3" />')
        a('  </g>')
    # When each run plays: the tuned block first, then the weaker and stronger blocks side by side.
    order = []
    for n, (j, i) in enumerate((j, i) for j in range(ROWS) for i in range(COLS)):
        order.append((RUN0 + n * RUN_STEP, TUNED, i, j))
    second = RUN0 + COLS * ROWS * RUN_STEP + PAUSE
    for n, (j, i) in enumerate((j, i) for j in range(ROWS) for i in range(COLS)):
        order.append((second + n * RUN_STEP, WEAKER, i, j))
        order.append((second + n * RUN_STEP, STRONGER, i, j))
    tally_steps = []
    for t, b, i, j in order:
        x, y = cells[(b, i, j)]
        if broke(b, i, j):
            c = cell
            crack = (f"M{f(x + c * 0.34)} {f(y + c * 0.16)}L{f(x + c * 0.56)} {f(y + c * 0.44)}"
                     f"L{f(x + c * 0.4)} {f(y + c * 0.58)}L{f(x + c * 0.66)} {f(y + c * 0.86)}")
            a(f'  <g class="pop" style="--at: {t}ms; --dur: 260ms">')
            a(f'    <rect class="sw-broke" x="{f(x)}" y="{f(y)}" width="{f(cell)}" height="{f(cell)}" rx="3" />')
            a(f'    <path class="sw-crack" d="{crack}" />')
            a('  </g>')
            tally_steps.append(t + 120)
        else:
            a(f'  <rect class="sw-held pop" x="{f(x)}" y="{f(y)}" width="{f(cell)}" height="{f(cell)}" rx="3" style="--at: {t}ms; --dur: 260ms" />')
    tally_steps.sort()
    last_run = max(t for t, *_ in order)
    # Along and across: arrows under and beside the block that plays first.
    tx0 = centers[TUNED] - bw / 2
    ay = top + bh + 7
    a('  <g class="fade" style="--at: 300ms; --dur: 300ms">')
    a(f'    <path class="sw-axis" d="M{f(tx0 + 3)} {f(ay)}H{f(tx0 + bw - 3)}M{f(tx0 + 7)} {f(ay - 3.5)}l-4 3.5 4 3.5M{f(tx0 + bw - 7)} {f(ay - 3.5)}l4 3.5-4 3.5" />')
    vx = tx0 - (centers[TUNED] - centers[WEAKER] - bw) / 2
    a(f'    <path class="sw-axis" d="M{f(vx)} {f(top + 3)}V{f(top + bh - 3)}M{f(vx - 3.5)} {f(top + 7)}l3.5-4 3.5 4M{f(vx - 3.5)} {f(top + bh - 7)}l3.5 4 3.5-4" />')
    a('  </g>')
    # The tally: one tick for each of the 45 runs; the breaks fill it from the left.
    span = tally_x1 - tally_x0
    tick = span / 45
    a('  <g class="fade" style="--at: 300ms; --dur: 300ms">')
    a(f'    <rect class="sw-track" x="{f(tally_x0)}" y="{f(tally_y)}" width="{f(span)}" height="12" rx="3" />')
    a('  </g>')
    for k, t in enumerate(tally_steps):
        a(f'  <rect class="sw-count fade" x="{f(tally_x0 + k * tick)}" y="{f(tally_y)}" width="{f(tick + 0.4)}" height="12" style="--at: {t}ms; --dur: 120ms" />')
    lab_y = tally_y + 12 + end_font_gap
    a('  <g class="fade" style="--at: 300ms; --dur: 300ms">')
    a(f'    <path class="sw-ticks" d="' + "".join(f"M{f(tally_x0 + k * tick)} {f(tally_y + 3)}v6" for k in range(1, 45)) + '" />')
    a(f'    <rect class="sw-track-edge" x="{f(tally_x0)}" y="{f(tally_y)}" width="{f(span)}" height="12" rx="3" />')
    a(f'    <text class="sw-end" x="{f(tally_x0)}" y="{f(lab_y)}">0</text>')
    a(f'    <text class="sw-end" x="{f(tally_x1)}" y="{f(lab_y)}">45</text>')
    a('  </g>')
    # What the study allows for "sometimes": in some runs, but not none and not all. The two ends,
    # outside the bracket, would fail.
    end = last_run + 380
    by = tally_y - 8
    bx0, bx1 = tally_x0 + tick, tally_x1 - tick
    a(f'  <path class="sw-band draw" d="M{f(bx0)} {f(by + 5)}V{f(by)}H{f(bx1)}V{f(by + 5)}" pathLength="1" style="--at: {end}ms; --dur: 450ms" />')
    for k, ex in enumerate((tally_x0 + tick * 0.5, tally_x1 - tick * 0.5)):
        q = 3.4 if cls == "narrow" else 2.6
        a(f'  <path class="sw-out pop" d="M{f(ex - q)} {f(by - 1 - q)}l{f(2 * q)} {f(2 * q)}m0-{f(2 * q)}-{f(2 * q)} {f(2 * q)}" style="--at: {end + 350 + k * 60}ms" />')
    # The count, and the verdict beside it.
    n = len(tally_steps)
    nx = tally_x0 + n * tick
    a(f'  <text class="sw-n fade" x="{f(nx)}" y="{f(lab_y)}" style="--at: {tally_steps[-1] + 100}ms">{n}</text>')
    a(f'  <path class="sw-n-tick fade" d="M{f(nx)} {f(tally_y + 12)}v4" style="--at: {tally_steps[-1] + 100}ms" />')
    cx, cy = nx + 22, lab_y - 4.5
    a(f'  <g class="pop" style="--at: {end + 500}ms">')
    a(f'    <circle class="at-ok" cx="{f(cx)}" cy="{f(cy)}" r="8.5" />')
    a(f'    <path class="at-ok-mark" d="m{f(cx - 3.6)} {f(cy)} 2.6 2.6 4.8-5.2" />')
    a('  </g>')
    a(f'  <circle class="fx-ping ping-once sw-ping" cx="{f(cx)}" cy="{f(cy)}" r="8.5" style="--at: {end + 550}ms" />')
    # Step badges: under the tuned block (its aims), under the weaker and stronger blocks, and
    # beside the tally (the comparison).
    under = ay + badge_r + 8
    badges = [(1, centers[TUNED], under, RUN0), (2, centers[WEAKER], under, second),
              (2, centers[STRONGER], under, second), (3, tally_x0 - badge_r - 9, tally_y + 6, end)]
    for k, (num, x, y, t) in enumerate(badges):
        a(f'  <g class="pop" style="--at: {t}ms"><circle class="fig-badge" cx="{f(x)}" cy="{f(y)}" r="{f(badge_r)}" /><text class="fig-num" x="{f(x)}" y="{f(y)}" dy=".36em">{num}</text></g>')
    a('</svg>')
    open(os.path.join(DIR, name), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", name, "breaks", n, "second block at", second, "bracket at", end, "ends", end + 550 + 900, "ms")


build("swing-sweep.svg", "wide", W=480, cell=24, gap=4, top=4, tally_y=160, tally_x0=64, tally_x1=416,
      badge_r=9.5, end_font_gap=16)
build("swing-sweep-narrow.svg", "narrow", W=300, cell=14.5, gap=3, top=4, tally_y=124, tally_x0=40,
      tally_x1=262, badge_r=10, end_font_gap=18)

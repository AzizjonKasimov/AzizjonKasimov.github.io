# Writes partials/figures/hourly-thresholds.svg and -narrow.svg: one made-up day of the anomaly
# detector's error, judged by one threshold for the whole day (top) and by 24 hourly thresholds
# (bottom). The same morning anomaly is missed by the first and flagged by the second.
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "partials", "figures")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# The usual error at each hour (made up): small at night, larger around midday.
E = [.05, .05, .05, .05, .06, .09, .15, .22, .30, .40, .52, .60, .64, .62, .55, .45, .34, .24, .16, .10, .07, .06, .05, .05]
THR = [e * 1.25 + .08 for e in E]          # one threshold per hour, a margin above the usual error
GLOBAL = max(THR) + .02                     # one line for the day must clear the busiest hour
A_HOUR, A_VAL = 7.5, .6                     # the morning anomaly: over its hour's line, under the day's


def smooth(points):
    """A Catmull-Rom curve through the points, as cubic Bezier segments."""
    d = f"M{f(points[0][0])} {f(points[0][1])}"
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d


def err_at(h):
    """The usual error at hour h, read off the hourly values."""
    i = min(max(int(h - .5), 0), 22)
    t = min(max(h - .5 - i, 0), 1)
    return E[i] + (E[i + 1] - E[i]) * t


def build(name, cls, W, x0, x1, bases, scale, axis_y, H, badge_x, badge_r, dot_r, sfx):
    X = lambda h: x0 + (x1 - x0) * h / 24
    L = []
    a = L.append
    a(f'<svg class="{cls}" viewBox="0 0 {W} {H}">')
    for p, base in enumerate(bases):
        Y = lambda v, b=base: b - v * scale
        top = Y(1.08)
        # The panel: its ground line, and light hour marks every 6 hours.
        a('  <g class="fade" style="--dur: 300ms">')
        a(f'    <path class="th-axis" d="M{f(x0)} {f(base)}H{f(x1)}" />')
        a(f'    <path class="th-grid" d="' + "".join(f"M{f(X(h))} {f(top)}V{f(base)}" for h in (6, 12, 18)) + '" />')
        a('  </g>')
        # The usual error: an area under a smooth curve through the hour centres.
        pts = [(X(0), Y(E[0]))] + [(X(h + .5), Y(E[h])) for h in range(24)] + [(X(24), Y(E[23]))]
        curve = smooth(pts)
        band_at, band_dur = (100, 800) if p == 0 else (2150, 600)
        a(f'  <g class="wipe" style="--at: {band_at}ms; --dur: {band_dur}ms">')
        a(f'    <path class="th-band" d="{curve}L{f(X(24))} {f(base)}L{f(X(0))} {f(base)}Z" />')
        a(f'    <path class="th-curve" d="{curve}" />')
        a('  </g>')
        ay = Y(A_VAL)
        stem_from = Y(err_at(A_HOUR))
        if p == 0:
            gy = Y(GLOBAL)
            a(f'  <path class="th-global wipe" d="M{f(x0)} {f(gy)}H{f(x1)}" style="--at: 950ms; --dur: 400ms" />')
            a(f'  <path class="th-stem th-stem-missed grow-up" d="M{f(X(A_HOUR))} {f(stem_from)}V{f(ay + dot_r)}" style="--at: 1450ms; --dur: 250ms" />')
            a(f'  <circle class="th-missed pop" cx="{f(X(A_HOUR))}" cy="{f(ay)}" r="{f(dot_r)}" style="--at: 1650ms" />')
            # A gap marker between the anomaly and the line it stayed under.
            a(f'  <path class="th-gap fade" d="M{f(X(A_HOUR))} {f(ay - dot_r - 3)}V{f(gy + 3)}" style="--at: 1750ms" />')
            badges = [(1, Y(.12), 150), (2, gy, 950)]
        else:
            steps = f"M{f(X(0))} {f(Y(THR[0]))}"
            for h in range(24):
                steps += f"H{f(X(h + 1))}"
                if h < 23:
                    steps += f"V{f(Y(THR[h + 1]))}"
            a(f'  <path class="th-global th-global-ref fade" d="M{f(x0)} {f(Y(GLOBAL))}H{f(x1)}" style="--at: 2150ms; --dur: 400ms" />')
            a(f'  <path class="th-steps wipe" d="{steps}" style="--at: 2400ms; --dur: 1000ms" />')
            a(f'  <path class="th-stem grow-up" d="M{f(X(A_HOUR))} {f(stem_from)}V{f(ay + dot_r)}" style="--at: 3450ms; --dur: 250ms" />')
            a(f'  <circle class="th-hit pop" cx="{f(X(A_HOUR))}" cy="{f(ay)}" r="{f(dot_r)}" style="--at: 3650ms" />')
            a(f'  <circle class="fx-ping th-ping ping-once" cx="{f(X(A_HOUR))}" cy="{f(ay)}" r="{f(dot_r + 1)}" style="--at: 3700ms" />')
            # The anomaly's own hour, lit: its line is the one it crosses.
            hy = Y(THR[int(A_HOUR)])
            a(f'  <path class="th-hour pop" d="M{f(X(int(A_HOUR)))} {f(hy)}H{f(X(int(A_HOUR) + 1))}" style="--at: 3400ms" />')
            badges = [(3, Y(THR[0]) - badge_r - 3, 2150)]
        for n, y, t in badges:
            a(f'  <g class="pop" style="--at: {t}ms"><circle class="fig-badge" cx="{f(badge_x)}" cy="{f(y)}" r="{f(badge_r)}" /><text class="fig-num" x="{f(badge_x)}" y="{f(y)}" dy=".36em">{n}</text></g>')
    a('  <g class="fade" style="--dur: 300ms">')
    for h in (0, 6, 12, 18, 24):
        a(f'    <text class="th-hours" x="{f(X(h))}" y="{f(axis_y)}">{h}</text>')
    a('  </g>')
    a('</svg>')
    open(os.path.join(DIR, name), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", name)


build("hourly-thresholds.svg", "wide", W=460, x0=44, x1=444, bases=(152, 318), scale=118,
      axis_y=342, H=350, badge_x=22, badge_r=9.5, dot_r=5.5, sfx="")
build("hourly-thresholds-narrow.svg", "narrow", W=300, x0=34, x1=290, bases=(128, 262), scale=94,
      axis_y=286, H=294, badge_x=14, badge_r=10.5, dot_r=6, sfx="-narrow")

# Writes partials/figures/resume-job.svg and resume-job-narrow.svg: a big job that fails partway
# and resumes from its last checkpoint. One generator for both, so their timing stays the same.
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "partials", "figures")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# Timing, ms. The first run saves seven batches, fails on the eighth and holds there for about a
# second; then the resumed run saves the last five.
SAVE_AT = [650 + 130 * i for i in range(7)] + [3200 + 130 * i for i in range(5)]
FLAG_AT = [t + 140 for t in SAVE_AT]
FAIL_AT = 1730
GONE_AT = 1830
BADGE3_AT = 2130
RESUME_AT = 2750
ARROW_AT = 2850
DONE_AT = 3950


def build(name, cls, vb_w, vb_h, x0, pitch, w, h, ay, by, icon_cx, icon_r, pen, pole, badge_r,
          badge_y, db_x, db_w, db_top, db_bottom, db_cap, label_xy, label_end, check_r, clip_id,
          corner, db_mark_x, db_mark_r, db_flag_x, db_flag_left):
    xs = [x0 + pitch * i for i in range(12)]
    gap = pitch - w
    cps = [x + w + gap / 2 for x in xs]
    cy_a, cy_b = ay + h / 2, by + h / 2
    cx8 = xs[7] + w / 2
    rx_db = db_w / 2
    body = (f"M{f(db_x)} {f(db_top)}c0-{f(db_cap * 0.55)} {f(rx_db * 0.45)}-{f(db_cap)} {f(rx_db)}-{f(db_cap)}"
            f"s{f(rx_db)} {f(db_cap * 0.45)} {f(rx_db)} {f(db_cap)}v{f(db_bottom - db_top)}"
            f"c0 {f(db_cap * 0.55)}-{f(rx_db * 0.45)} {f(db_cap)}-{f(rx_db)} {f(db_cap)}"
            f"s-{f(rx_db)}-{f(db_cap * 0.45)}-{f(rx_db)}-{f(db_cap)}z")
    rim = (f"M{f(db_x)} {f(db_top)}c0 {f(db_cap * 0.55)} {f(rx_db * 0.45)} {f(db_cap)} {f(rx_db)} {f(db_cap)}"
           f"s{f(rx_db)}-{f(db_cap * 0.45)} {f(rx_db)}-{f(db_cap)}")
    fill_bottom = db_bottom + db_cap
    step = (fill_bottom - db_top) / 12
    rnd = 4 if cls == "wide" else 3

    def flag(x, y_base, scale=1.0):
        p, q = pen * scale, pole * scale
        # The pennant points back over the batch the checkpoint closes.
        return f"M{f(x)} {f(y_base - 1)}V{f(y_base - q)}l-{f(p)} {f(p * 0.42)} {f(p)} {f(p * 0.42)}"

    L = []
    a = L.append
    a(f'<svg class="{cls}" viewBox="0 0 {vb_w} {vb_h}">')
    a('  <defs>')
    a(f'    <clipPath id="{clip_id}"><path d="{body}" /></clipPath>')
    a('  </defs>')
    a('  <g class="pop" style="--at: 0ms">')
    a(f'    <circle class="art-panel" cx="{f(icon_cx)}" cy="{f(cy_a)}" r="{f(icon_r)}" />')
    k = icon_r * 0.55
    a(f'    <path class="art-accent-line" d="M{f(icon_cx)} {f(cy_a - k)}v{f(k)}l{f(k * 0.7)} {f(k * 0.42)}" />')
    a('  </g>')
    a('  <g class="fade" style="--at: 150ms">')
    for x in xs[:8]:
        a(f'    <rect class="rj-slot" x="{f(x)}" y="{f(ay)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" />')
    a(f'    <g class="fx-gone dim" style="--at: {GONE_AT}ms; --dur: 300ms">')
    for x in xs[8:]:
        a(f'      <rect class="rj-slot" x="{f(x)}" y="{f(ay)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" />')
    a('    </g>')
    a('  </g>')
    a('  <g class="fade" style="--at: 150ms">')
    a(f'    <path class="art-panel" d="{body}" />')
    lx, ly = label_xy
    a(f'    <text{" class=\"rj-db-name\"" if label_end else ""} x="{f(lx)}" y="{f(ly)}">PostgreSQL</text>')
    a('  </g>')
    # What the database holds: one level per saved batch, the first run's seven below the line
    # where it stopped, the resumed run's five above it.
    a(f'  <g clip-path="url(#{clip_id})">')
    for i in range(12):
        y = fill_bottom - step * (i + 1)
        hh = step + 0.5
        if i == 11:
            y, hh = db_top - db_cap - 2, fill_bottom - step * 11 - (db_top - db_cap - 2) + 0.5
        a(f'    <rect class="rj-level fade" x="{f(db_x - 2)}" y="{f(y)}" width="{f(db_w + 4)}" height="{f(hh)}" style="--at: {FLAG_AT[i]}ms" />')
    seps = "".join(f"M{f(db_x)} {f(fill_bottom - step * (i + 1))}h{f(db_w)}" for i in range(11) if i != 6)
    a(f'    <path class="rj-level-sep fade" d="{seps}" style="--at: {FLAG_AT[11]}ms" />')
    a(f'    <path class="rj-stop draw" d="M{f(db_x)} {f(fill_bottom - step * 7)}h{f(db_w)}" pathLength="1" style="--at: {FAIL_AT + 50}ms; --dur: 250ms" />')
    a('  </g>')
    a('  <g class="fade" style="--at: 150ms">')
    a(f'    <path class="rj-db-edge" d="{body}" />')
    a(f'    <path class="rj-db-edge" d="{rim}" />')
    a('  </g>')
    split = fill_bottom - step * 7
    mx, mr = db_mark_x, db_mark_r
    # The first run's part: the scheduled run's clock beside it.
    a(f'  <g class="pop" style="--at: {FLAG_AT[0]}ms">')
    a(f'    <circle class="art-panel" cx="{f(mx)}" cy="{f((fill_bottom + split) / 2)}" r="{f(mr)}" />')
    kk = mr * 0.55
    cyl = (fill_bottom + split) / 2
    a(f'    <path class="art-accent-line rj-mini" d="M{f(mx)} {f(cyl - kk)}v{f(kk)}l{f(kk * 0.7)} {f(kk * 0.42)}" />')
    a('  </g>')
    # The resumed run's part: the play mark beside it.
    cyu = (split + db_top) / 2
    tt = mr * 0.45
    a(f'  <g class="pop" style="--at: {FLAG_AT[7]}ms">')
    a(f'    <circle class="art-panel" cx="{f(mx)}" cy="{f(cyu)}" r="{f(mr)}" />')
    a(f'    <path class="rj-play" d="M{f(mx - tt * 0.75)} {f(cyu - tt)}v{f(2 * tt)}l{f(tt * 1.65)}-{f(tt)}z" />')
    a('  </g>')
    # The checkpoint, kept in the database: a flag on the line where the first run stopped.
    fx = db_flag_x
    fp = pen * 0.75
    sign = -1 if db_flag_left else 1
    a(f'  <path class="rj-flag pop" d="M{f(fx)} {f(split)}V{f(split - pole * 0.62)}l{f(sign * fp)} {f(fp * 0.42)} {f(-sign * fp)} {f(fp * 0.42)}" style="--at: {FAIL_AT + 80}ms" />')
    for i in range(7):
        a(f'  <rect class="rj-saved wipe" x="{f(xs[i])}" y="{f(ay)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" style="--at: {SAVE_AT[i]}ms; --dur: 140ms" />')
    a(f'  <g class="fx-gone dim" style="--at: {FAIL_AT}ms; --dur: 150ms">')
    a(f'    <rect class="rj-saved wipe" x="{f(xs[7])}" y="{f(ay)}" width="{f(w * 0.58)}" height="{f(h)}" rx="{rnd}" style="--at: {FAIL_AT - 150}ms; --dur: 150ms" />')
    a('  </g>')
    a(f'  <rect class="rj-fail pop" x="{f(xs[7])}" y="{f(ay)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" style="--at: {FAIL_AT}ms" />')
    xh = w * 0.24
    a(f'  <path class="rj-x pop" d="M{f(cx8 - xh)} {f(cy_a - xh)}l{f(2 * xh)} {f(2 * xh)}m0-{f(2 * xh)}-{f(2 * xh)} {f(2 * xh)}" style="--at: {FAIL_AT + 50}ms" />')
    for i in range(7):
        a(f'  <path class="rj-flag pop" d="{flag(cps[i], ay, 1.4 if i == 6 else 1.0)}" style="--at: {FLAG_AT[i]}ms" />')
    a(f'  <g class="fade" style="--at: {RESUME_AT}ms; --dur: 300ms">')
    a(f'    <rect class="rj-skip" x="{f(xs[0])}" y="{f(by)}" width="{f(xs[6] + w - xs[0])}" height="{f(h)}" rx="{rnd}" />')
    for x in xs[7:]:
        a(f'    <rect class="rj-slot" x="{f(x)}" y="{f(by)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" />')
    a('  </g>')
    a(f'  <g class="pop" style="--at: {RESUME_AT}ms">')
    a(f'    <circle class="art-panel" cx="{f(icon_cx)}" cy="{f(cy_b)}" r="{f(icon_r)}" />')
    t = icon_r * 0.45
    a(f'    <path class="rj-play" d="M{f(icon_cx - t * 0.75)} {f(cy_b - t)}v{f(2 * t)}l{f(t * 1.65)}-{f(t)}z" />')
    a('  </g>')
    y0, y1 = ay + h + 4, by - 3
    ax = cps[6]
    a(f'  <path class="rj-resume draw" d="M{f(ax)} {f(y0)}V{f(y1)}" pathLength="1" style="--at: {ARROW_AT}ms; --dur: 300ms" />')
    ah = 4 if cls == "narrow" else 5
    a(f'  <path class="rj-resume pop" d="M{f(ax - ah)} {f(y1 - ah)}l{ah} {ah} {ah}-{ah}" style="--at: {ARROW_AT + 260}ms" />')
    for j, i in enumerate(range(7, 12)):
        a(f'  <rect class="rj-saved wipe" x="{f(xs[i])}" y="{f(by)}" width="{f(w)}" height="{f(h)}" rx="{rnd}" style="--at: {SAVE_AT[7 + j]}ms; --dur: 140ms" />')
    for j, i in enumerate(range(7, 12)):
        a(f'  <path class="rj-flag pop" d="{flag(cps[i], by)}" style="--at: {FLAG_AT[7 + j]}ms" />')
    cx_c, cy_c = corner
    a(f'  <g class="pop" style="--at: {DONE_AT}ms">')
    a(f'    <circle class="art-accent" cx="{f(cx_c)}" cy="{f(cy_c)}" r="{f(check_r)}" />')
    c = check_r * 0.42
    a(f'    <path class="art-check" d="m{f(cx_c - c)} {f(cy_c)} {f(c * 0.75)} {f(c * 0.75)} {f(c * 1.3)}-{f(c * 1.45)}" />')
    a('  </g>')
    badges = [(1, xs[0] + pitch / 2 + w / 2, ay + h + badge_r + 7, 150),
              (2, (xs[1] + xs[6]) / 2 + w / 2, badge_y, FLAG_AT[0]),
              (3, xs[7] + w + 12 + badge_r, cy_a, BADGE3_AT), (4, cps[6] + badge_r + 9, (y0 + y1) / 2, ARROW_AT + 100)]
    for n, x, y, t in badges:
        a(f'  <g class="pop" style="--at: {t}ms"><circle class="fig-badge" cx="{f(x)}" cy="{f(y)}" r="{f(badge_r)}" /><text class="fig-num" x="{f(x)}" y="{f(y)}" dy=".36em">{n}</text></g>')
    a('</svg>')
    open(os.path.join(DIR, name), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", name)


# Desktop and tablet: the database to the right of the rows.
build("resume-job.svg", "wide", vb_w=470, vb_h=276, x0=52, pitch=27, w=24, h=36, ay=74, by=214,
      icon_cx=24, icon_r=13, pen=10, pole=20, badge_r=9.5, badge_y=26, db_x=410, db_w=48,
      db_top=124, db_bottom=212, db_cap=7, label_xy=(434, 238), label_end=False, check_r=9,
      clip_id="rj-db-clip", corner=(434, 108), db_mark_x=389, db_mark_r=8.5, db_flag_x=410,
      db_flag_left=True)
# Phones: the database under the rows, its name to its left.
build("resume-job-narrow.svg", "narrow", vb_w=284, vb_h=262, x0=29.5, pitch=20.8, w=18, h=30, ay=46,
      by=148, icon_cx=11.5, icon_r=9.5, pen=7, pole=15, badge_r=10.5, badge_y=15, db_x=210, db_w=44,
      db_top=208, db_bottom=250, db_cap=5.5, label_xy=(188, 236), label_end=True, check_r=8.5,
      clip_id="rj-db-clip-narrow", corner=(232, 199), db_mark_x=270, db_mark_r=8, db_flag_x=210,
      db_flag_left=True)

# Writes partials/figures/agent-turn.svg and agent-turn-narrow.svg: one agent turn of Network App
# as a sequence diagram. Lanes: the phone (with its database), the gateway, Claude; time runs down.
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "partials", "figures")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


# Icon shapes from partials/icons (24px grid).
ICONS = {
    "phone": '<rect x="6" y="2" width="12" height="20" rx="2.5" /><path d="M11 18h2" />',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" /><path d="m9 12 2 2 4-4" />',
    "sparkle": '<path d="M12 3 13.9 8.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z" />',
    "message": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /><path d="M8 9h8" /><path d="M8 13h5" />',
    "undo": '<path d="M9 14 4 9l5-5" /><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11" />',
    "db": '<ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" />',
}

# Story timing, ms. Each call: when its line starts drawing; the checks pop as it passes them.
T = {
    "msg": 250, "b1": 150,
    "b2": 750, "call1": 800, "res1": 1200,
    "b3": 1600, "call2": 1650, "err": 2450, "call3": 2850, "res3": 3250,
    "b4": 3600, "reply": 3650,
}
DRAW = 300


def build(name, cls, W, lanes, box_w, rows, H, icon_r, check_r, badge_x, badge_r, sfx):
    P, G, C = lanes
    L = []
    a = L.append
    a(f'<svg class="{cls}" viewBox="0 0 {W} {H}">')
    a('  <defs>')
    for k, body in ICONS.items():
        a(f'    <symbol id="at-{k}{sfx}" viewBox="0 0 24 24">{body}</symbol>')
    a('  </defs>')
    # The phone, holding its database: a lane of its own.
    a(f'  <rect class="at-phone fade" x="{f(P - box_w / 2)}" y="2" width="{f(box_w)}" height="{f(H - 4)}" rx="16" style="--dur: 400ms" />')
    top = 22 + icon_r + 6
    db_y = top + 8
    lane_top_phone = db_y + icon_r * 1.8 + 6
    a('  <g class="fade" style="--dur: 400ms">')
    a(f'    <path class="at-lane" d="M{f(G)} {f(top)}V{f(H - 10)}M{f(C)} {f(top)}V{f(H - 10)}M{f(P)} {f(lane_top_phone)}V{f(H - 10)}" />')
    a('  </g>')
    for i, (x, icon) in enumerate(((P, "phone"), (G, "shield"), (C, "sparkle"))):
        s = icon_r * 1.2
        a(f'  <g class="pop" style="--at: {i * 70}ms">')
        a(f'    <circle class="art-panel" cx="{f(x)}" cy="22" r="{f(icon_r)}" />')
        a(f'    <use class="at-icon" href="#at-{icon}{sfx}" x="{f(x - s / 2)}" y="{f(22 - s / 2)}" width="{f(s)}" height="{f(s)}" />')
        a('  </g>')
    # The phone's database, in a white circle like the other icons, locked: it stays on the phone.
    dr = icon_r * 0.9
    dcy = db_y + dr - 2
    a('  <g class="fade" style="--at: 150ms">')
    a(f'    <circle class="art-panel" cx="{f(P)}" cy="{f(dcy)}" r="{f(dr)}" />')
    ds = dr * 1.15
    a(f'    <use class="at-icon" href="#at-db{sfx}" x="{f(P - ds / 2)}" y="{f(dcy - ds / 2)}" width="{f(ds)}" height="{f(ds)}" />')
    lx, ly = P + dr * 0.72, dcy + dr * 0.72
    a(f'    <circle class="at-lock-bg" cx="{f(lx)}" cy="{f(ly)}" r="7" />')
    a(f'    <path class="at-lock" d="M{f(lx - 3)} {f(ly - 0.5)}h6v4h-6zM{f(lx - 1.8)} {f(ly - 0.5)}v-1.5a1.8 1.8 0 0 1 3.6 0v1.5" />')
    a('  </g>')
    dw, dh, dx, dy = dr * 2, dr * 2, P - dr, dcy - dr
    a(f'  <circle class="fx-ping ping-once" cx="{f(P)}" cy="{f(dcy)}" r="{f(dr + 1)}" style="--at: {T["call1"] + DRAW + 60}ms" />')
    a(f'  <circle class="fx-ping ping-once" cx="{f(P)}" cy="{f(dcy)}" r="{f(dr + 1)}" style="--at: {T["call3"] + DRAW + 60}ms" />')

    gap = check_r + 3  # where a line stops short of a check mark on the phone's lane

    def right(y, cls_line, start, t, head=True, from_x=None):
        x0 = from_x if from_x is not None else P + 2
        x1 = C - 4
        if cls_line == "at-call":
            a(f'  <path class="{cls_line} draw" d="M{f(x0)} {f(y)}H{f(x1)}" pathLength="1" style="--at: {t}ms; --dur: {DRAW}ms" />')
        else:
            a(f'  <path class="{cls_line} wipe" d="M{f(x0)} {f(y)}H{f(x1)}" style="--at: {t}ms; --dur: {DRAW}ms" />')
        if head:
            a(f'  <path class="{cls_line}-head pop" d="M{f(x1 - 5)} {f(y - 4.5)}l5 4.5-5 4.5" style="--at: {t + DRAW - 40}ms" />')

    def left(y, cls_line, t, end_x):
        x0 = C - 2
        a(f'  <path class="{cls_line} draw" d="M{f(x0)} {f(y)}H{f(end_x)}" pathLength="1" style="--at: {t}ms; --dur: {DRAW}ms" />')
        a(f'  <path class="{cls_line}-head pop" d="M{f(end_x + 5)} {f(y - 4.5)}l-5 4.5 5 4.5" style="--at: {t + DRAW - 40}ms" />')

    def schema(x, y, t):
        r = check_r
        w = r * 3.6
        a(f'  <g class="pop" style="--at: {t}ms">')
        a(f'    <rect class="at-ok" x="{f(x - w / 2)}" y="{f(y - r)}" width="{f(w)}" height="{f(2 * r)}" rx="{f(r)}" />')
        b = r * 0.55
        a(f'    <path class="at-brace" d="M{f(x - w / 2 + r * 0.95)} {f(y - b)}q-{f(r * 0.3)} 0-{f(r * 0.3)} {f(b * 0.45)}v{f(b * 0.25)}q0 {f(b * 0.3)}-{f(r * 0.28)} {f(b * 0.3)}q{f(r * 0.28)} 0 {f(r * 0.28)} {f(b * 0.3)}v{f(b * 0.25)}q0 {f(b * 0.45)} {f(r * 0.3)} {f(b * 0.45)}'
          f'M{f(x + w / 2 - r * 0.95)} {f(y - b)}q{f(r * 0.3)} 0 {f(r * 0.3)} {f(b * 0.45)}v{f(b * 0.25)}q0 {f(b * 0.3)} {f(r * 0.28)} {f(b * 0.3)}q-{f(r * 0.28)} 0-{f(r * 0.28)} {f(b * 0.3)}v{f(b * 0.25)}q0 {f(b * 0.45)}-{f(r * 0.3)} {f(b * 0.45)}" />')
        a(f'    <path class="at-ok-mark" d="m{f(x - r * 0.42)} {f(y)} {f(r * 0.3)} {f(r * 0.3)} {f(r * 0.55)}-{f(r * 0.6)}" />')
        a('  </g>')

    def check(x, y, ok, t):
        kind = "at-ok" if ok else "at-no"
        r = check_r
        a(f'  <g class="pop" style="--at: {t}ms">')
        a(f'    <circle class="{kind}" cx="{f(x)}" cy="{f(y)}" r="{f(r)}" />')
        if ok:
            a(f'    <path class="{kind}-mark" d="m{f(x - r * 0.42)} {f(y)} {f(r * 0.3)} {f(r * 0.3)} {f(r * 0.55)}-{f(r * 0.6)}" />')
        else:
            q = r * 0.34
            a(f'    <path class="{kind}-mark" d="M{f(x - q)} {f(y - q)}l{f(2 * q)} {f(2 * q)}m0-{f(2 * q)}-{f(2 * q)} {f(2 * q)}" />')
        a('  </g>')

    r1, r2, r2b, r3, r3b, r3c, r3d, r4 = rows
    # 1. My message goes out, through the gateway, to Claude.
    mr = icon_r * 0.72
    a(f'  <g class="pop" style="--at: {T["msg"] - 100}ms">')
    a(f'    <circle class="art-panel" cx="{f(P)}" cy="{f(r1)}" r="{f(mr)}" />')
    a(f'    <use class="at-icon" href="#at-message{sfx}" x="{f(P - mr * 0.6)}" y="{f(r1 - mr * 0.6)}" width="{f(mr * 1.2)}" height="{f(mr * 1.2)}" />')
    a('  </g>')
    right(r1, "at-call", None, T["msg"], from_x=P + mr + 3)
    # 2. A tool call: checked by the gateway, then by the phone; only its result goes back.
    left(r2, "at-call", T["call1"], P + gap)
    schema(G, r2, T["call1"] + DRAW // 2)
    check(P, r2, True, T["call1"] + DRAW + 20)
    right(r2b, "at-result", None, T["res1"])
    # 3. A call the phone refuses; the error goes back, and the corrected call is saved.
    left(r3, "at-call", T["call2"], P + gap)
    schema(G, r3, T["call2"] + DRAW // 2)
    check(P, r3, False, T["call2"] + DRAW + 20)
    right(r3b, "at-error", None, T["err"])
    left(r3c, "at-call", T["call3"], P + gap)
    schema(G, r3c, T["call3"] + DRAW // 2)
    check(P, r3c, True, T["call3"] + DRAW + 20)
    right(r3d, "at-result", None, T["res3"])
    # 4. The reply: every change listed, with one Undo.
    cw, ch = box_w - 18, 26
    left(r4, "at-call", T["reply"], P + cw / 2 + 2)
    cx0 = P - cw / 2
    a(f'  <g class="pop" style="--at: {T["reply"] + DRAW + 40}ms">')
    a(f'    <rect class="at-card" x="{f(cx0)}" y="{f(r4 - ch / 2)}" width="{f(cw)}" height="{f(ch)}" rx="6" />')
    a(f'    <path class="at-card-line" d="M{f(cx0 + 7)} {f(r4 - 4)}h{f(cw * 0.42)}M{f(cx0 + 7)} {f(r4 + 4)}h{f(cw * 0.3)}" />')
    us = 13
    a(f'    <use class="at-undo" href="#at-undo{sfx}" x="{f(cx0 + cw - us - 5)}" y="{f(r4 - us / 2)}" width="{us}" height="{us}" />')
    a('  </g>')
    for n, y, t in ((1, r1, T["b1"]), (2, r2, T["b2"]), (3, r3, T["b3"]), (4, r4, T["b4"])):
        a(f'  <g class="pop" style="--at: {t}ms"><circle class="fig-badge" cx="{f(badge_x)}" cy="{f(y)}" r="{f(badge_r)}" /><text class="fig-num" x="{f(badge_x)}" y="{f(y)}" dy=".36em">{n}</text></g>')
    a('</svg>')
    open(os.path.join(DIR, name), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", name)


build("agent-turn.svg", "wide", W=420, lanes=(70, 210, 350), box_w=92,
      rows=(126, 174, 204, 254, 284, 330, 360, 406), H=432, icon_r=17, check_r=8.5,
      badge_x=398, badge_r=9.5, sfx="")
build("agent-turn-narrow.svg", "narrow", W=300, lanes=(50, 150, 250), box_w=78,
      rows=(122, 170, 200, 250, 280, 326, 356, 402), H=428, icon_r=16, check_r=9,
      badge_x=286, badge_r=10, sfx="-narrow")

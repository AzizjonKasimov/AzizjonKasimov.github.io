# Writes partials/figures/receipt-match.svg and -narrow.svg: a made-up day of Coupang charges on
# the bank statement (top) and Coupang order emails (bottom). A receipt counts only when its total
# equals the charge and it was sent within two hours of it.
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "partials", "figures")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def hm(h, m):
    return h + m / 60


MINUS = "\u2212"
# Made-up day. Charges: (time, amount). Emails: (time, total).
THIN = "\u2009"  # groups the thousands in every language; a comma is a decimal sign in some
C1, C3 = (hm(12, 0), f"12{THIN}800"), (hm(17, 30), f"12{THIN}800")
EX = (hm(10, 50), f"8{THIN}900")      # inside the first charge's window, but another total
E1, E3 = (hm(12, 0), f"12{THIN}800"), (hm(17, 30), f"12{THIN}800")

# Story timing, ms.
T = {"rows": 150, "mails": 450, "b1": 150, "total": 1000, "b2": 1000, "window": 1900, "far": 2150,
     "b3": 1900, "match": 2700, "b4": 3300, "names": 3350}


def build(name, cls, W, H, t0, t1, x0, x1, top_y, mail_y, axis_y, badge_r, sfx, low_line, glyph):
    X = lambda t: x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    L = []
    a = L.append
    a(f'<svg class="{cls}" viewBox="0 0 {W} {H}">')
    a('  <defs>')
    a(f'    <symbol id="rm-mail{sfx}" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></symbol>')
    a(f'    <symbol id="rm-row{sfx}" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18" /><path d="M3 15h18" /><path d="M9 9v12" /></symbol>')
    a(f'    <symbol id="rm-spark{sfx}" viewBox="0 0 24 24"><path d="M12 3 13.9 8.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z" /></symbol>')
    a('  </defs>')
    # Two hours either side of each charge.
    band_top, band_bot = top_y - 17 - 12 - 8, axis_y
    for i, (t, _) in enumerate((C1, C3)):
        a(f'  <rect class="rm-window fade" x="{f(X(t - 2))}" y="{f(band_top)}" width="{f(X(t + 2) - X(t - 2))}" height="{f(band_bot - band_top)}" rx="6" style="--at: {T["window"] + i * 120}ms; --dur: 400ms" />')
    # The tracks and the time axis.
    a('  <g class="fade" style="--dur: 300ms">')
    a(f'    <path class="rm-track" d="M{f(x0)} {f(top_y)}H{f(x1)}M{f(x0)} {f(mail_y)}H{f(x1)}" />')
    a(f'    <path class="rm-axis" d="M{f(x0)} {f(axis_y)}H{f(x1)}" />')
    ticks = [h for h in range(int(t0) + 1, int(t1)) if h % 2 == 0]
    a(f'    <path class="rm-axis" d="' + "".join(f"M{f(X(h))} {f(axis_y - 3)}v6" for h in ticks) + '" />')
    for h in ticks:
        a(f'    <text class="rm-hour" x="{f(X(h))}" y="{f(axis_y + 18)}">{h}:00</text>')
    a('  </g>')
    gw = gh = glyph
    def glyph(kind, t, y, at, extra=""):
        a(f'  <g class="pop" style="--at: {at}ms">')
        a(f'    <rect class="rm-glyph-bg" x="{f(X(t) - gw / 2)}" y="{f(y - gh / 2)}" width="{gw}" height="{f(gh)}" rx="3" />')
        a(f'    <use class="rm-{kind}{extra}" href="#rm-{kind}{sfx}" x="{f(X(t) - gw / 2)}" y="{f(y - gh / 2)}" width="{gw}" height="{f(gh)}" />')
        a('  </g>')
    def label(t, y, text, at, cls_extra=""):
        a(f'  <text class="rm-amount{cls_extra} fade" x="{f(X(t))}" y="{f(y)}" style="--at: {at}ms">{text}</text>')
    # Charges on the statement, amounts above; order emails below, totals under them.
    for i, (t, amt) in enumerate((C1, C3)):
        glyph("row", t, top_y, T["rows"] + i * 90)
        label(t, top_y - 17, MINUS + amt, T["rows"] + i * 90 + 100)
    for i, (t, amt) in enumerate((EX, E1, E3)):
        glyph("mail", t, mail_y, T["mails"] + i * 90, " rm-mail-off" if (t, amt) == EX else "")
        if (t, amt) == EX and low_line:
            a(f'  <text class="rm-amount rm-amount-off rm-start fade" x="{f(X(C1[0] - 2) + 5)}" y="{f(mail_y + 26 + low_line)}" style="--at: {T["mails"] + 100}ms">{amt}</text>')
        elif (t, amt) == EX:
            label(t, mail_y + 26, amt, T["mails"] + i * 90 + 100, " rm-amount-off")
        else:
            label(t, mail_y + 26, amt, T["mails"] + i * 90 + 100)

    def link(ta, tb, kind, at, mark_t=0.5):
        xa, ya = X(ta), top_y + gh / 2 + 2
        xb, yb = X(tb), mail_y - gh / 2 - 2
        cls_line = "rm-match" if kind == "ok" else "rm-nomatch"
        a(f'  <path class="{cls_line} draw" d="M{f(xa)} {f(ya)}L{f(xb)} {f(yb)}" pathLength="1" style="--at: {at}ms; --dur: 300ms" />')
        mx, my = xa + (xb - xa) * mark_t, ya + (yb - ya) * mark_t
        r = 8
        a(f'  <g class="pop" style="--at: {at + 280}ms">')
        if kind == "ok":
            a(f'    <circle class="at-ok" cx="{f(mx)}" cy="{f(my)}" r="{r}" />')
            a(f'    <path class="at-ok-mark" d="m{f(mx - 3.4)} {f(my)} 2.4 2.4 4.4-4.8" />')
        else:
            a(f'    <circle class="at-no" cx="{f(mx)}" cy="{f(my)}" r="{r}" />')
            a(f'    <path class="at-no-mark" d="M{f(mx - 2.7)} {f(my - 2.7)}l5.4 5.4m0-5.4-5.4 5.4" />')
        a('  </g>')
        return mx, my

    # 2. Same total? The email near the first charge cost something else.
    ex_x, ex_y = link(C1[0], EX[0], "no", T["total"], 0.68)
    # 3. Within two hours? The later email has the same total but is hours away.
    far_x, far_y = link(C1[0], E3[0], "no", T["far"], (14.75 - C1[0]) / (E3[0] - C1[0]))
    # The two matches.
    link(C1[0], E1[0], "ok", T["match"])
    link(C3[0], E3[0], "ok", T["match"] + 150)
    # 4. The matched email's product names go up to the charge, and the AI can label it.
    for i, (t, _) in enumerate((C1, C3)):
        xa, xb = X(t), X(t)
        a(f'  <path class="fx-dot" d="M{f(xb)} {f(mail_y - gh / 2 - 2)}L{f(xa)} {f(band_top - 13 + 9)}" pathLength="100" style="--at: {T["names"] + i * 150}ms; --dur: 600ms" />')
        sx, sy = X(t), band_top - 13
        a(f'  <g class="pop" style="--at: {T["names"] + 520 + i * 150}ms">')
        a(f'    <circle class="art-panel" cx="{f(sx)}" cy="{f(sy)}" r="8.5" />')
        a(f'    <use class="rm-spark" href="#rm-spark{sfx}" x="{f(sx - 6)}" y="{f(sy - 6)}" width="12" height="12" />')
        a('  </g>')
    # Step badges, each beside what its step is about.
    bx = x0 - badge_r - 4
    badges = [(1, bx, top_y, T["b1"]),
              (2, bx, ex_y, T["b2"]),
              (3, far_x, far_y - 8 - badge_r - 6, T["b3"]),
              (4, X(C3[0]) + 8.5 + badge_r + 6, band_top - 13, T["b4"])]
    for n, x, y, t in badges:
        a(f'  <g class="pop" style="--at: {t}ms"><circle class="fig-badge" cx="{f(x)}" cy="{f(y)}" r="{f(badge_r)}" /><text class="fig-num" x="{f(x)}" y="{f(y)}" dy=".36em">{n}</text></g>')
    a('</svg>')
    open(os.path.join(DIR, name), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("wrote", name)


build("receipt-match.svg", "wide", W=460, H=330, t0=9.4, t1=20.1, x0=40, x1=448, top_y=86,
      mail_y=238, axis_y=296, badge_r=9.5, sfx="", low_line=0, glyph=26)
build("receipt-match-narrow.svg", "narrow", W=300, H=316, t0=9.4, t1=20.1, x0=26, x1=292, top_y=80,
      mail_y=220, axis_y=282, badge_r=10, sfx="-narrow", low_line=16, glyph=22)

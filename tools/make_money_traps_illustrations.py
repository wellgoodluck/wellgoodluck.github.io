#!/usr/bin/env python3
"""Generate the Money Traps (Nov 9) and Money Basics (Nov 12) illustrations as SVG files in articles/illustrations/. Not run by the workflows:
run it by hand after changing a figure here (python3 tools/make_money_traps_illustrations.py), then upload the SVGs.
Every color comes from the classes in assets/site.css's illustration block (the companion colors for identity only); nothing here sets a color.
viewBox width is 360; text never smaller than 12.5 units."""
import html, math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join("articles", "illustrations")
os.makedirs(OUT, exist_ok=True)
W = 360


def esc(s):
    return html.escape(str(s), quote=True)


# Spanish versions (Nov 9 pilot): with LANG = "es", T() and write() swap each English string for its entry in ES
# (keys are the strings exactly as the English drawing passes them) and write <name>-es.svg. A string with no entry
# stays English, so check the output. Spanish runs longer: the Spanish runs may pass wider boxes (see SPANISH below).
LANG = "en"
ES = {}


def T(x, y, s, cls="", anchor="start", extra=""):
    if LANG == "es":
        s = ES.get(s, s)
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    c = f' class="{cls}"' if cls else ""
    return f'<text x="{x:g}" y="{y:g}"{a}{c}{extra}>{s}</text>'


def tx(s):
    return esc(s)


def R(x, y, w, h, cls, rx=0, extra=""):
    r = f' rx="{rx:g}"' if rx else ""
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"{r} class="{cls}"{extra}/>'


def L(x1, y1, x2, y2, cls):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{cls}"/>'


def P(d, cls, extra=""):
    return f'<path d="{d}" class="{cls}"{extra}/>'


def tag(x, y, w, h, label, cls="ink-fill", tcls="xs rev", anchor="middle"):
    """An inverted label: ink box, sheet-colored text (the pressed-button look)."""
    tx_ = x + w / 2 if anchor == "middle" else x + 6
    return R(x, y, w, h, cls, rx=3) + T(tx_, y + h / 2 + 4.5, tx(label), tcls, anchor)


def fictional(x, y, anchor="end"):
    return T(x, y, "FICTIONAL · FOR ILLUSTRATION", "cap", anchor)


def write(name, h, body, title, desc):
    if LANG == "es":
        name, title, desc = name + "-es", ES.get(title, title), ES.get(desc, desc)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h:g}" role="img" '
           f'aria-labelledby="{name}-t {name}-d">'
           f'<title id="{name}-t">{esc(title)}</title><desc id="{name}-d">{esc(desc)}</desc>\n'
           + "\n".join(body) + "\n</svg>\n")
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name, h)


def money(v, cents=True):
    s = f"{abs(v):,.2f}" if cents else f"{abs(v):,.0f}"
    return ("−$" if v < 0 else "$") + s


# ---------------------------------------------------------------- 0. credit score factors
def credit_score_factors():
    b = []
    b.append(T(0, 16, "What goes into a FICO score", "h"))
    b.append(T(0, 36, "Approximate weights, out of 100%", "s i2"))
    parts = [(35, "Paying on time"), (30, "How much of your limits you use"), (15, "How long you've had credit"),
             (10, "New applications"), (10, "Mix of credit types")]
    x, y0, bw, bh = 0, 50, W, 34
    fills = ["teal-fill", "c1-fill", "c2-fill", "c3-fill", "c4-fill"]
    for i, (p, lab) in enumerate(parts):
        w = bw * p / 100
        b.append(R(x, y0, w - 2 if i < 4 else w, bh, fills[i], rx=3))
        x += w
    y = y0 + bh + 26
    for i, (p, lab) in enumerate(parts):
        b.append(R(0, y - 11, 12, 12, fills[i], rx=2))
        b.append(T(20, y, f"{p}%", "m", "start"))
        b.append(T(62, y, tx(lab)))
        y += 24
        if i < 4:
            b.append(L(0, y - 16, W, y - 16, "rule"))
    y += 6
    b.append(R(0.5, y, W - 1, 60, "well", rx=6))
    b.append(T(14, y + 24, "NOT IN THE SCORE", "cap"))
    b.append(T(14, y + 46, "Income · job · savings · checking balance", "s"))
    h = y + 61
    write("credit-score-factors", h, b, "What goes into a FICO score",
          "A bar split into five parts: paying on time 35%, how much of your limits you use 30%, how long you've had "
          "credit 15%, new applications 10%, and the mix of credit types 10%. Not in the score: income, job, savings "
          "or checking balance.")


# ---------------------------------------------------------------- 1a. overdraft statement
def overdraft_statement():
    b = []
    rows = [("Starting balance", None, 20.00, False), ("Lunch", -18.00, 2.00, False), ("Coffee", -6.00, -4.00, False),
            ("FEE", -35.00, -39.00, True), ("Movie rental", -9.00, -48.00, False), ("FEE", -35.00, -83.00, True),
            ("Gas", -30.00, -113.00, False), ("FEE", -35.00, -148.00, True)]
    top = 88
    rh = 31
    h_sheet = top + rh * len(rows) + 70
    b.append(R(0.5, 0.5, W - 1, h_sheet, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Checking activity, Tuesday", "h"))
    b.append(T(14, 72, "ITEM", "cap"))
    ax = 244 if LANG == "en" else 268          # the Spanish fee label is wider, so the amounts move right
    b.append(T(ax, 72, "AMOUNT", "cap", "end"))
    b.append(T(W - 14, 72, "BALANCE", "cap", "end"))
    b.append(L(14, 80, W - 14, 80, "rule"))
    y = top
    for lab, amt, bal, fee in rows:
        cy = y + rh / 2 + 5
        if fee:
            b.append(tag(14, y + 6, 108 if LANG == "en" else 164, 20, "OVERDRAFT FEE"))
            b.append(T(ax, cy, money(amt), "b", "end"))
            b.append(T(W - 14, cy, money(bal), "b", "end"))
        else:
            b.append(T(14, cy, tx(lab), "i2" if amt is None else ""))
            if amt is not None:
                b.append(T(ax, cy, money(amt), "", "end"))
            b.append(T(W - 14, cy, money(bal), "", "end"))
        y += rh
        b.append(L(14, y, W - 14, y, "rule"))
    b.append(L(14, y, W - 14, y, "ink-line"))
    b.append(T(14, y + 26, "You owe the bank", "m"))
    b.append(T(W - 14, y + 30, "$148.00", "big", "end"))
    b.append(T(14, y + 50, "$43 you didn't have, plus $105 in fees", "s i2"))
    # the callout under the sheet
    yy = h_sheet + 26
    b.append(T(0, yy, "The first fee was for being $4 short.", "s"))
    b.append(T(0, yy + 20, "Each fee is the same, whatever the amount.", "s i2"))
    write("overdraft-statement", yy + 26, b, "A fictional day of checking activity with three overdraft fees",
          "Starting balance $20. Lunch $18 leaves $2. Coffee $6 leaves minus $4, and a $35 overdraft fee makes it "
          "minus $39. A $9 movie rental makes it minus $48, and another $35 fee minus $83. Gas $30 makes it minus $113, "
          "and a third $35 fee minus $148. You owe the bank $148: the $43 you didn't have, plus $105 in fees. The first "
          "fee was for being $4 short.")


# ---------------------------------------------------------------- 1b. overdraft opt-in switch
def overdraft_optin():
    b = []
    h = 270
    b.append(R(0.5, 0.5, W - 1, h - 1, "sheet", rx=6))
    b.append(T(14, 26, "Settings", "h"))
    b.append(fictional(W - 14, 26))
    b.append(L(14, 38, W - 14, 38, "rule"))
    b.append(T(14, 64, "Overdraft coverage for debit card", "m"))
    b.append(T(14, 84, "and ATM transactions", "m"))
    # switch, off
    sx, sy = W - 14 - 52, 58
    b.append(R(sx, sy, 52, 28, "range-fill", rx=14))
    b.append(f'<circle cx="{sx + 14:g}" cy="{sy + 14:g}" r="11" class="sheet"/>')
    b.append(T(sx + 38, sy + 19, "Off", "xs m", "middle"))
    b.append(L(14, 104, W - 14, 104, "rule"))
    b.append(tag(14, 118, 40, 20, "OFF"))
    b.append(T(64, 133, "Not enough money? The purchase", "s"))
    b.append(T(64, 151, "is declined. No fee.", "s b"))
    b.append(R(14, 168, 40, 20, "frame", rx=3))
    b.append(T(34, 182.5, "ON", "xs m", "middle"))
    b.append(T(64, 183, "The bank may pay it and charge an", "s i2"))
    b.append(T(64, 201, "overdraft fee, often $35.", "s i2"))
    b.append(T(14, 232, "Checks and automatic bill payments aren't", "xs i2"))
    b.append(T(14, 249, "covered by this switch.", "xs i2"))
    write("overdraft-opt-in", h, b, "A fictional bank-app setting for overdraft coverage, switched off",
          "A settings screen with the switch for overdraft coverage on debit card and ATM transactions turned off. "
          "Off: if there isn't enough money, the purchase is declined, with no fee. On: the bank may pay it and charge "
          "an overdraft fee, often $35. Checks and automatic bill payments aren't covered by this switch.")


# ---------------------------------------------------------------- 2a. minimum payment warning box
def card_minimum_box():
    b = []
    h = 388
    b.append(R(0.5, 0.5, W - 1, 304, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Card statement", "h"))
    b.append(L(14, 56, W - 14, 56, "rule"))
    for i, (k, v) in enumerate([("New balance", "$2,000.00"), ("Minimum payment due", "$57.27"),
                                ("Interest rate (APR)", "22.36%")]):
        yy = 78 + i * 22
        b.append(T(14, yy, k, "s i2"))
        b.append(T(W - 14, yy, v, "s m", "end"))
    # the warning box
    bx, by, bw = 14, 136, W - 28
    b.append(R(bx, by, bw, 156, "frame", rx=3))
    b.append(T(bx + 10, by + 20, "Minimum Payment Warning", "s b"))
    b.append(T(bx + 10, by + 38, "Paying only the minimum costs more in interest", "xs i2"))
    b.append(T(bx + 10, by + 54, "and takes longer.", "xs i2"))
    cols = [bx + 10, bx + 140, bx + bw - 10]
    b.append(T(cols[0], by + 80, "IF YOU PAY", "cap"))
    b.append(T(cols[1], by + 80, "PAID OFF IN", "cap"))
    b.append(T(cols[2], by + 80, "TOTAL PAID", "cap", "end"))
    b.append(L(bx + 10, by + 88, bx + bw - 10, by + 88, "rule"))
    b.append(T(cols[0], by + 108, "Only the minimum", "s"))
    b.append(R(cols[1] - 6, by + 93, 78, 22, "wash", rx=3))
    b.append(T(cols[1], by + 108, "12 years", "s b"))
    b.append(T(cols[2], by + 108, "$4,651", "s b", "end"))
    b.append(L(bx + 10, by + 118, bx + bw - 10, by + 118, "rule"))
    b.append(T(cols[0], by + 138, "$77 a month", "s"))
    b.append(T(cols[1], by + 138, "3 years", "s"))
    b.append(T(cols[2], by + 138, "$2,763", "s", "end"))
    b.append(T(cols[2], by + 152, "(saves $1,888)", "xs i2", "end"))
    # callout
    b.append(P(f"M{cols[1] + 30} {by + 116} L{cols[1] + 30} {h - 62}", "lead"))
    b.append(T(0, h - 46, "Federal law has required this box since 2010.", "s"))
    b.append(T(0, h - 26, "It rounds to the nearest year; the exact figure is", "s i2"))
    b.append(T(0, h - 8, "11 years, 8 months.", "s i2"))
    write("card-minimum-box", h, b, "A fictional credit card statement with its minimum payment warning",
          "A statement for a $2,000 balance at 22.36% with a $57.27 minimum payment. The minimum payment warning box "
          "says that paying only the minimum, it will be paid off in 12 years at a total of $4,651. Paying $77 a "
          "month, it will be paid off in 3 years at a total of $2,763, saving $1,888. Federal law has required this "
          "box since 2010; it rounds to the nearest year, and the exact figure is 11 years, 8 months.")


# ---------------------------------------------------------------- 2b. three ways to pay (bars)
def card_three_ways():
    b = []
    rows = [("Only the minimum", "11 yrs 8 mo", 2651), ("$100 a month", "26 months", 526), ("$200 a month", "12 months", 234)]
    b.append(T(0, 16, "Interest paid on $2,000 at 22.36%", "h"))
    b.append(T(0, 36, "No new charges; same card, three ways to pay", "s i2"))
    y = 56
    maxw = W - 70
    for lab, when, v in rows:
        b.append(T(0, y + 4, lab, "m"))
        b.append(T(W, y + 4, when, "s i2", "end"))
        w = maxw * v / 2651
        b.append(R(0, y + 12, w, 18, "teal-fill", rx=2))
        b.append(T(w + 6, y + 26, f"${v:,}" if v != 2651 else "$2,651", "s b"))
        y += 58
    write("card-three-ways", y - 10, b, "Interest paid on $2,000 at 22.36%, three ways",
          "Paying only the minimum: about $2,651 in interest over 11 years and 8 months. Paying $100 a month: about "
          "$526 over 26 months. Paying $200 a month: about $234 over 12 months.")


# ---------------------------------------------------------------- 3. BNPL calendar
def bnpl_calendar():
    b = []
    plans = {"H": ("Hoodie", 22.50), "P": ("Headphones", 60.00), "S": ("Sneakers", 45.00), "T": ("Tickets", 15.00)}
    edge = {"H": "c1-edge", "P": "c2-edge", "S": "c3-edge", "T": "c4-edge"}
    bought = {1: "H", 3: "P", 4: "S", 6: "T"}           # day of the month each was bought (Mon = 1)
    due = {}
    for d, k in bought.items():
        for n in range(4):
            due.setdefault(d + 14 * n, []).append(k)
    paydays = {5, 19}
    cw, ch = 43, 50
    gx, gy = 0, 62
    b.append(T(0, 16, "Four plans, one month", "h"))
    b.append(T(0, 36, "Each pays a quarter now and every two weeks after.", "s i2"))
    days = "MTWTFSS"
    for i, d in enumerate(days):
        b.append(T(gx + i * cw + cw / 2, gy - 8, d, "cap", "middle"))
    b.append(T(W, gy - 8, "WEEK", "cap", "end"))
    for wk in range(4):
        tot = 0
        for i in range(7):
            day = wk * 7 + i + 1
            x, y = gx + i * cw, gy + wk * ch
            b.append(R(x + 0.5, y + 0.5, cw - 1, ch - 1, "sheet"))
            b.append(T(x + 5, y + 15, str(day), "xs i2"))
            if day in paydays:
                b.append(T(x + 5, y + 40, "PAY", "xs b"))
            ks = due.get(day, [])
            for j, k in enumerate(ks):
                amt = plans[k][1]
                lab = f"{amt:g}" if amt != 22.5 else "22.50"
                b.append(R(x + 3, y + 22 + j * 22, cw - 6, 19, edge[k], rx=3))
                b.append(T(x + cw / 2, y + 22 + j * 22 + 14, lab, "xs b", "middle"))
                tot += amt
        tx_ = gx + 7 * cw + 6
        ty = gy + wk * ch + ch / 2 + 5
        b.append(T(W, ty, f"${tot:,.2f}" if tot else "$0", "s b" if tot else "s mu", "end"))
    y = gy + 4 * ch + 26
    b.append(T(0, y, "Bought on the 1st, 3rd, 4th and 6th. PAY = payday.", "xs i2"))
    b.append(T(0, y + 20, "Week 3: all four are due, three of them before payday.", "s m"))
    legend = " · ".join(f"{v[0]} ${v[1]:.2f}".replace(".00", "") for v in plans.values())
    ly = y + 44
    for i, (k, (name, amt)) in enumerate(plans.items()):
        lx = (i % 2) * 180
        yy = ly + (i // 2) * 22
        b.append(R(lx, yy - 12, 16, 14, edge[k], rx=3))
        b.append(T(lx + 24, yy, f"{name}: ${amt:.2f}".replace(".00", "") + " each", "xs"))
    write("bnpl-calendar", ly + 30, b, "A month of four buy now, pay later plans",
          "A calendar of four weeks. Four pay-in-4 plans were started on the 1st, 3rd, 4th and 6th: a hoodie ($22.50 "
          "a payment), headphones ($60), sneakers ($45) and concert tickets ($15). Week 1 holds the four first "
          "payments, $142.50. Week 2 nothing. Week 3 all four are due again, on the 15th, 17th, 18th and 20th, $142.50, "
          "three of them before the payday on the 19th. Week 4 nothing.")


# ---------------------------------------------------------------- 4a. payday treadmill
def payday_treadmill():
    b = []
    b.append(T(0, 16, "A $300 payday loan, rolled over", "h"))
    b.append(T(0, 36, "$15 per $100, due every two weeks", "s i2"))
    y = 56
    rh = 52
    bw = 150
    for i in range(5):
        last = i == 4
        b.append(T(0, y + 20, f"Weeks {2 * i + 1}–{2 * i + 2}", "s m"))
        bx = 92
        if last:
            b.append(R(bx, y + 6, bw, 22, "teal-fill", rx=2))
            b.append(T(bx + bw / 2, y + 21.5, "$300 paid back", "xs rev", "middle"))
        else:
            b.append(R(bx + 0.5, y + 6.5, bw - 1, 21, "frame", rx=2))
            b.append(T(bx + bw / 2, y + 21.5, "$300 still owed", "xs i2", "middle"))
        b.append(tag(bx + bw + 8, y + 7, 54, 20, "$45 fee"))
        b.append(T(W, y + 21.5, f"${45 * (i + 1)}", "s b", "end"))
        if i < 4:
            b.append(L(0, y + rh - 8, W, y + rh - 8, "rule"))
        y += rh
    b.append(T(W, 50, "FEES SO FAR", "cap", "end"))
    b.append(L(0, y - 4, W, y - 4, "ink-line"))
    b.append(T(0, y + 18, "Ten weeks, $225 in fees, to borrow $300.", "s m"))
    write("payday-treadmill", y + 24, b, "A $300 payday loan rolled over four times",
          "Five two-week periods. In each of the first four you pay a $45 fee and still owe the $300. In the fifth "
          "you pay the $45 fee and the $300. Fees so far: $45, $90, $135, $180, $225. Ten weeks, $225 in fees, "
          "to borrow $300.")


# ---------------------------------------------------------------- 5. cash advance timelines
def cash_advance_timelines():
    b = []
    x0, x1 = 12, W - 12
    def X(day):
        return x0 + (x1 - x0) * day / 60
    b.append(T(0, 16, "The same $500, two ways, over 60 days", "h"))
    # purchase
    y = 76
    b.append(T(0, y - 32, "AS A PURCHASE, PAID IN FULL", "cap"))
    b.append(R(X(0), y, X(55) - X(0), 14, "wash"))
    b.append(L(X(0), y + 7, X(60), y + 7, "ink-line"))
    for d, lab in [(0, "Buy"), (30, "Statement"), (55, "Paid")]:
        b.append(L(X(d), y - 2, X(d), y + 16, "ink-line"))
        b.append(T(X(d), y + 32, lab, "xs i2", "middle" if d not in (0,) else "start"))
    b.append(T(X(27), y - 8, "grace period: no interest", "xs teal", "middle"))
    b.append(T(W, y + 54, "Cost: $0", "m", "end"))
    # advance
    y = 196
    b.append(T(0, y - 40, "AS A CASH ADVANCE", "cap"))
    # interest wedge growing from day 0
    b.append(f'<defs><pattern id="ca-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch-line"/></pattern></defs>')
    b.append(P(f"M{X(0)} {y + 7} L{X(60)} {y - 9} L{X(60)} {y + 7} Z", "", ' fill="url(#ca-hatch)"'))
    b.append(L(X(0), y + 7, X(60), y + 7, "ink-line"))
    b.append(L(X(0), y - 2, X(0), y + 16, "ink-line"))
    b.append(L(X(60), y - 2, X(60), y + 16, "ink-line"))
    b.append(tag(X(0), y + 22, 104, 20, "$25 fee, day 1"))
    b.append(T(X(60), y + 37, "Paid", "xs i2", "end"))
    b.append(T(X(30), y - 16, "interest from day 1", "xs i2", "middle"))
    b.append(T(W, y + 62, "Cost: about $50", "m", "end"))
    b.append(T(0, y + 62, "5% fee + 29.99% APR", "xs i2"))
    write("cash-advance-timelines", y + 70, b, "A $500 purchase versus a $500 cash advance over 60 days",
          "Two timelines of 60 days. As a purchase paid in full by the due date, the grace period means no interest: "
          "cost $0. As a cash advance, a $25 fee is charged on day 1 and interest at 29.99% builds from day 1: cost "
          "about $50 when it is paid back on day 60.")


# ---------------------------------------------------------------- 6a. car loan balances
def car_balances():
    def pmt(P, r, n):
        r = r / 12
        return P * r / (1 - (1 + r) ** -n)
    def bals(n):
        p = pmt(35000, 0.069, n); rr = 0.069 / 12; b_ = 35000; out = [b_]
        for m in range(1, 85):
            b_ = max(b_ * (1 + rr) - p, 0) if m <= n else 0
            out.append(b_)
        return out
    b = []
    gx0, gx1, gy0, gy1 = 44, W - 12, 74, 262
    def X(m):
        return gx0 + (gx1 - gx0) * m / 84
    def Y(v):
        return gy1 - (gy1 - gy0) * v / 36000
    b.append(T(0, 16, "Still owed on a $35,000 car, at 6.9%", "h"))
    b.append(T(0, 36, "Loan balance by length of loan, no down payment", "s i2"))
    for v in (0, 10000, 20000, 30000):
        b.append(L(gx0, Y(v), gx1, Y(v), "rule"))
        b.append(T(gx0 - 6, Y(v) + 4, f"${v // 1000}K" if v else "$0", "xs mu", "end"))
    for yr in range(0, 8):
        b.append(T(X(12 * yr), gy1 + 18, f"{yr}" if yr else "0 yrs", "xs mu", "middle" if yr else "start"))
    # the year-5 marker
    b.append(L(X(60), gy0 - 4, X(60), gy1, "frame"))
    def line(series, cls):
        return P("M" + " L".join(f"{X(m):.1f} {Y(v):.1f}" for m, v in enumerate(series)), cls)
    # typical value at year five, simplified as a straight line from the price
    b.append(P(f"M{X(0):.1f} {Y(35000):.1f} L{X(60):.1f} {Y(20300):.1f}", "ink-line dashed"))
    b.append(f'<circle cx="{X(60):.1f}" cy="{Y(20300):.1f}" r="3.5" class="ink-fill"/>')
    for n, cls in ((60, "teal-line"), (72, "c1-line dashed"), (84, "c2-line dotted")):
        b.append(line(bals(n)[:n + 1], cls))
    for v, c in ((11772, "c2-fill"), (6881, "c1-fill")):
        b.append(f'<circle cx="{X(60):.1f}" cy="{Y(v):.1f}" r="4" class="{c}"/>')
    b.append(T(X(60), gy0 - 10, "YEAR 5", "cap", "middle"))
    y = gy1 + 44
    b.append(L(0, y - 4, 18, y - 4, "teal-line")); b.append(T(24, y, "5-year", "xs"))
    b.append(L(76, y - 4, 94, y - 4, "c1-line dashed")); b.append(T(100, y, "6-year", "xs"))
    b.append(L(152, y - 4, 170, y - 4, "c2-line dotted")); b.append(T(176, y, "7-year loan", "xs"))
    b.append(L(256, y - 4, 274, y - 4, "ink-line dashed")); b.append(T(280, y, "Car value", "xs"))
    y += 30
    b.append(T(0, y, "AT YEAR 5", "cap"))
    for k, v in (("5-year loan", "paid off"), ("6-year loan", "$6,881 still owed"), ("7-year loan", "$11,772 still owed"),
                 ("The car", "worth about $20,300")):
        y += 22
        b.append(T(0, y, k, "s"))
        b.append(T(W, y, v, "s b", "end"))
        b.append(L(0, y + 7, W, y + 7, "rule"))
    b.append(T(0, y + 28, "Value line simplified: about 42% lost by year five.", "xs i2"))
    write("car-loan-balances", y + 34, b, "What is still owed after five years on 5-, 6- and 7-year car loans",
          "A chart of a $35,000 car loan at 6.9% with no down payment. At year five, the 5-year loan is paid off, the "
          "6-year loan still owes $6,881 and the 7-year loan still owes $11,772. A car that has lost about 42% of its "
          "value by then is worth about $20,300. The value line is simplified as a straight line.")


# ---------------------------------------------------------------- price tags (6b, 7a)
def tag_shape(x, y, w, h):
    n = 22
    d = (f"M{x + n} {y} L{x + w - 6} {y} Q{x + w} {y} {x + w} {y + 6} L{x + w} {y + h - 6} Q{x + w} {y + h} {x + w - 6} {y + h} "
         f"L{x + n} {y + h} L{x} {y + h / 2} Z")
    return P(d, "sheet") + f'<circle cx="{x + n - 4:g}" cy="{y + h / 2:g}" r="4" class="well"/>'


def car_price_tag():
    b = []
    b.append(T(0, 16, "The same 7-year loan, both sides of the tag", "h"))
    y = 34
    b.append(tag_shape(0, y, 172, 104))
    b.append(T(30, y + 26, "FRONT", "cap"))
    b.append(T(30, y + 62, "$527", "big"))
    b.append(T(30, y + 84, "a month", "s i2"))
    b.append(tag_shape(186, y, 174, 104))
    b.append(T(216, y + 26, "BACK", "cap"))
    b.append(T(216, y + 62, "$44,229", "big"))
    b.append(T(216, y + 84, "84 payments in all", "s i2"))
    b.append(T(0, y + 132, "$35,000 car + $9,229 interest, at 6.9%", "s"))
    write("car-price-tag", y + 140, b, "The front and back of a price tag for a seven-year car loan",
          "Front of the tag: $527 a month. Back of the tag: $44,229, 84 payments in all. That is the $35,000 car plus "
          "$9,229 in interest at 6.9%.")


def rto_price_tag():
    b = []
    b.append(T(0, 16, "What a total-cost tag could look like", "h"))
    b.append(T(0, 36, "Total cost on the tag, not just the weekly price", "s i2"))
    y = 52
    b.append(tag_shape(0, y, 172, 118))
    b.append(T(30, y + 26, "FRONT", "cap"))
    b.append(T(30, y + 64, "$38.99", "big"))
    b.append(T(30, y + 86, "a week", "s i2"))
    b.append(tag_shape(186, y, 174, 118))
    b.append(T(216, y + 26, "BACK", "cap"))
    b.append(T(216, y + 50, "48 weeks to own", "s"))
    b.append(T(216, y + 78, "$1,871.52", "big"))
    b.append(T(216, y + 100, "Retail price $612", "s i2"))
    write("rto-price-tag", y + 126, b, "The front and back of a rent-to-own price tag",
          "Front of the tag: $38.99 a week. Back of the tag: 48 weeks to own, $1,871.52 in total, against a retail "
          "price of $612. The Federal Trade Commission has recommended showing shoppers the total cost while they shop.")


def rto_three_laptops():
    b = []
    b.append(T(0, 16, "What the rent-to-own total would buy", "h"))
    y = 40
    def laptop(x, y, filled=True):
        s = []
        s.append(R(x + 10, y, 80, 52, "teal-fill" if filled else "frame", rx=3))
        s.append(R(x + 16, y + 6, 68, 40, "sheet", rx=1))
        s.append(P(f"M{x} {y + 62} L{x + 100} {y + 62} L{x + 92} {y + 54} L{x + 8} {y + 54} Z", "teal-fill" if filled else "frame"))
        s.append(T(x + 50, y + 31, "$612", "s m", "middle"))
        return "".join(s)
    for i in range(3):
        b.append(laptop(i * 125 - (2 if i == 2 else 0), y))
    b.append(T(0, y + 92, "3 laptops at retail: $1,836", "m"))
    b.append(T(W, y + 92, "+ $35.52 left", "s i2", "end"))
    b.append(L(0, y + 104, W, y + 104, "rule"))
    b.append(T(0, y + 126, "48 rent-to-own payments: $1,871.52, for one", "s i2"))
    write("rto-three-laptops", y + 132, b, "Three laptops for the price of one rent-to-own laptop",
          "Three laptops at the $612 retail price cost $1,836, with $35.52 left over from the $1,871.52 that 48 "
          "rent-to-own payments cost for one laptop.")


# ---------------------------------------------------------------- 8. subscriptions statement
def subs_statement():
    b = []
    rows = [("Grocery store", 84.12, False), ("Streaming service A", 15.49, True), ("Gas station", 41.30, False),
            ("Streaming service B", 11.99, True), ("Music", 10.99, True), ("Coffee shop", 5.75, False),
            ("Cloud storage", 2.99, True), ("Gym", 29.99, True), ("Pharmacy", 12.40, False),
            ("Phone game pass", 6.99, True), ("News app", 9.99, True), ("Restaurant", 38.60, False)]
    top, rh = 88, 27
    sh = top + rh * len(rows) + 64
    b.append(R(0.5, 0.5, W - 1, sh, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Card activity, one month", "h"))
    b.append(T(14, 72, "CHARGE", "cap"))
    b.append(T(250, 72, "AMOUNT", "cap", "end"))
    b.append(T(W - 14, 72, "RUNNING", "cap", "end"))
    b.append(L(14, 80, W - 14, 80, "rule"))
    y, run = top, 0
    for lab, amt, rec in rows:
        cy = y + rh / 2 + 5
        if rec:
            run += amt
            b.append(R(10, y + 3, W - 20, rh - 6, "wash", rx=3))
            b.append(T(18, cy, tx(lab), "s m"))
            b.append(T(250, cy, f"${amt:.2f}", "s m", "end"))
            b.append(T(W - 14, cy, f"${run:.2f}", "s b", "end"))
        else:
            b.append(T(18, cy, tx(lab), "s i2"))
            b.append(T(250, cy, f"${amt:.2f}", "s i2", "end"))
        y += rh
    b.append(L(14, y + 2, W - 14, y + 2, "ink-line"))
    b.append(T(14, y + 26, "Repeats every month", "m"))
    b.append(T(W - 14, y + 28, "$88.43", "big", "end"))
    b.append(T(14, y + 48, "That's $1,061 a year.", "s i2"))
    b.append(T(0, sh + 26, "Shaded: charges that renew on their own.", "s"))
    b.append(T(0, sh + 46, "The gym (unused) and the news app (a free trial)", "s i2"))
    b.append(T(0, sh + 64, "add up to $40 a month, about $480 a year.", "s i2"))
    write("subscriptions-statement", sh + 70, b, "A fictional month of card charges with the subscriptions shaded",
          "A month of twelve card charges. Seven renew every month: streaming service A $15.49, streaming service B "
          "$11.99, music $10.99, cloud storage $2.99, gym $29.99, phone game pass $6.99 and news app $9.99, a running "
          "total of $88.43 a month, $1,061 a year. The unused gym and the news app left from a free trial add up to "
          "$40 a month, about $480 a year.")


# ---------------------------------------------------------------- 9a. fictional finfluencer post
def finfluencer_post():
    b = []
    h_card = 250
    b.append(R(0.5, 0.5, W - 1, h_card, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(f'<circle cx="34" cy="52" r="18" class="range-fill"/>')
    b.append(T(34, 57, "TG", "s b", "middle"))
    b.append(T(62, 48, "TotallyRealGains", "m"))
    b.append(T(62, 66, "@totally.real.gains.example", "xs i2"))
    lines = [("My system makes 1% a day.", "1"), ("Guaranteed. I never lose.", None),
             ("Only 20 spots left this week!", "2"), ("DM me to join the VIP group.", "3"),
             ("Deposits in crypto only.", "4")]
    y = 102
    for s, n in lines:
        b.append(T(26, y, tx(s)))
        if n:
            b.append(f'<circle cx="{W - 30:g}" cy="{y - 5:g}" r="11" class="ink-fill"/>')
            b.append(T(W - 30, y - 0.5, n, "xs rev", "middle"))
        y += 24
    b.append(L(14, y - 6, W - 14, y - 6, "rule"))
    b.append(T(26, y + 14, "12.4K likes · 3,108 shares", "xs mu"))
    y = h_card + 30
    flags = [("1", "A steady, guaranteed return. Real investments go up and down."),
             ("2", "Urgency, so you don't stop to check."),
             ("3", "A move to a private chat or group."),
             ("4", "Payment in crypto, gift cards or wires.")]
    for n, s in flags:
        b.append(f'<circle cx="11" cy="{y - 5:g}" r="11" class="ink-fill"/>')
        b.append(T(11, y - 0.5, n, "xs rev", "middle"))
        words = s.split(" ")
        line1, line2 = s, ""
        if len(s) > 44:
            cut = s.rfind(" ", 0, 44)
            line1, line2 = s[:cut], s[cut + 1:]
        b.append(T(30, y, tx(line1), "s"))
        if line2:
            y += 18
            b.append(T(30, y, tx(line2), "s i2"))
        y += 28
    write("finfluencer-post", y - 10, b, "A fictional social media post with four warning signs marked",
          "A made-up post from an invented account, TotallyRealGains: \"My system makes 1% a day. Guaranteed. I never "
          "lose. Only 20 spots left this week! DM me to join the VIP group. Deposits in crypto only.\" Four warning "
          "signs are numbered: 1, a steady, guaranteed return, when real investments go up and down; 2, urgency, so "
          "you don't stop to check; 3, a move to a private chat or group; 4, payment in crypto, gift cards or wires.")


# ---------------------------------------------------------------- 9b. 1% a day curve
def one_percent_curve():
    b = []
    gx0, gx1, gy0, gy1 = 44, W - 10, 56, 236
    def X(d):
        return gx0 + (gx1 - gx0) * d / 365
    def Y(v):
        return gy1 - (gy1 - gy0) * v / 40000
    b.append(T(0, 16, "$1,000 at \"just 1% a day\"", "h"))
    b.append(T(0, 36, "Compounded every day for a year", "s i2"))
    for v in (0, 10000, 20000, 30000, 40000):
        b.append(L(gx0, Y(v), gx1, Y(v), "rule"))
        b.append(T(gx0 - 6, Y(v) + 4, f"${v // 1000}K" if v else "$0", "xs mu", "end"))
    for d, lab in ((0, "Day 0"), (90, "90"), (180, "180"), (270, "270"), (365, "365")):
        b.append(T(X(d), gy1 + 18, lab, "xs mu", "middle" if d not in (0, 365) else ("start" if d == 0 else "end")))
    d = "M" + " L".join(f"{X(t):.1f} {Y(1000 * 1.01 ** t):.1f}" for t in range(0, 366, 5)) + f" L{X(365):.1f} {Y(1000 * 1.01 ** 365):.1f}"
    b.append(P(d, "teal-line"))
    b.append(L(X(0), Y(1000), X(365), Y(1100), "ink-line dashed"))
    b.append(f'<circle cx="{X(365):.1f}" cy="{Y(37783):.1f}" r="4" class="series-ring"/>')
    b.append(T(X(365) - 8, Y(37783) + 4, "about $37,800", "s b", "end"))
    yl = gy1 + 42
    b.append(L(0, yl - 4, 18, yl - 4, "teal-line")); b.append(T(24, yl, "1% a day", "xs"))
    b.append(L(110, yl - 4, 128, yl - 4, "ink-line dashed")); b.append(T(134, yl, "A 10% year, for comparison: $1,100", "xs"))
    b.append(T(0, yl + 28, "Nearly 38 times your money. No legitimate", "s"))
    b.append(T(0, yl + 46, "investment reliably does anything close.", "s"))
    write("one-percent-a-day", yl + 52, b, "What 1% a day would do to $1,000 in a year",
          "A curve rising slowly and then steeply, from $1,000 on day 0 to about $37,800 on day 365, nearly 38 times "
          "the money. A dashed line for comparison: a 10% year, ending at $1,100. No legitimate investment reliably "
          "does anything close.")


# ---------------------------------------------------------------- 10a. two savers
def two_savers():
    def path(start, stop):
        b_ = 0; out = {22: 0}
        for a in range(22, 65):
            if start <= a <= stop:
                b_ = (b_ + 4050) * 1.06
            else:
                b_ = b_ * 1.06
            out[a + 1] = b_
        return out
    A, B, C = path(22, 64), path(32, 64), path(22, 31)
    b = []
    gx0, gx1, gy0, gy1 = 54, W - 52, 56, 240
    def X(a):
        return gx0 + (gx1 - gx0) * (a - 22) / 43
    def Y(v):
        return gy1 - (gy1 - gy0) * v / 850000
    b.append(T(0, 16, "Two savers, $4,050 a year each", "h"))
    b.append(T(0, 36, "Balance by age, at an assumed 6% a year", "s i2"))
    for v in (0, 200000, 400000, 600000, 800000):
        b.append(L(gx0, Y(v), gx1, Y(v), "rule"))
        b.append(T(gx0 - 6, Y(v) + 4, f"${v // 1000}K" if v else "$0", "xs mu", "end"))
    for a in (22, 32, 42, 52, 65):
        b.append(T(X(a), gy1 + 18, f"{a}", "xs mu", "middle"))
    def line(s, cls):
        return P("M" + " L".join(f"{X(a):.1f} {Y(v):.1f}" for a, v in sorted(s.items())), cls)
    b.append(line(C, "c2-line dotted"))
    b.append(line({a: v for a, v in B.items() if a >= 32}, "c1-line dashed"))
    b.append(line(A, "teal-line"))
    for s, lab, cls in ((A, "$805K", "s b"), (B, "$418K", "s b"), (C, "$387K", "s b")):
        b.append(T(X(65) + 6, Y(s[65]) + (4 if s is A else (-2 if s is B else 12)), lab, cls))
    y = gy1 + 42
    b.append(L(0, y - 4, 18, y - 4, "teal-line")); b.append(T(24, y, "Starts at 22", "xs"))
    b.append(L(120, y - 4, 138, y - 4, "c1-line dashed")); b.append(T(144, y, "Starts at 32", "xs"))
    b.append(L(236, y - 4, 254, y - 4, "c2-line dotted")); b.append(T(260, y, "Saves 22–31,", "xs"))
    b.append(T(260, y + 15, "then stops", "xs"))
    b.append(T(0, y + 40, "The 6% return is an assumption, not a promise.", "xs i2"))
    write("two-savers", y + 46, b, "Retirement balances at 65 for three savers",
          "Each saver puts in $4,050 a year, 6% of a $45,000 salary plus the full match, at an assumed 6% return. "
          "Starting at 22 and saving to 65: about $805,000. Starting at 32: about $418,000. Saving only from 22 to 31 "
          "and then stopping: about $387,000, nearly as much as the saver who started at 32.")


# ---------------------------------------------------------------- 10b. pay stub
def pay_stub():
    b = []
    rows = [("Gross pay", "$1,730.77", ""), ("401(k), you, 3%", "−$51.92", ""), ("Employer match", "+$25.96", "teal")]
    sh = 252
    b.append(R(0.5, 0.5, W - 1, sh, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Pay stub, one paycheck", "h"))
    b.append(T(14, 64, "$45,000 a year, paid every two weeks", "xs i2"))
    b.append(L(14, 74, W - 14, 74, "rule"))
    y = 98
    for k, v, c in rows:
        b.append(T(14, y, k, "s"))
        b.append(T(W - 14, y, v, "s b" + (" teal" if c else ""), "end"))
        b.append(L(14, y + 10, W - 14, y + 10, "rule"))
        y += 30
    b.append(tag(14, y - 12, 156, 20, "MATCH YOU PASSED UP"))
    b.append(T(W - 14, y + 3, "$25.96", "s b", "end"))
    b.append(T(14, y + 34, "Your employer matches 50% of what you put in,", "xs i2"))
    b.append(T(14, y + 50, "up to 6% of pay. At 6%, the match is $51.92.", "xs i2"))
    b.append(T(0, sh + 28, "$25.96 a paycheck is $675 a year.", "s m"))
    write("pay-stub-match", sh + 34, b, "A fictional pay stub showing the employer match passed up",
          "One paycheck on a $45,000 salary, paid every two weeks: gross pay $1,730.77; your 401(k) contribution at "
          "3%, $51.92; the employer match, $25.96. The match you passed up: $25.96. Your employer matches 50% of what "
          "you put in, up to 6% of pay, so at 6% the match would be $51.92. $25.96 a paycheck is $675 a year.")


# ---------------------------------------------------------------- 11. balance before day one
def student_balance():
    b = []
    b.append(T(0, 16, "What you owe when repayment starts", "h"))
    b.append(T(0, 36, "$7,500 a year for four years, unsubsidized, at 6.52%", "s i2"))
    y = 54
    total = 35868
    w1 = W * 30000 / total
    b.append(R(0, y, w1 - 2, 40, "teal-fill", rx=3))
    b.append(T(10, y + 25, "$30,000 borrowed", "s rev"))
    f'<defs></defs>'
    b.append(f'<defs><pattern id="sl-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch-line"/></pattern></defs>')
    b.append(R(w1, y, W - w1, 40, "", rx=3, extra=' fill="url(#sl-hatch)"'))
    b.append(R(w1 + 0.5, y + 0.5, W - w1 - 1, 39, "frame", rx=3))
    b.append(T(W, y + 62, "+ about $5,900 of interest", "s m", "end"))
    b.append(T(W, y + 80, "built up before the first payment", "s i2", "end"))
    b.append(L(0, y + 96, W, y + 96, "rule"))
    b.append(T(0, y + 120, "First bill is figured on about $35,900", "m"))
    write("student-balance", y + 126, b, "What a student owes when repayment starts",
          "A bar: $30,000 borrowed, $7,500 a year for four years in unsubsidized loans at 6.52%, plus about $5,900 of "
          "interest built up during school and the six-month grace period, so the first bill is figured on about $35,900.")


# ---------------------------------------------------------------- 12. the worry ad
def worry_ad():
    b = []
    def num(cx, cy, n):
        return (f'<circle cx="{cx:g}" cy="{cy:g}" r="11" class="ink-fill"/>' + T(cx, cy + 4.5, n, "xs rev", "middle"))
    h_card = 276
    b.append(R(0.5, 0.5, W - 1, h_card, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 52, "Tired, foggy, bloated?", "big"))
    b.append(num(W - 26, 45, "1"))
    b.append(T(14, 76, "It could be \u201ctoxin overload.\u201d", "m"))
    b.append(T(14, 96, "Daily Cleanse Formula (an invented product)", "s i2"))
    b.append(L(14, 112, W - 14, 112, "rule"))
    b.append(T(14, 136, "Offer ends tonight:", "s"))
    b.append(tag(140, 121, 92, 22, "02:14:37"))
    b.append(num(W - 26, 132, "2"))
    b.append(R(14, 156, 248, 40, "teal-fill", rx=4))
    b.append(T(138, 181, "TRY IT FREE: just $4.95 shipping", "s rev", "middle"))
    b.append(num(W - 26, 176, "3"))
    b.append(T(14, 224, "After 14 days, $79.95 a month until you", "xs i2"))
    b.append(T(14, 241, "cancel. These statements have not been", "xs i2"))
    b.append(T(14, 258, "evaluated by the Food and Drug Administration.", "xs i2"))
    b.append(num(W - 26, 240, "4"))
    y = h_card + 32
    for n, s_ in (("1", "A problem you didn't know you had"), ("2", "Urgency"), ("3", "A \u201cfree\u201d first step"),
                  ("4", "The real product, in the small print")):
        b.append(num(11, y - 5, n))
        b.append(T(30, y, s_, "s"))
        y += 28
    write("worry-ad", y - 12, b, "A fictional supplement ad with the four steps of a worry ad numbered",
          "A made-up ad for an invented supplement, Daily Cleanse Formula. 1: the headline asks \u201cTired, foggy, "
          "bloated?\u201d and says it could be \u201ctoxin overload\u201d, a problem you didn't know you had. 2: a "
          "countdown, \u201cOffer ends tonight: 02:14:37\u201d, the urgency. 3: a button, \u201cTry it free: just $4.95 "
          "shipping\u201d, the free first step. 4: the small print, \u201cAfter 14 days, $79.95 a month until you cancel. "
          "These statements have not been evaluated by the Food and Drug Administration\u201d, the real product.")


# ---------------------------------------------------------------- four levels of debt (Plain words, Nov 9)
def four_borrowers():
    """Four columns, one per borrower; identity edges on the headers (with the name as the second cue)."""
    b = []
    cw = W / 4
    cx = [cw * i + cw / 2 for i in range(4)]
    b.append(T(0, 16, "Four kinds of borrower", "h"))
    b.append(T(0, 36, "Same word, debt, with different rules at each level", "s i2"))
    heads = [("Household", "c1-edge"), ("City", "c2-edge"), ("State", "c3-edge"), ("Washington", "teal-edge")]
    y = 52
    for (h, edge), x in zip(heads, cx):
        b.append(R(x - cw / 2 + 3, y, cw - 6, 26, edge, rx=4))
        b.append(T(x, y + 17.5, h, "s m", "middle"))
    def row(y, cap, cells):
        b.append(L(0, y - 18, W, y - 18, "rule"))
        b.append(T(0, y, cap, "cap"))
        for x, c in zip(cx, cells):
            lines = c if isinstance(c, tuple) else (c,)
            for k, ln in enumerate(lines):
                cls = ("s b" if k == 0 else "xs i2")
                b.append(T(x, y + 24 + 16 * k, ln, cls, "middle"))
    row(108, "DOES IT ISSUE THE MONEY IT OWES?", ["No", "No", "No", ("Yes", "it owes dollars")])
    row(176, "CAN IT GO BANKRUPT?", ["Yes", ("Yes", "if its state", "allows it"), "No", ("No", "can't be forced", "to default")])
    row(260, "MUST IT BALANCE ITS BUDGET?", [("Over time", "loans end"), ("Yes", "day-to-day", "budget"), ("Yes", "day-to-day", "budget"), "No"])
    y = 344
    b.append(L(0, y - 18, W, y - 18, "rule"))
    b.append(T(0, y, "IN A RECESSION", "cap"))
    ay0, ay1 = y + 16, y + 52
    for i, x in enumerate(cx):
        if i < 3:
            b.append(L(x, ay0, x, ay1, "ink-line"))
            b.append(P(f"M{x - 6:g} {ay1 - 8:g} L{x:g} {ay1:g} L{x + 6:g} {ay1 - 8:g}", "ink-line"))
            b.append(T(x, ay1 + 20, "Cuts back", "s b", "middle"))
        else:
            b.append(L(x, ay1, x, ay0, "teal-line"))
            b.append(P(f"M{x - 6:g} {ay0 + 8:g} L{x:g} {ay0:g} L{x + 6:g} {ay0 + 8:g}", "teal-line"))
            b.append(T(x, ay1 + 20, "Borrows more", "s b", "middle"))
    y = ay1 + 52
    b.append(T(0, y, "Cities and states must balance their day-to-day", "xs i2"))
    b.append(T(0, y + 16, "budgets, so a recession forces cuts. Washington", "xs i2"))
    b.append(T(0, y + 32, "can borrow to fill the gap.", "xs i2"))
    write("four-borrowers", y + 40, b, "Four kinds of borrower: a household, a city, a state and Washington",
          "A comparison in four columns. Does it issue the money it owes? Household no, city no, state no, Washington yes, "
          "because it owes dollars. Can it go bankrupt? Household yes; city yes, if its state allows it; state no; "
          "Washington no, it can't be forced to default. Must it balance its budget? Household over time, because loans "
          "end; city and state yes, their day-to-day budgets; Washington no. In a recession: household, city and state cut "
          "back; Washington borrows more. Cities and states must balance their day-to-day budgets, so a recession forces "
          "cuts; Washington can borrow to fill the gap.")


# ---------------------------------------------------------------- Money Traps parts 13-16 (Nov 9)
import textwrap


def numdot(x, y, n):
    return f'<circle cx="{x:g}" cy="{y - 5:g}" r="11" class="ink-fill"/>' + T(x, y - 0.5, str(n), "xs rev", "middle")


def betting_cost():
    """Expected yearly loss on $20 a day ($7,300 wagered), picking winners half the time."""
    b = []
    rows = [("One game at a time, at −110", "4.5¢ per $1", 332), ("All bets, 2025 average", "about 10¢ per $1", 742),
            ("Four-pick parlays", "17¢ per $1", 1240)]
    b.append(T(0, 16, "What $20 a day of betting costs in a year", "h"))
    b.append(T(0, 36, "Expected loss on $7,300 of bets, winning half of them", "s i2"))
    y = 64
    maxw = W - 74
    for lab, rate, v in rows:
        b.append(T(0, y + 4, tx(lab), "m"))
        b.append(T(W, y + 4, tx(rate), "s i2", "end"))
        w = maxw * v / 1240
        b.append(R(0, y + 12, w, 18, "teal-fill", rx=2))
        b.append(T(w + 6, y + 26, f"${round(v, -1):,.0f}", "s b"))
        y += 58
    b.append(T(0, y + 2, "These are averages. In any one year some bettors come", "xs i2"))
    b.append(T(0, y + 18, "out ahead and many lose more; the more you bet, the", "xs i2"))
    b.append(T(0, y + 34, "closer your results get to the average.", "xs i2"))
    write("betting-cost", y + 42, b, "What $20 a day of betting costs in a year",
          "Expected loss on $7,300 of bets, winning half of them. One game at a time at standard minus 110 "
          "odds, about 4.5 cents per dollar: about $330. All bets at the 2025 average, about 10 cents per dollar: about "
          "$740. Four-pick parlays, about 17 cents per dollar: about $1,240. These are averages; in any one year some "
          "bettors come out ahead and many lose more, and the more you bet, the closer your results get to the average.")


def gig_payouts():
    """Where $20,000 of app payouts goes: car costs, federal tax, what's left to spend."""
    b = []
    b.append(T(0, 16, "Where $20,000 of app payouts goes", "h"))
    b.append(T(0, 36, "Delivery work in 2026, federal tax, single filer", "s i2"))
    cases = [("Gig work only", 5000, 2120), ("Gig work plus a $20,000 part-time job", 5000, 3290)]
    y = 62
    sc = W / 20000
    for lab, car, tax in cases:
        left = 20000 - car - tax
        b.append(T(0, y, tx(lab), "m"))
        x = 0
        for v, cls in ((car, "range-fill"), (tax, "ink-fill"), (left, "teal-fill")):
            b.append(R(x, y + 10, v * sc - (2 if cls != "teal-fill" else 0), 22, cls))
            x += v * sc
        yy = y + 52
        b.append(R(0, yy - 10, 10, 10, "range-fill"))
        b.append(T(16, yy, f"Car costs ${car:,}", "xs"))
        b.append(R(134, yy - 10, 10, 10, "ink-fill"))
        b.append(T(150, yy, f"Tax ${tax:,}", "xs b"))
        b.append(R(238, yy - 10, 10, 10, "teal-fill"))
        b.append(T(254, yy, f"Yours ${left:,}", "xs"))
        y += 92
    b.append(T(0, y - 14, "The app pays the whole $20,000. The tax is due in April", "xs i2"))
    b.append(T(0, y + 2, "unless you pay it as you go.", "xs i2"))
    write("gig-payouts", y + 10, b, "Where $20,000 of app payouts goes",
          "Delivery work in 2026, federal tax, single filer. Gig work only: car costs $5,000, self-employment tax $2,120, "
          "leaving $12,880 to spend. Gig work plus a $20,000 part-time job: car costs $5,000, tax $3,290, leaving $11,710. "
          "The app pays the whole $20,000; the tax is due in April unless you pay it as you go.")


def scam_texts():
    """A fictional text thread from a fake bank fraud department, with four warning signs numbered."""
    b = []
    msgs = [("in", "ALERT: A $1,240 charge was attempted on your card. Reply YES if this was you, NO if not.", None),
            ("out", "NO", None),
            ("in", "A fraud specialist will call you now. Stay on the line. Don't hang up.", 1),
            ("in", "To protect your money, move it to a safe account. Send it by Zelle to yourself at this number.", 2),
            ("in", "Don't tell anyone at the branch. They may be part of the fraud.", 3)]
    b_w = 232
    rows = []
    for side, text, n in msgs:
        lines = textwrap.wrap(text, 34)
        rows.append((side, lines, n))
    h_card = 64 + sum(len(l) * 17 + 22 for _, l, _ in rows) + 4
    b.append(R(0.5, 0.5, W - 1, h_card, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Bank Fraud Dept.", "m"))
    b.append(T(W - 14, 44, "Text message", "xs i2", "end"))
    b.append(L(14, 54, W - 14, 54, "rule"))
    y = 66
    for side, lines, n in rows:
        hh = len(lines) * 17 + 10
        if side == "in":
            b.append(R(14, y, b_w, hh, "wash", rx=8))
            for k, ln in enumerate(lines):
                b.append(T(24, y + 18 + 17 * k, tx(ln), "s"))
            if n:
                b.append(numdot(W - 30, y + hh / 2 + 5, n))
        else:
            b.append(R(W - 14 - 48, y, 48, hh, "frame", rx=8))
            b.append(T(W - 14 - 24, y + 18, tx(lines[0]), "s b", "middle"))
        y += hh + 12
    y = h_card + 30
    flags = [(1, "Pressure to act now, before you can check."),
             (2, "\"Move your money to keep it safe.\" A real bank never asks this."),
             (3, "Secrecy, even from your own bank."),
             (4, "Hang up and call the number on the back of your card.")]
    for n, text in flags:
        if n < 4:
            b.append(numdot(11, y, n))
        lines = textwrap.wrap(text, 44)
        for k, ln in enumerate(lines):
            b.append(T(30 if n < 4 else 0, y + 18 * k, tx(ln), "s" if (k == 0 and n < 4) else ("s b" if n == 4 else "s i2")))
        y += 18 * len(lines) + 12
    write("scam-texts", y - 6, b, "A fictional text thread from a fake bank fraud department, with three warning signs marked",
          "A made-up text thread from \"Bank Fraud Dept.\": an alert about a $1,240 charge asks for a YES or NO reply; "
          "after a NO, the messages say a fraud specialist will call and not to hang up (warning sign 1, pressure to act "
          "now), to move money to a safe account by sending it by Zelle to yourself at their number (sign 2: a real bank "
          "never asks this), and not to tell anyone at the branch (sign 3, secrecy, even from your own bank). The safe "
          "move: hang up and call the number on the back of your card.")


def cosigner_notice():
    """The FTC's required Notice to Cosigner (16 CFR 444.3), excerpted, with three sentences marked. A real federal form,
    so no FICTIONAL label."""
    b = []
    sents = [("You are being asked to guarantee this debt. Think carefully before you do.", None),
             ("If the borrower doesn't pay the debt, you will have to.", 1),
             ("Be sure you can afford to pay if you have to, and that you want to accept this responsibility.", None),
             ("You may have to pay up to the full amount of the debt if the borrower does not pay. You may also have to "
              "pay late fees or collection costs, which increase this amount.", 2),
             ("The creditor can collect this debt from you without first trying to collect from the borrower.", 3),
             ("If this debt is ever in default, that fact may become a part of your credit record.", None)]
    blocks = [(textwrap.wrap(t, 42), n) for t, n in sents]
    h_sheet = 70 + sum(len(l) * 18 + 10 for l, _ in blocks) + 8
    b.append(R(0.5, 0.5, W - 1, h_sheet, "sheet", rx=6))
    b.append(T(14, 22, "REQUIRED BY FEDERAL RULE · EXCERPT", "cap"))
    b.append(T(14, 46, "Notice to Cosigner", "h"))
    b.append(L(14, 58, W - 14, 58, "rule"))
    y = 76
    for lines, n in blocks:
        hh = len(lines) * 18
        if n:
            b.append(R(10, y - 13, W - 54, hh + 4, "wash", rx=3))
            b.append(numdot(W - 24, y + hh / 2 - 4, n))
        for k, ln in enumerate(lines):
            b.append(T(16, y + 18 * k, tx(ln), "s b" if n else "s"))
        y += hh + 10
    y = h_sheet + 28
    b.append(T(0, y, "Lenders such as auto dealers and finance companies must", "xs i2"))
    b.append(T(0, y + 16, "hand this to a co-signer as a separate page.", "xs i2"))
    write("cosigner-notice", y + 24, b, "The federal Notice to Cosigner, excerpted, with three sentences marked",
          "An excerpt of the Notice to Cosigner required by federal rule (16 CFR 444.3): You are being asked to guarantee "
          "this debt. Think carefully before you do. Marked 1: If the borrower doesn't pay the debt, you will have to. Be "
          "sure you can afford to pay if you have to, and that you want to accept this responsibility. Marked 2: You may "
          "have to pay up to the full amount of the debt if the borrower does not pay. You may also have to pay late fees "
          "or collection costs, which increase this amount. Marked 3: The creditor can collect this debt from you "
          "without first trying to collect from the borrower. If this debt is ever in default, that fact may become a "
          "part of your credit record. Lenders such as auto dealers and finance companies must hand this to a co-signer "
          "as a separate page.")


# ---------------------------------------------------------------- Nov 11: four more parts
def statement_marked():
    """Fictional credit card statement with a duplicate, a $1 test charge and a refund that never posted."""
    b = []
    rows = [("Oct 2", "Grocery Mart", "$64.18", None), ("Oct 3", "Fitness Club", "$29.00", None),
            ("Oct 3", "Fitness Club", "$29.00", 1), ("Oct 7", "Online order", "$112.40", None),
            ("Oct 9", "ZQX*SVC 8831", "$1.00", 2)]
    top = 90
    rh = 30
    h_sheet = top + rh * len(rows) + 64
    b.append(R(0.5, 0.5, W - 1, h_sheet, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Card statement, closing Oct 15", "h"))
    b.append(T(14, 72, "DATE", "cap"))
    b.append(T(70, 72, "DESCRIPTION", "cap"))
    b.append(T(W - 50, 72, "AMOUNT", "cap", "end"))
    b.append(L(14, 80, W - 14, 80, "rule"))
    y = top
    for d, desc, amt, n in rows:
        cy = y + rh / 2 + 5
        if n:
            b.append(R(10, y + 3, W - 20, rh - 6, "wash", rx=3))
            b.append(numdot(W - 26, cy + 1, n))
        b.append(T(14, cy, d, "s i2"))
        b.append(T(70, cy, tx(desc), "b" if n else ""))
        b.append(T(W - 50, cy, amt, "b" if n else "", "end"))
        y += rh
        b.append(L(14, y, W - 14, y, "rule"))
    b.append(R(10, y + 10, W - 20, 40, "wash", rx=3))
    b.append(numdot(W - 26, y + 36, 3))
    b.append(T(14, y + 27, "Not here: the $86.00 refund from", "s b"))
    b.append(T(14, y + 43, "your Oct 1 return", "s b"))
    yy = h_sheet + 26
    notes = [(1, "Charged twice: a billing error."), (2, "A $1 charge you don't know: thieves test"),
             (None, "cards this way. Call the card company now."), (3, "A refund that never posted is a billing error too.")]
    for n, line in notes:
        if n:
            b.append(numdot(11, yy + 1, n))
        b.append(T(30, yy, tx(line), "s"))
        yy += 22
    b.append(T(0, yy + 6, "To dispute them under federal law, a written", "s i2"))
    b.append(T(0, yy + 24, "notice must reach the card company by Dec 14,", "s i2"))
    b.append(T(0, yy + 42, "60 days after the Oct 15 statement.", "s i2"))
    write("statement-marked", yy + 50, b, "A fictional credit card statement with three problems marked",
          "A fictional card statement closing October 15: Grocery Mart $64.18; Fitness Club $29.00; Fitness Club $29.00 "
          "again, marked 1, charged twice, a billing error; Online order $112.40; ZQX*SVC 8831 $1.00, marked 2, a $1 "
          "charge you don't know, the way thieves test cards, so call the card company now. Marked 3: the $86.00 refund "
          "from an October 1 return isn't on the statement, which is a billing error too. To dispute any of them under "
          "federal law, the written notice must reach the card company by December 14, 60 days after October 15.")


def cushion_costs():
    """What a $400 repair costs beyond the $400, four ways to pay."""
    b = []
    b.append(T(0, 16, "A $400 car repair, with $100 in checking", "h"))
    b.append(T(0, 36, "What it costs beyond the $400", "s i2"))
    rows = [("Overdraft, four fees", "$140", 140), ("Payday loan for $300, kept 8 weeks", "$180", 180),
            ("Credit card at 22%, $50 a month", "about $37", 37), ("Your own savings", "$0", 0)]
    y = 58
    maxw = W - 80
    for lab, val, v in rows:
        b.append(T(0, y + 4, tx(lab), "m"))
        w = maxw * v / 180
        if v:
            b.append(R(0, y + 12, w, 18, "teal-fill", rx=2))
        else:
            b.append(L(0, y + 12, 0, y + 30, "ink-line"))
        b.append(T(w + 6, y + 26, val, "s b"))
        y += 56
    b.append(T(0, y, "Fees and rates are illustrative; some banks charge", "xs i2"))
    b.append(T(0, y + 16, "less for an overdraft, or nothing.", "xs i2"))
    write("cushion-costs", y + 24, b, "What a $400 car repair costs beyond the $400, four ways",
          "A $400 car repair with $100 in checking. Overdrawing the debit card, with four overdraft fees: $140. A payday "
          "loan for the $300 you're short, kept eight weeks: $180 in fees. A credit card at 22%, paying $50 a month: about $37 in interest. Your "
          "own savings: $0. Fees and rates are illustrative; some banks charge less for an overdraft, or nothing.")


def one_name_reach():
    """Sam and Alex's accounts: what Alex can reach the week after Sam dies."""
    b = []
    b.append(T(0, 16, "The week after: what Alex can use", "h"))
    b.append(T(0, 36, "Sam handled the money. Most of it was in Sam's name.", "s i2"))
    rows = [("Joint checking", "$3,200", "Passes to Alex", True),
            ("Savings, Sam only", "$18,000", "Waits for the estate", False),
            ("Credit card, Sam only", "", "Closed; Alex never had a card", False),
            ("401(k)", "$140,000", "Alex's, after weeks of paperwork", False)]
    y = 54
    for title, amt, note, now in rows:
        b.append(R(0.5, y + 0.5, W - 1, 52, "sheet" if now else "well", rx=4))
        b.append(tag(10, y + 10, 74, 18, "USE NOW" if now else "NOT YET", "ink-fill" if now else "ink2-fill"))
        b.append(T(94, y + 24, tx(title), "s b"))
        if amt:
            b.append(T(W - 10, y + 24, amt, "s b", "end"))
        b.append(T(94, y + 43, tx(note), "xs i2"))
        y += 60
    yy = y + 10
    b.append(L(0, yy - 4, W, yy - 4, "rule"))
    b.append(T(0, yy + 16, "Set up differently, with a beneficiary on", "s"))
    b.append(T(0, yy + 34, "the savings and a card in Alex's own name:", "s"))
    b.append(T(0, yy + 62, "$21,200", "big"))
    b.append(T(108, yy + 62, "usable that week, and a credit", "s i2"))
    b.append(T(108, yy + 80, "history of Alex's own.", "s i2"))
    write("one-name-reach", yy + 88, b, "What Alex can use the week after Sam dies, in an illustrative household",
          "Use now: joint checking, $3,200, which passes to Alex. Not yet: savings in Sam's name only, $18,000, which "
          "waits for the estate; the credit card in Sam's name only, closed, with no card ever in Alex's name; the "
          "401(k), $140,000, which is Alex's after weeks of paperwork. Set up differently, with a beneficiary on the "
          "savings and a card in Alex's own name: $21,200 usable that week, and a credit history of Alex's own.")


def creep_bars():
    """Year-10 spend vs. save for Taylor and Jordan, and what each has saved."""
    b = []
    b.append(T(0, 16, "Same pay, same raises, year 10", "h"))
    b.append(T(0, 36, "$58,715 a year. Jordan saved half of every raise.", "s i2"))
    y = 60
    for name, spend, save in (("Taylor", 56953, 1761), ("Jordan", 50508, 8207)):
        b.append(T(0, y + 4, name, "m"))
        ws = W * spend / 58715
        b.append(R(0, y + 12, ws, 20, "range-fill"))
        b.append(R(ws, y + 12, W - ws, 20, "teal-fill"))
        b.append(T(0, y + 50, f"Spends ${spend:,}", "s"))
        b.append(T(W, y + 50, f"Saves ${save:,}", "s b", "end"))
        y += 74
    b.append(L(0, y - 6, W, y - 6, "rule"))
    b.append(T(0, y + 16, "Saved after 10 years, at a 6% return", "m"))
    y += 30
    for name, v in (("Taylor", 20100), ("Jordan", 56400)):
        w = (W - 140) * v / 56400
        b.append(T(0, y + 14, name, "s"))
        b.append(R(60, y, w, 18, "teal-fill", rx=2))
        b.append(T(60 + w + 6, y + 14, f"${v:,}", "s b"))
        y += 30
    b.append(T(0, y + 8, "Jordan's spending still rose about $6,900 over the ten years.", "xs i2"))
    write("creep-bars", y + 16, b, "Same pay, two habits: year-10 spending and saving for Taylor and Jordan",
          "Both earn $58,715 in year 10 after ten 3% raises. Taylor spends $56,953 and saves $1,761. Jordan, who saved "
          "half of every raise, spends $50,508 and saves $8,207. Saved after ten years at a 6% return: Taylor about "
          "$20,100, Jordan about $56,400. Jordan's spending still rose about $6,900 over the ten years.")


# ---------------------------------------------------------------- Money Basics (Nov 12)
def stub_split():
    """Money Basics 1: a $900 paycheck and where it goes."""
    b = []
    rows = [("Gross pay (60 hours × $15)", "$900.00", ""), ("Social Security (6.2%)", "−$55.80", "c1-fill"),
            ("Medicare (1.45%)", "−$13.05", "c2-fill"), ("Federal income tax", "−$28.08", "c3-fill")]
    sh = 214
    b.append(R(0.5, 0.5, W - 1, sh, "sheet", rx=6))
    b.append(fictional(14, 22, "start"))
    b.append(T(14, 44, "Pay stub, one paycheck", "h"))
    b.append(T(14, 64, "$15 an hour, paid every two weeks", "xs i2"))
    b.append(L(14, 74, W - 14, 74, "rule"))
    y = 98
    for k, v, c in rows:
        if c:
            b.append(R(14, y - 10, 10, 10, c, rx=2))
        b.append(T(30 if c else 14, y, tx(k), "s"))
        b.append(T(W - 14, y, v, "s b", "end"))
        b.append(L(14, y + 10, W - 14, y + 10, "rule"))
        y += 26
    b.append(R(14, y - 10, 10, 10, "teal-fill", rx=2))
    b.append(T(30, y + 1, "Take-home pay", "m"))
    b.append(T(W - 14, y + 1, "$803.07", "m", "end"))
    b.append(L(14, y + 11, W - 14, y + 11, "ink-line"))
    y = sh + 22
    b.append(T(0, y, "The same $900 as one bar", "s b"))
    y += 12
    x = 0
    for v, cls in ((55.80, "c1-fill"), (13.05, "c2-fill"), (28.08, "c3-fill"), (803.07, "teal-fill")):
        w = W * v / 900
        b.append(R(x, y, w - (1 if cls != "teal-fill" else 0), 24, cls))
        x += w
    b.append(T(0, y + 44, "$96.93 taken out", "xs"))
    b.append(T(W, y + 44, "$803.07 to your account", "xs b", "end"))
    write("stub-split", y + 50, b, "A fictional pay stub: where a $900 paycheck goes",
          "One paycheck at $15 an hour, 60 hours, paid every two weeks, single, no state income tax. Gross pay $900.00. "
          "Social Security, 6.2%: $55.80. Medicare, 1.45%: $13.05. Federal income tax withheld: $28.08. Take-home pay: "
          "$803.07. Shown again as one bar: $96.93 taken out, $803.07 to your account.")


def two_balances():
    """Money Basics 2: what the app shows against what's really left, Monday to Friday."""
    b = []
    b.append(T(0, 16, "One week, two balances", "h"))
    b.append(T(0, 36, "A $350 rent check is mailed Monday", "s i2"))
    ly = 58
    b.append(R(0, ly - 10, 12, 12, "range-fill", rx=2)); b.append(T(18, ly, "Your app shows", "xs"))
    b.append(R(140, ly - 10, 12, 12, "teal-fill", rx=2)); b.append(T(158, ly, "What's really left", "xs"))
    days = [("Monday: rent check mailed", 420, 70), ("Tuesday: $40 of gas, $100 hold", 320, 30),
            ("Wednesday: $60 of groceries", 260, -30), ("Thursday: landlord cashes the check", -90, -30),
            ("Friday: gas hold drops to $40", -30, -30)]
    z, sc = 64, 220 / 420
    y0 = 80
    y = y0
    for lab, app, real in days:
        b.append(T(0, y + 12, tx(lab), "s"))
        b.append(L(z, y + 17, z, y + 48, "ink-line"))
        for i, (v, cls) in enumerate(((app, "range-fill"), (real, "teal-fill"))):
            by = y + 20 + i * 14
            w = abs(v) * sc
            b.append(R(z if v >= 0 else z - w, by, w, 11, cls))
            b.append(T(W, by + 10, money(v, False), "xs b" if cls == "teal-fill" else "xs", "end"))
        y += 58
    b.append(T(z, y + 4, "$0", "xs mu", "middle"))
    b.append(T(0, y + 32, "The app catches up on Thursday. Your own count", "xs i2"))
    b.append(T(0, y + 48, "knew on Monday that the week's limit was $70.", "xs i2"))
    write("two-balances", y + 56, b, "One fictional week: what a banking app shows against what's really left",
          "Monday, a $350 rent check is mailed: the app shows $420, really left $70. Tuesday, $40 of gas with a $100 "
          "pump hold: app $320, really left $30. Wednesday, $60 of groceries: app $260, really left minus $30. "
          "Thursday, the landlord cashes the check: app minus $90, really left minus $30. Friday, the gas hold drops "
          "to the real $40: both minus $30. The app catches up on Thursday; your own count knew on Monday that the "
          "week's limit was $70.")


def budget_bar():
    """Money Basics 3: the same $2,689 of take-home pay, living alone and with a roommate."""
    b = []
    b.append(T(0, 16, "$2,689 a month take-home, two ways", "h"))
    b.append(T(0, 36, "$18 an hour, full time", "s i2"))
    parts = (("Fixed bills", "c1-fill"), ("Set aside", "c2-fill"), ("Flexible", "c3-fill"), ("Savings", "teal-fill"))
    y = 58
    for name, vals, note in (("Living alone", (1560, 115, 770, 244), "Savings $244 a month, 9%"),
                             ("With a roommate", (1060, 115, 770, 744), "Savings $744 a month, 28%")):
        b.append(T(0, y + 4, name, "m"))
        x = 0
        for v, (pn, cls) in zip(vals, parts):
            w = W * v / 2689
            b.append(R(x, y + 12, w - (1 if cls != "teal-fill" else 0), 22, cls))
            x += w
        b.append(T(0, y + 52, f"Fixed bills ${vals[0]:,}", "xs"))
        b.append(T(W, y + 52, note, "xs b", "end"))
        y += 80
    lx = [0, 96, 180, 262]
    for (pn, cls), xx in zip(parts, lx):
        b.append(R(xx, y - 10, 12, 12, cls, rx=2)); b.append(T(xx + 18, y, pn, "xs"))
    b.append(L(0, y + 14, W, y + 14, "rule"))
    b.append(T(0, y + 36, "Splitting the rent frees $500 a month,", "s"))
    b.append(T(0, y + 54, "more than the whole eating-out line.", "s"))
    write("budget-bar", y + 62, b, "The same $2,689 of monthly take-home pay, living alone and with a roommate",
          "Living alone: fixed bills $1,560, set aside for irregular costs $115, flexible spending $770, savings $244 a "
          "month, 9%. With a roommate: fixed bills $1,060, set aside $115, flexible $770, savings $744 a month, 28%. "
          "Splitting the rent frees $500 a month, more than the whole eating-out line.")


def rate_gap():
    """Money Basics 4: $100 a month for five years at 0.38% and at 4%."""
    b = []
    b.append(T(0, 16, "$100 a month for five years", "h"))
    b.append(T(0, 36, "$6,000 put in, at two savings rates", "s i2"))
    y = 58
    full = W - 4
    for lab, tot, intr in (("At 0.38%, the national average", 6056, 56), ("At 4%, many online banks", 6618, 618)):
        b.append(T(0, y + 4, lab, "m"))
        wd = full * 6000 / 6618
        wi = full * intr / 6618
        b.append(R(0, y + 12, wd - 1, 22, "range-fill"))
        b.append(R(wd, y + 12, max(wi, 2), 22, "teal-fill"))
        b.append(T(0, y + 52, "$6,000 put in", "xs"))
        b.append(T(W, y + 52, f"+ ${intr} interest = ${tot:,}", "xs b", "end"))
        y += 80
    b.append(R(0, y - 10, 12, 12, "range-fill", rx=2)); b.append(T(18, y, "Your deposits", "xs"))
    b.append(R(130, y - 10, 12, 12, "teal-fill", rx=2)); b.append(T(148, y, "Interest", "xs"))
    b.append(T(0, y + 28, "Same deposits, same insurance, eleven times the interest.", "xs i2"))
    write("rate-gap", y + 36, b, "$100 a month for five years at two savings rates",
          "$6,000 put in over five years. At 0.38%, the national average savings rate: $56 of interest, $6,056 in all. "
          "At 4%, paid by many online banks: $618 of interest, $6,618 in all. Same deposits, same insurance, eleven "
          "times the interest.")


def both_ways():
    """Money Basics 5: $2,000 saved at 4% and owed at 22.36%, over ten years."""
    save = {t: 2000 * 1.04 ** t for t in range(11)}
    owe = {t: 2000 * (1 + 0.2236 / 365) ** (365 * t) for t in range(11)}
    b = []
    gx0, gx1, gy0, gy1 = 54, W - 70, 56, 236
    def X(t):
        return gx0 + (gx1 - gx0) * t / 10
    def Y(v):
        return gy1 - (gy1 - gy0) * v / 20000
    b.append(T(0, 16, "The same $2,000, both ways", "h"))
    b.append(T(0, 36, "Saved at 4%, or owed on a card at 22.36%", "s i2"))
    for v in (0, 5000, 10000, 15000, 20000):
        b.append(L(gx0, Y(v), gx1, Y(v), "rule"))
        b.append(T(gx0 - 6, Y(v) + 4, f"${v // 1000}K" if v else "$0", "xs mu", "end"))
    for t in (0, 2, 4, 6, 8, 10):
        b.append(T(X(t), gy1 + 18, f"{t}", "xs mu", "middle"))
    b.append(T((gx0 + gx1) / 2, gy1 + 36, "Years", "xs mu", "middle"))
    def line(s, cls):
        return P("M" + " L".join(f"{X(t):.1f} {Y(v):.1f}" for t, v in sorted(s.items())), cls)
    b.append(line(save, "teal-line"))
    b.append(line(owe, "c3-line dashed"))
    b.append(T(X(10) + 6, Y(owe[10]) + 4, "$18,699", "s b"))
    b.append(T(X(10) + 6, Y(owe[10]) + 20, "owed", "xs"))
    b.append(T(X(10) + 6, Y(save[10]) - 10, "$2,960", "s b"))
    b.append(T(X(10) + 6, Y(save[10]) + 6, "saved", "xs"))
    y = gy1 + 62
    b.append(L(0, y - 4, 18, y - 4, "teal-line")); b.append(T(24, y, "Saved at 4%", "xs"))
    b.append(L(130, y - 4, 148, y - 4, "c3-line dashed")); b.append(T(154, y, "Owed at 22.36%, never paid", "xs"))
    b.append(T(0, y + 26, "Real cards require payments; this shows what", "xs i2"))
    b.append(T(0, y + 42, "compounding does to any part left unpaid.", "xs i2"))
    write("both-ways", y + 50, b, "$2,000 over ten years, saved at 4% and owed at 22.36%",
          "Two lines from the same $2,000. Saved at 4% a year, it grows to about $2,080 after one year, $2,433 after "
          "five and $2,960 after ten. Owed on a credit card at 22.36% and never paid down, it grows to about $2,501 "
          "after one year, $6,115 after five and $18,699 after ten. Real cards require payments; this shows what "
          "compounding does to any part left unpaid.")



# ---------------------------------------------------------------- Spanish pilot (Nov 9): the overdraft page's two drawings
ES.update({
    "FICTIONAL · FOR ILLUSTRATION": "FICTICIO · SOLO DE EJEMPLO",
    # overdraft-statement
    "Starting balance": "Saldo inicial", "Lunch": "Almuerzo", "Coffee": "Café", "Movie rental": "Renta de película",
    "Gas": "Gasolina", "OVERDRAFT FEE": "CARGO POR SOBREGIRO", "Checking activity, Tuesday": "Movimientos del martes",
    "ITEM": "CONCEPTO", "AMOUNT": "MONTO", "BALANCE": "SALDO", "You owe the bank": "Le debe al banco",
    "$43 you didn't have, plus $105 in fees": "$43 que no tenía, más $105 en cargos",
    "The first fee was for being $4 short.": "El primer cargo fue porque le faltaban $4.",
    "Each fee is the same, whatever the amount.": "Cada cargo es igual, sin importar el monto.",
    "A fictional day of checking activity with three overdraft fees":
        "Un día ficticio de movimientos en la cuenta de cheques, con tres cargos por sobregiro",
    ("Starting balance $20. Lunch $18 leaves $2. Coffee $6 leaves minus $4, and a $35 overdraft fee makes it "
     "minus $39. A $9 movie rental makes it minus $48, and another $35 fee minus $83. Gas $30 makes it minus $113, "
     "and a third $35 fee minus $148. You owe the bank $148: the $43 you didn't have, plus $105 in fees. The first "
     "fee was for being $4 short."):
        ("Saldo inicial de $20. Un almuerzo de $18 deja $2. Un café de $6 deja menos $4, y un cargo por sobregiro de "
         "$35 lo lleva a menos $39. Una renta de película de $9 lo lleva a menos $48, y otro cargo de $35 a menos $83. "
         "Gasolina por $30 lo lleva a menos $113, y un tercer cargo de $35 a menos $148. Le debe al banco $148: los $43 "
         "que no tenía, más $105 en cargos. El primer cargo fue porque le faltaban $4."),
    # overdraft-opt-in
    "Settings": "Configuración", "Overdraft coverage for debit card": "Cobertura de sobregiro para",
    "and ATM transactions": "tarjeta de débito y cajeros", "Off": "No", "OFF": "NO", "ON": "SÍ",
    "Not enough money? The purchase": "¿No le alcanza? La compra",
    "is declined. No fee.": "se rechaza. Sin cargo.",
    "The bank may pay it and charge an": "El banco puede pagarla y cobrarle",
    "overdraft fee, often $35.": "un cargo por sobregiro, a menudo $35.",
    "Checks and automatic bill payments aren't": "Los cheques y los pagos automáticos",
    "covered by this switch.": "no dependen de este interruptor.",
    "A fictional bank-app setting for overdraft coverage, switched off":
        "Un ajuste ficticio de cobertura de sobregiro en la aplicación de un banco, desactivado",
    ("A settings screen with the switch for overdraft coverage on debit card and ATM transactions turned off. "
     "Off: if there isn't enough money, the purchase is declined, with no fee. On: the bank may pay it and charge "
     "an overdraft fee, often $35. Checks and automatic bill payments aren't covered by this switch."):
        ("Una pantalla de configuración con el interruptor de cobertura de sobregiro para tarjeta de débito y cajeros "
         "automáticos desactivado. No: si no hay suficiente dinero, la compra se rechaza, sin cargo. Sí: el banco puede "
         "pagarla y cobrarle un cargo por sobregiro, a menudo $35. Los cheques y los pagos automáticos no dependen de "
         "este interruptor."),
})
SPANISH = (overdraft_statement, overdraft_optin)


for fn in (credit_score_factors, overdraft_statement, overdraft_optin, card_minimum_box, card_three_ways, bnpl_calendar,
           payday_treadmill, cash_advance_timelines, car_balances, car_price_tag, rto_price_tag, rto_three_laptops,
           subs_statement, finfluencer_post, one_percent_curve, two_savers, pay_stub, student_balance, worry_ad,
           four_borrowers, betting_cost, gig_payouts, scam_texts, cosigner_notice, statement_marked, cushion_costs,
           one_name_reach, creep_bars, stub_split, two_balances, budget_bar, rate_gap, both_ways):
    fn()

LANG = "es"
for fn in SPANISH:
    fn()
LANG = "en"

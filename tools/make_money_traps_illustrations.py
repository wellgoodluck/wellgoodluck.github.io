#!/usr/bin/env python3
"""Generate the Money Traps illustrations (Nov 9) as SVG files in articles/illustrations/. Not run by the workflows:
run it by hand after changing a figure here (python3 tools/make_money_traps_illustrations.py), then upload the SVGs.
Every color comes from the classes in assets/site.css's illustration block (the companion colors for identity only); nothing here sets a color.
viewBox width is 360; text never smaller than 12.5 units."""
import html, math, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join("articles", "illustrations")
os.makedirs(OUT, exist_ok=True)
W = 360


def esc(s):
    return html.escape(str(s), quote=True)


def T(x, y, s, cls="", anchor="start", extra=""):
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
    b.append(T(244, 72, "AMOUNT", "cap", "end"))
    b.append(T(W - 14, 72, "BALANCE", "cap", "end"))
    b.append(L(14, 80, W - 14, 80, "rule"))
    y = top
    for lab, amt, bal, fee in rows:
        cy = y + rh / 2 + 5
        if fee:
            b.append(tag(14, y + 6, 108, 20, "OVERDRAFT FEE"))
            b.append(T(244, cy, money(amt), "b", "end"))
            b.append(T(W - 14, cy, money(bal), "b", "end"))
        else:
            b.append(T(14, cy, tx(lab), "i2" if amt is None else ""))
            if amt is not None:
                b.append(T(244, cy, money(amt), "", "end"))
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
    y = 62
    b.append(T(0, y - 14, "AS A PURCHASE, PAID IN FULL", "cap"))
    b.append(R(X(0), y, X(55) - X(0), 14, "wash"))
    b.append(L(X(0), y + 7, X(60), y + 7, "ink-line"))
    for d, lab in [(0, "Buy"), (30, "Statement"), (55, "Paid")]:
        b.append(L(X(d), y - 2, X(d), y + 16, "ink-line"))
        b.append(T(X(d), y + 32, lab, "xs i2", "middle" if d not in (0,) else "start"))
    b.append(T(X(27), y - 8, "grace period: no interest", "xs teal", "middle"))
    b.append(T(W, y + 54, "Cost: $0", "m", "end"))
    # advance
    y = 168
    b.append(T(0, y - 14, "AS A CASH ADVANCE", "cap"))
    # interest wedge growing from day 0
    b.append(f'<defs><pattern id="ca-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch-line"/></pattern></defs>')
    b.append(P(f"M{X(0)} {y + 7} L{X(60)} {y - 9} L{X(60)} {y + 7} Z", "", ' fill="url(#ca-hatch)"'))
    b.append(L(X(0), y + 7, X(60), y + 7, "ink-line"))
    b.append(L(X(0), y - 2, X(0), y + 16, "ink-line"))
    b.append(L(X(60), y - 2, X(60), y + 16, "ink-line"))
    b.append(tag(X(0), y + 22, 104, 20, "$25 fee, day 1"))
    b.append(T(X(60), y + 37, "Paid", "xs i2", "end"))
    b.append(T(X(36), y - 8, "interest from day 1", "xs i2", "middle"))
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


for fn in (credit_score_factors, overdraft_statement, overdraft_optin, card_minimum_box, card_three_ways, bnpl_calendar,
           payday_treadmill, cash_advance_timelines, car_balances, car_price_tag, rto_price_tag, rto_three_laptops,
           subs_statement, finfluencer_post, one_percent_curve, two_savers, pay_stub, student_balance, worry_ad):
    fn()

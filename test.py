file = open("data", 'r')
lines = file.readlines();


def makeProfit(b, s):
    return float(lines[s]) * 100 / 2 - float(lines[b]) * 120 / 2


buy = -1
sell = -1
count = 0
buys = []
sells = []
profit = 0.0
for i in range(0, len(lines) - 1):

    if float(lines[i]) < float(lines[i + 1]):
        if buy == -1:
            buy = i
            buys.append(i)
    elif float(lines[i]) >= float(lines[i + 1]) and buy != -1:
        if sell == -1:
            sell = i
            sells.append(i)
            count += 1
    if sell != -1 and buy != -1:
        buy = -1
        sell = -1

print(buys)
print(sells)
profit = 0.0
for j in range(0, len(buys) - 1):
    profit += makeProfit(buys[j], sells[j])
print(profit)

cancelled = []

for j in range(0, len(buys) - 1):
    if float(lines[sells[j]]) < float(lines[buys[j + 1]]) * 1.2:
        cancelled.append(j)

for j in cancelled:
    sells.remove(sells[j])
    buys.remove(buys[j + 1])

print(buys)
print(sells)

profit = 0.0
for j in range(0, len(buys) - 1):
    profit += makeProfit(buys[j], sells[j])
print(profit)

charges = []
discharges = []
for j in range(0, len(buys)):
    charges.append(60 * float(lines[buys[j]]))
    discharges.append(50 * float(lines[sells[j]]))
print(charges)
print(discharges)

# file = open("datat", 'r')
file = open("week", 'r')
# file = open("month", 'r')
# file = open("day", 'r')
# file = open("data", 'r')
lines = file.readlines()

datas = []
patterns = []
commands = []  # charge: 1, discharges: -1, noaction: 0
removeMask = []
runAgain = True

for l in lines:
    datas.append(float(l))
    commands.append(0)
    removeMask.append(0)
    patterns.append(-2)


def getPatterns():
    for i in range(0, len(datas) - 1):
        if removeMask[i] == 1:
            continue
        j = 1
        while removeMask[i + j] == 1 and i + j < len(removeMask):
            j += 1
        if i + j > len(removeMask):
            break
        if datas[i + j] - datas[i] > 0:
            patterns[i] = 1
        elif datas[i + j] - datas[i] < 0:
            patterns[i] = -1
        else:
            patterns[i] = 0


def getCommands():
    capacity = 0
    buy = False
    for i in range(0, len(datas) - 1):
        # print(capacity)

        if removeMask[i] == 0 and patterns[i] == 1 and commands[i] == 0 and capacity < 4 and not buy:
            if i + 4 - capacity < len(datas) - 1:
                tempCapacity = 0
                for j in range(i, i + 4 - capacity + 1):
                    tempCapacity += commands[j]
                if tempCapacity + capacity == 4:
                    continue
            commands[i] = 1
            removeMask[i] = 1
            global runAgain
            runAgain = True
            buy = True
        if removeMask[i] == 0 and patterns[i] == -1 and capacity > 0 and commands[i] == 0 and buy:
            commands[i] = -1
            removeMask[i] = 1
            buy = False
        if commands[i] == 1:
            capacity += 1
        elif commands[i] == -1:
            capacity -= 1


while runAgain:
    runAgain = False
    getPatterns()
    getCommands()
    # print(commands)
profit = 0.0
for i in range(0, len(commands)):
    if commands[i] == 1:
        profit -= datas[i] * 30
        # print (-datas[i]*30)
    elif commands[i] == -1:
        profit += datas[i] * 30 / 1.2
        # print(datas[i] * 30)
    # print(str(commands[i]))
#
for i in range(1, len(commands) + 1):
    print(str(commands[i - 1]))

print(profit)

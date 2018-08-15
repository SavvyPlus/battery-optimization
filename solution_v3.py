import scipy.io as sio

# file = open("datat", 'r')
# file = open("week", 'r')
file = open("month", 'r')
# file = open("day", 'r')
# file = open("data", 'r')
lines = file.readlines()

mat_contents = sio.loadmat('HH_Sim_Spot_1000_500eachVIC1_forBattery_2018-08-15.mat')
current = 0
next = 1


def max_profit(capacity, index, no_action, buy_action, sell_action):
    value = max(no_action, buy_action, sell_action)
    if value == no_action:
        paths[next][capacity] = paths[current][capacity]
        if len(paths[next][capacity]) <= index:
            paths[next][capacity] += '0'
        else:
            paths[next][capacity] = paths[next][capacity][:index] + '0' + paths[next][capacity][index + 1:]
    elif value == buy_action:
        paths[next][capacity] = paths[current][capacity - 1]
        if len(paths[next][capacity]) <= index:
            paths[next][capacity] += '1'
        else:
            paths[next][capacity] = paths[next][capacity][:index] + '1' + paths[next][capacity][index + 1:]
    elif value == sell_action:
        paths[next][capacity] = paths[current][capacity + 1]
        if len(paths[next][capacity]) <= index:
            paths[next][capacity] += '2'
        else:
            paths[next][capacity] = paths[next][capacity][:index] + '2' + paths[next][capacity][index + 1:]
    return value


for index_simulation in range(len(mat_contents['Spot_Sims'])):
    datas = []
    for i in range(len(mat_contents['Spot_Sims'])):
        # print (str(i) + ' ' + str(mat_contents['Spot_Sims'][i][0]))
        datas.append( mat_contents['Spot_Sims'][i][index_simulation])
    patterns = []
    dp = [[0.0] * 5 for i in range(2)]
    paths = [[[] for i in range(5)] for j in range(2)]
    path = []

    for i in range(2):
        for j in range(5):
            paths[i][j] = ''
            for k in range(j):
                paths[i][j] += '1'
    for i in range(1, len(datas)):
        sell = datas[i] * 30 / 1.2
        buy = - datas[i] * 30
        if 0 < i < 5:
            for k in range(0, i):
                dp[current][i] -= datas[k] * 30

        if i == 1:
            # dp[next][0] = max(dp[current][0], dp[current][1] + sell)
            # dp[next][1] = max(dp[current][1], dp[current][0] + buy)
            dp[next][0] = max_profit(0, i, dp[current][0], -100000, dp[current][1] + sell)
            dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy, -100000)

        if i == 2:
            # dp[next][1] = max(dp[next][1], dp[current][2] + sell)
            # dp[next][2] = max(dp[current][2], dp[current][1] + buy)
            dp[next][0] = max_profit(0, i, dp[current][0], -100000, dp[current][1] + sell)
            dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy, dp[current][2] + sell)
            dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy, -100000)

        if i == 3:
            # dp[next][2] = max(dp[next][2], dp[current][3] + sell)
            # dp[next][3] = max(dp[current][3], dp[current][2] + buy)
            dp[next][0] = max_profit(0, i, dp[current][0], -100000, dp[current][1] + sell)
            dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy, dp[current][2] + sell)
            dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy, dp[current][3] + sell)
            dp[next][3] = max_profit(3, i, dp[current][3], dp[current][2] + buy, -100000)

        if i > 3:
            # dp[next][3] = max(dp[next][3], dp[current][4] + sell)
            # dp[next][4] = max(dp[current][4], dp[current][3] + buy)
            dp[next][0] = max_profit(0, i, dp[current][0], -100000, dp[current][1] + sell)
            dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy, dp[current][2] + sell)
            dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy, dp[current][3] + sell)
            dp[next][3] = max_profit(3, i, dp[current][3], dp[current][2] + buy, dp[current][4] + sell)
            dp[next][4] = max_profit(4, i, dp[current][4], dp[current][3] + buy, -100000)

        temp = current
        current = next
        next = temp

    profit = 0.0
    for i in range(0, 5):
        profit = max(dp[current][i], profit)
        if profit == dp[current][i]:
            path = paths[current][i]

    print(profit)
    print(path)
    # for i in path:
    #     print(i)

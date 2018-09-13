from FileUtils import write_to

trigger_price = -100000
times_to_full_charge = 4

amount_per_charge = 120 / times_to_full_charge

# file = open("datat", 'r')
# file = open("week", 'r')
# file = open("month", 'r')
# file = open("day", 'r')
# file = open("daya", 'r')
# file = open("data", 'r')
file = open("real_data_" + str(int(amount_per_charge)) + "min")
# file = open("real_data_5min")
lines = file.readlines()
data = []

for l in lines:
    data.append(float(l))

prefix = str(int(amount_per_charge))
trigger_tag = '_trigger_' + str(trigger_price) if trigger_price > 0 else ''


def max_profit(capacity, index, no_action, buy_action, sell_action, paths, current, next):
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


def write_to_file(data, path):
    field_names = ['Time_Ending', 'Price', 'Dispatch', 'Energy Level', 'Discharge Energy (MWh)', 'Charge Energy (MWh)',
                   'Revenue', 'Cost', 'Profit']
    time_ending = open("Time_Ending")
    times = time_ending.readlines()
    rows = []
    count = 0
    for index in range(len(path)):
        row = {'price': data[index], 'Time_Ending': times[index]}
        if path[index] == '1':
            count += 1
            row['dispatch'] = 'charge'
            row['revenue'] = 0
            row['cost'] = data[index] * amount_per_charge
        elif path[index] == '2':
            row['dispatch'] = 'discharge'
            row['revenue'] = data[index] * amount_per_charge / 1.2
            row['cost'] = 0
            count -= 1
        else:
            row['dispatch'] = ''
            row['revenue'] = 0
            row['cost'] = 0
        row['profit'] = row['revenue'] - row['cost']
        row['energy level'] = count * amount_per_charge
        rows.append(row)
    write_to(prefix + '_mins_backcasting' + trigger_tag + '.csv', rows, field_names)


for index_simulation in range(1):
    dp = [[0.0] * (times_to_full_charge + 1) for i in range(2)]
    paths = [[[] for i in range(times_to_full_charge + 1)] for j in range(2)]
    path = []
    current = 0
    next = 1

    # print(len(datas))
    for i in range(2):
        for j in range(times_to_full_charge + 1):
            paths[i][j] = ''
            for k in range(j):
                paths[i][j] += '1'
    paths[0][0] = '0'
    for i in range(1, len(data)):
        sell = data[i] * amount_per_charge / 1.2
        buy = - data[i] * amount_per_charge
        if 0 < i < times_to_full_charge + 1:
            for k in range(0, i):
                dp[current][i] -= data[k] * amount_per_charge

        for j in range(i + 1 if i < times_to_full_charge else times_to_full_charge + 1):
            if j == 0:
                dp[next][j] = max_profit(j, i, dp[current][j], -10000000,
                                         dp[current][j + 1] + sell if data[i] > trigger_price else -10000000,
                                         paths,
                                         current,
                                         next)
            elif j == i or j == times_to_full_charge:
                dp[next][j] = max_profit(j, i, dp[current][j], dp[current][j - 1] + buy, -10000000, paths, current,
                                         next)

            elif 0 < j < i:
                dp[next][j] = max_profit(j, i, dp[current][j], dp[current][j - 1] + buy,
                                         dp[current][j + 1] + sell if data[i] > trigger_price else -10000000,
                                         paths,
                                         current, next)

        temp = current
        current = next
        next = temp

    profit = -1000
    for i in range(0, times_to_full_charge + 1):
        profit = max(dp[current][i], profit)
        if profit == dp[current][i]:
            path = paths[current][i]

    print(profit)
    print(path)

    write_to_file(data, path)
# for s in finalpaths:
#     file.write(str(s) + "\n")

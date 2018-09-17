from FileUtils import write_to


# trigger_price = 300  # 100 300
# times_to_full_charge = 8  # 4 8
# capacity_battery = 400
# prefix = str(30)  # minutes file

# file = open("datat", 'r')
# file = open("week", 'r')
# file = open("month", 'r')
# file = open("day", 'r')
# file = open("daya", 'r')
# file = open("data", 'r')

def main():
    prefixes = [30]

    trigger_price_array = [-1000000, 100, 300]
    capacity_battery_array = [200, 400]
    input_folder = 'inputs/'
    input_files = ["spot_0th_30min", "spot_5th_30min", "spot_25th_30min", "spot_50th_30min", "spot_75th_30min",
                   "spot_95th_30min", "spot_100th_30min"]

    for i in range(len(input_files)):
        file = open(input_folder + input_files[i])
        # file = open("real_data_5min")
        lines = file.readlines()
        data = []
        for l in lines:
            data.append(float(l))
        for prefix in prefixes:
            for trigger_price in trigger_price_array:
                for capacity_battery in capacity_battery_array:
                    times_to_full_charge = (60 / prefix) * (capacity_battery / 100)
                    run(data, int(times_to_full_charge), capacity_battery, input_files[i], str(prefix), trigger_price)


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


def write_to_file(data, path, amount_per_charge, input_file, prefix, appendix, trigger_tag):
    field_names = ['Time_Ending', 'Price', 'Dispatch', 'Energy Level', 'Discharge Energy (MWh)', 'Charge Energy (MWh)',
                   'Revenue', 'Cost', 'Profit']
    time_ending = open("Time_Ending_" + prefix)
    times = time_ending.readlines()
    rows = []
    count = 0
    for index in range(len(path)):
        row = {'Price': data[index], 'Time_Ending': times[index].replace('\n', '')}
        if path[index] == '1':
            count += 1
            row['Dispatch'] = 'Charge'
            row['Revenue'] = 0
            row['Cost'] = data[index] * amount_per_charge * 1.2
            row['Discharge Energy (MWh)'] = 0
            row['Charge Energy (MWh)'] = amount_per_charge * 1.2
        elif path[index] == '2':
            row['Dispatch'] = 'Discharge'
            row['Revenue'] = data[index] * amount_per_charge
            row['Cost'] = 0
            row['Discharge Energy (MWh)'] = amount_per_charge
            row['Charge Energy (MWh)'] = 0
            count -= 1
        else:
            row['Dispatch'] = ''
            row['Revenue'] = 0
            row['Cost'] = 0
            row['Discharge Energy (MWh)'] = 0
            row['Charge Energy (MWh)'] = 0
        row['Profit'] = row['Revenue'] - row['Cost']
        row['Energy Level'] = count * amount_per_charge
        rows.append(row)
    write_to("output/" + prefix + '_mins_forecasting' + trigger_tag + appendix + "_" + input_file + '.csv', rows,
             field_names)


def run(data, times_to_full_charge, capacity_battery, input_file, prefix, trigger_price):
    trigger_tag = '_trigger_' + str(trigger_price) if trigger_price > 0 else ''
    amount_per_charge = capacity_battery / times_to_full_charge
    appendix = "_battery capacity_" + str(capacity_battery)
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
        sell = data[i] * amount_per_charge
        buy = - data[i] * amount_per_charge * 1.2
        if 0 < i < times_to_full_charge + 1:
            for k in range(0, i):
                dp[current][i] -= data[k] * amount_per_charge * 1.2

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

    write_to_file(data, path, amount_per_charge, input_file, prefix, appendix, trigger_tag)


if __name__ == '__main__':
    main()

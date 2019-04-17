from FileUtils import write_to_
# Scenario : a half-hour rest is necessary after every discharge.

# trigger_price = 300  # 100 300
# times_to_full_charge = 8  # 4 8
# capacity_battery = 400
# prefix = str(30)  # minutes file

file = open("datat", 'r')
# file = open("week", 'r')
# file = open("month", 'r')
# file = open("day", 'r')
# file = open("daya", 'r')
# file = open("data", 'r')

lines = file.readlines()
datas = []

for l in lines:
    datas.append(float(l))


def main():
    prefixes = [30]
    trigger_price_array = [-100000]
    capacity_battery_array = [100]
    power = 100
    # scenarios = ['Spot_Price_sample.mat']
    scenarios = ['Spot_Price_smallsample.mat']

    # simulation_size = 3
    # simulation_start = 0
    all_size = 1
    length_simulation = 35
    fragments = 1
    mat_file_key = 'Spot_Sims'

    for scenario in scenarios:
        # mat_contents = sio.loadmat('inputs/' + scenario, driver='family')
        for prefix in prefixes:
            for trigger_price in trigger_price_array:
                for capacity_battery in capacity_battery_array:

                    print(str(scenario) + "_" + str(trigger_price) + "_" + str(capacity_battery))

                    times_to_full_charge = (60 / prefix) * (capacity_battery / power)
                    amount_per_charge = capacity_battery / times_to_full_charge
                    trigger_tag = '_trigger_' + str(trigger_price) if trigger_price > 0 else ''
                    appendix = "_battery capacity_" + str(capacity_battery)

                    # comm = MPI.COMM_WORLD
                    # rank = comm.Get_rank()
                    # size = comm.Get_size()

                    for i in range(fragments):
                        # if i == rank:
                        paths = []

                        simulation_size = int(all_size / fragments)
                        simulation_start = i * simulation_size
                        for index_simulation in range(simulation_start, simulation_start + simulation_size):
                            data = datas
                            path = run(data, int(times_to_full_charge), capacity_battery, trigger_price)
                            paths.append(path)
                            datas.append(data)
                            print_all(path, data)
                        # write_to_file(datas, paths, amount_per_charge, "scenario_" + str(scenario), appendix,
                        #               trigger_tag, simulation_start, simulation_size, length_simulation)


def print_all(path, data):
    for i, j in zip(path, data):
        print(i, j)


def write_to_file(datas, paths, amount_per_charge, input_file, appendix, trigger_tag, simulation_start,
                  simulation_size, length_simulation):
    rows = []
    for index_simulation in range(simulation_size):
        row = []
        for index_row in range(length_simulation):
            revenue = 0
            cost = 0
            if paths[index_simulation][index_row] == '1':
                revenue = 0
                # cost = datas[index_simulation][index_row] * amount_per_charge * 1.2
                cost = 1
            elif paths[index_simulation][index_row] == '2':
                # revenue = datas[index_simulation][index_row] * amount_per_charge
                revenue = 1
                cost = 0
            row.append(revenue - cost)
        rows.append(row)
    write_to_(
        f"output/30_mins_forecasting_{input_file}_{trigger_tag}_{appendix}_{simulation_start}-{simulation_size + simulation_start}.csv",
        rows)


def max_profit(capacity, index, no_action, buy_action, sell_action_1, sell_action_2, paths, current, next, pre):
    value = max(no_action, buy_action, sell_action_1, sell_action_2)
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
    elif value == sell_action_1:
        paths[next][capacity] = paths[current][capacity + 1]
        if len(paths[next][capacity]) <= index:
            paths[next][capacity] += '2'
        else:
            paths[next][capacity] = paths[next][capacity][:index] + '2' + paths[next][capacity][index + 1:]
    elif value == sell_action_2:
        paths[next][capacity] = paths[pre][capacity + 1]
        if len(paths[next][capacity]) <= index:
            paths[next][capacity] += '20'
        else:
            paths[next][capacity] = paths[next][capacity][:index] + '20' + paths[next][capacity][index + 2:]
    return value


def run(data, times_to_full_charge, capacity_battery, trigger_price):
    amount_per_charge = capacity_battery / times_to_full_charge

    history_size = 3
    loss_rate = 1.2

    boundary = -10000000

    dp = [[0.0] * (times_to_full_charge + 1) for i in range(history_size)]
    paths = [[[] for i in range(times_to_full_charge + 1)] for j in range(history_size)]
    path = []
    current_i = 0
    next_i = 1
    pre_i = 2

    for i in range(history_size):
        for j in range(times_to_full_charge + 1):
            paths[i][j] = ''
            for k in range(j):
                paths[i][j] += '1'
    paths[0][0] = '0'
    for i in range(1, len(data)):
        sell = data[i] * amount_per_charge
        buy = - data[i] * amount_per_charge * loss_rate
        if 0 < i < times_to_full_charge + 1:
            for k in range(0, i):
                dp[current_i][i] -= data[k] * amount_per_charge * loss_rate

        for j in range(i + 1 if i < times_to_full_charge else times_to_full_charge + 1):
            # if paths[current_i][j][i - 1] == '2':
            #     dp[next_i][j] = max_profit(j, i, dp[current_i][j], -10000000,
            #                                -10000000,-10000000,
            #                                paths,
            #                                current_i,
            #                                next_i, pre_i)
            #     continue

            if j == 0:
                sell_amount_1 = dp[current_i][j + 1] + sell if data[i] > trigger_price and paths[current_i][j + 1][
                    i - 1] != '2' else boundary
                sell_amount_2 = (dp[pre_i][j + 1] + sell) if data[i] > trigger_price and paths[pre_i][j + 1][
                    i - 2] != '2' else boundary
                dp[next_i][j] = max_profit(j, i, dp[current_i][j], boundary,
                                           sell_amount_1, sell_amount_2,
                                           paths,
                                           current_i,
                                           next_i, pre_i)
            elif j == i or j == times_to_full_charge:
                buy_amount = dp[current_i][j - 1] + buy if paths[current_i][j - 1][i - 1] != '2' else boundary

                dp[next_i][j] = max_profit(j, i, dp[current_i][j], buy_amount, boundary, boundary, paths,
                                           current_i,
                                           next_i, pre_i)

            elif 0 < j < i:
                buy_amount = dp[current_i][j - 1] + buy if paths[current_i][j - 1][i - 1] != '2' else boundary
                sell_amount_1 = dp[current_i][j + 1] + sell if data[i] > trigger_price and paths[current_i][j + 1][
                    i - 1] != '2' else boundary
                sell_amount_2 = (dp[pre_i][j + 1] + sell) if data[i] > trigger_price and paths[pre_i][j + 1][
                    i - 2] != '2' else boundary
                dp[next_i][j] = max_profit(j, i, dp[current_i][j], buy_amount, sell_amount_1
                                           , sell_amount_2,
                                           paths,
                                           current_i, next_i, pre_i)

        current_i = (1 + current_i) % history_size
        next_i = (1 + next_i) % history_size
        pre_i = (1 + pre_i) % history_size

    profit = -1000
    for i in range(0, times_to_full_charge + 1):
        profit = max(dp[current_i][i], profit)
        if profit == dp[current_i][i]:
            path = paths[current_i][i]

    # print(profit)
    # print(path)
    return path


if __name__ == '__main__':
    main()

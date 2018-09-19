from FileUtils import write_to
from mpi4py import MPI
import scipy.io as sio


# with multi threads running on multi cores
# mpiexec -n 4 python solution_v4.py

def main():
    mat_contents = sio.loadmat('inputs/SpotPriceVREAS.mat')
    mat_key = 'SpotPrices'
    # mat_contents = []
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    all_size = 1000
    print(rank)
    length = int(all_size / (size - 1))
    print(length)

    if rank == 0:
        prefixes = [30]
        trigger_price_array = [300]
        capacity_battery_array = [400]
        scenarios = range(1)

        for scenario in scenarios:
            for prefix in prefixes:
                for trigger_price in trigger_price_array:
                    for capacity_battery in capacity_battery_array:
                        parameters = {'scenario': scenario, 'prefix': prefix, 'trigger': trigger_price,
                                      'capacity': capacity_battery, 'command': 'run'}
                        times_to_full_charge = (60 / prefix) * (capacity_battery / 100)
                        amount_per_charge = capacity_battery / times_to_full_charge
                        appendix = "_battery capacity_" + str(capacity_battery)
                        trigger_tag = '_trigger_' + str(trigger_price) if trigger_price > 0 else ''

                        comm.bcast(parameters, root=0)
                        paths = {}
                        for ii in range(size - 1):
                            path = comm.recv()
                            paths = {paths, path}
                        write_to_file(mat_contents[mat_key], paths, amount_per_charge, "scenario_" + str(scenario),
                                      appendix,
                                      trigger_tag)
                        # merge_data(amount_per_charge, "scenario_" + str(scenario), appendix, trigger_tag, size)
        parameters = {'command': 'stop'}
        comm.bcast(parameters, root=0)

    elif rank == size - 1:
        start = length * (rank - 1)
        end = all_size - 1
        print(str(start) + ' ' + str(end))
        parameters = comm.bcast(None, root=0)
        while parameters['command'] == 'run':
            data = multi_simulation(mat_contents[mat_key], int(start), int(end), parameters)
            comm.send(data, dest=0)
            parameters = comm.bcast(None, root=0)
    else:
        start = length * (rank - 1)
        end = length * rank - 1
        print(str(start) + ' ' + str(end))
        parameters = comm.bcast(None, root=0)
        while parameters['command'] == 'run':
            data = multi_simulation(mat_contents[mat_key], int(start), int(end), parameters)
            comm.send(data, dest=0)
            parameters = comm.bcast(None, root=0)


def multi_simulation(mat_contents, start, end, parameters):
    paths = {}
    capacity_battery = parameters['capacity']
    trigger_price = parameters['trigger']
    prefix = parameters['prefix']

    times_to_full_charge = (60 / prefix) * (capacity_battery / 100)

    for index_simulation in range(start, end + 1):
        data = []
        for l in range(210672):
            data.append(float(mat_contents[l][index_simulation]))

        path = run(data, int(times_to_full_charge), capacity_battery, trigger_price)
        paths[index_simulation] = path

        print(index_simulation)
    return paths


def write_to_file(mat_contents, paths, amount_per_charge, input_file, appendix, trigger_tag):
    field_names = []
    for key in range(len(paths)):
        field_names.append("profit_" + str(key))
    rows = []
    for index_row in range(len(paths[0])):
        row = {}
        print("row " + str(index_row))

        for index_simulation in range(len(paths)):
            revenue = 0
            cost = 0
            if paths[index_simulation][index_row] == '1':
                revenue = 0
                cost = mat_contents[index_row][index_simulation] * amount_per_charge * 1.2
            elif paths[index_simulation][index_row] == '2':
                revenue = mat_contents[index_row][index_simulation] * amount_per_charge
                cost = 0
            row["profit_" + str(index_simulation)] = revenue - cost
        rows.append(row)
    write_to("output/30_mins_forecasting" + "_" + input_file + trigger_tag + appendix + '.csv', rows,
             field_names)


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


def run(data, times_to_full_charge, capacity_battery, trigger_price):
    amount_per_charge = capacity_battery / times_to_full_charge

    dp = [[0.0] * (times_to_full_charge + 1) for i in range(2)]
    paths = [[[] for i in range(times_to_full_charge + 1)] for j in range(2)]
    path = []
    current = 0
    next = 1

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

    # print(profit)
    # print(path)
    return path


if __name__ == '__main__':
    main()

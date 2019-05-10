from FileUtils import write_to_
import heapq
import sys
from os import walk
import scipy.io as sio
import multiprocessing

# Scenario : three half-hours rest is necessary after every second discharge for one hour battery.
# For every iteration, record more states for each capacity and pick up topK of them to do the next iteration.
# Use heap to achieve TopK in a log(K)*n complexity in time space.

plot = []


def load_inputs(folder):
    f = []
    for (dirpath, dirnames, filenames) in walk(folder):
        f.extend(filenames)
    return f


def main():
    # scenario_index = sys.argv[1]

    prefixes = [30]
    trigger_price_array = [-100000]
    capacity_battery_array = [360]
    power = 90
    # scenarios = ['Spot_Price_sample.mat']
    scenario_input_files = load_inputs('inputs')

    # simulation_size = 3
    # simulation_start = 0
    process_size = 4
    mat_file_key = 'Spot_Sims'
    thread_count = 0

    # scenario = scenario_input_files[int(scenario_index)]
    for scenario in scenario_input_files:
        if 'DS_Store' in scenario:
            continue
        print(scenario)
        mat_contents = sio.loadmat('inputs/' + scenario)
        length_simulation = mat_contents[mat_file_key].shape[0]
        all_size = mat_contents[mat_file_key].shape[1]
        # all_size =20
        print(length_simulation)
        for prefix in prefixes:
            for trigger_price in trigger_price_array:
                for capacity_battery in capacity_battery_array:

                    # print(str(scenario) + "_" + str(trigger_price) + "_" + str(capacity_battery))

                    times_to_full_charge = (60 / prefix) * (capacity_battery / power)
                    amount_per_charge = capacity_battery / times_to_full_charge
                    trigger_tag = '_trigger_' + str(trigger_price) if trigger_price > 0 else ''
                    appendix = "_battery capacity_" + str(capacity_battery)

                    for i in range(process_size):
                        # if i == rank:
                        new_thread = MyThread(thread_count, i, all_size, process_size, length_simulation, mat_contents,
                                              times_to_full_charge,
                                              capacity_battery,
                                              trigger_price, amount_per_charge, scenario, appendix, trigger_tag,
                                              mat_file_key)
                        new_thread.start()
                        thread_count += 1
                        # new_thread.join()


class MyThread(multiprocessing.Process):

    def __init__(self, process_count, i, all_size, thread_size, length_simulation, mat_contents, times_to_full_charge,
                 capacity_battery,
                 trigger_price, amount_per_charge, scenario, appendix, trigger_tag, mat_file_key):
        multiprocessing.Process.__init__(self)
        self.process_count = process_count
        self.i = i
        self.all_size = all_size
        self.thread_size = thread_size
        self.length_simulation = length_simulation
        self.mat_contents = mat_contents
        self.times_to_full_charge = times_to_full_charge
        self.capacity_battery = capacity_battery
        self.trigger_price = trigger_price
        self.amount_per_charge = amount_per_charge
        self.scenario = scenario
        self.appendix = appendix
        self.trigger_tag = trigger_tag
        self.mat_file_key = mat_file_key

    def run(self):
        paths = []
        datas = []

        simulation_size = int(self.all_size / self.thread_size)
        simulation_start = self.i * simulation_size
        for index_simulation in range(simulation_start, simulation_start + simulation_size):
            print(f'Job {self.process_count}: {index_simulation - simulation_start} / {simulation_size}')
            data = []
            for l in range(self.length_simulation):
                data.append(float(self.mat_contents[self.mat_file_key][l][index_simulation]))
            path = run(data, int(self.times_to_full_charge), self.capacity_battery, self.trigger_price)
            paths.append(path)
            # datas.append(data)
        write_to_file(datas, paths, self.amount_per_charge, "scenario_" + str(self.scenario), self.appendix,
                      self.trigger_tag, simulation_start, simulation_size, self.length_simulation)


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

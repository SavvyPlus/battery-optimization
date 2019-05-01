from FileUtils import write_to_
import heapq
import sys
from os import walk
import scipy.io as sio

# Scenario : three half-hours rest is necessary after every second discharge for one hour battery.
# For every iteration, record more states for each capacity and pick up topK of them to do the next iteration.
# Use heap to achieve TopK in a log(K)*n complexity in time space.

plot=[]


def load_inputs(folder):
    f = []
    for (dirpath, dirnames, filenames) in walk(folder):
        f.extend(filenames)
    return f


def main():
    scenario_index = sys.argv[1]
    top_k = 25

    prefixes = [30]
    trigger_price_array = [-100000]
    capacity_battery_array = [100]
    power = 100
    # scenarios = ['Spot_Price_sample.mat']
    scenario_input_files = load_inputs('inputs')

    # simulation_size = 3
    # simulation_start = 0
    all_size = 4500
    fragments = 1
    mat_file_key = 'Spot_Sims'

    # for scenario in scenario_input_files:
    scenario = scenario_input_files[int(scenario_index)]
    print(scenario)
    mat_contents = sio.loadmat('inputs/' + scenario)
    length_simulation = mat_contents[mat_file_key].shape[0]
    print(length_simulation)
    for prefix in prefixes:
        for trigger_price in trigger_price_array:
            for capacity_battery in capacity_battery_array:

                # print(str(scenario) + "_" + str(trigger_price) + "_" + str(capacity_battery))

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
                    datas = []

                    simulation_size = int(all_size / fragments)
                    simulation_start = i * simulation_size
                    for index_simulation in range(simulation_start, simulation_start + simulation_size):
                        print(index_simulation)
                        data = []
                        for l in range(length_simulation):
                            data.append(float(mat_contents[mat_file_key][l][index_simulation]))
                        path = run(data, int(times_to_full_charge), capacity_battery, trigger_price, top_k)
                        paths.append(path)
                        datas.append(data)
                    write_to_file(datas, paths, amount_per_charge, "scenario_" + str(scenario), appendix,
                                  trigger_tag, simulation_start, simulation_size, length_simulation)


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


def max_profit(capacity, index, no_action, buy_action, sell_action_1, states, current, next):
    value = max(no_action, buy_action, sell_action_1)

    if value == no_action:
        states[next][capacity].discharge_count = states[current][capacity].discharge_count
        states[next][capacity].path = states[current][capacity].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '0'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '0' + states[next][capacity].path[
                                                                                      index + 1:]
    elif value == buy_action:
        states[next][capacity].discharge_count = states[current][capacity - 1].discharge_count
        states[next][capacity].path = states[current][capacity - 1].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '1'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '1' + states[next][capacity].path[
                                                                                      index + 1:]
    elif value == sell_action_1:
        states[next][capacity].discharge_count = states[current][capacity + 1].discharge_count
        states[next][capacity].discharge()
        states[next][capacity].path = states[current][capacity + 1].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '2'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '2' + states[next][capacity].path[
                                                                                      index + 1:]
    return value


def run(data, times_to_full_charge, capacity_battery, trigger_price, top_k):
    amount_per_charge = capacity_battery / times_to_full_charge

    history_size = 20
    loss_rate = 1.2

    boundary = -10000000

    states = []
    for i in range(history_size):
        one_row = []
        for j in range(times_to_full_charge + 1):
            one_row.append([])
        states.append(one_row)

    path = []
    current_i = 0
    next_i = 1

    new_state = State(times_to_full_charge)
    new_state.path = '0'
    states[0][0].append(new_state)

    new_state = State(times_to_full_charge)
    new_state.value -= data[0] * amount_per_charge * loss_rate
    new_state.path = '1'
    states[0][1].append(new_state)

    for i in range(1, len(data)):
        sell = data[i] * amount_per_charge
        buy = - data[i] * amount_per_charge * loss_rate
        # if 0 < i < times_to_full_charge + 1:
        #     new_state = State(times_to_full_charge)
        #     for k in range(0, i):
        #         new_state.value -= data[k] * amount_per_charge * loss_rate
        #     states[current_i][i].append(new_state)

        for j in range(i + 2 if i < times_to_full_charge else times_to_full_charge + 1):

            states[next_i][j].clear()
            if j == 0:
                discharge_action(data, times_to_full_charge, trigger_price, sell, states, current_i, next_i, i, j)
                no_action(times_to_full_charge, states, current_i, next_i, i, j)
            elif j == i or j == times_to_full_charge:
                no_action(times_to_full_charge, states, current_i, next_i, i, j)
                charge_action(data, times_to_full_charge, trigger_price, buy, states, current_i, next_i, i, j)
            elif 0 < j < i:
                discharge_action(data, times_to_full_charge, trigger_price, sell, states, current_i, next_i, i, j)
                no_action(times_to_full_charge, states, current_i, next_i, i, j)
                charge_action(data, times_to_full_charge, trigger_price, buy, states, current_i, next_i, i, j)

            states[next_i][j] = heapq.nlargest(top_k, states[next_i][j], key=lambda x: x.value)

        current_i = (1 + current_i) % history_size
        next_i = (1 + next_i) % history_size

    profit = -1000
    for index in range(0, times_to_full_charge + 1):
        the_best_state = heapq.nlargest(1, states[current_i][index], lambda x: x.value)
        if the_best_state[0].value > profit:
            profit = the_best_state[0].value
            path = the_best_state[0].path

    # print(top_k,profit)
    # plot.append(profit)
    # print(path)
    return path


def discharge_action(data, times_to_full_charge, trigger_price, sell_amount, states, current_i, next_i, i, j):
    for one_state in states[current_i][j + 1]:
        if one_state.can_dispatch(i - 1) and data[i] > trigger_price:
            temp_state = State(times_to_full_charge)
            temp_state.initialise(one_state)
            temp_state.value = temp_state.value + sell_amount
            temp_state.path += '2'
            temp_state.discharge()
            states[next_i][j].append(temp_state)


def charge_action(data, times_to_full_charge, trigger_price, buy_amount, states, current_i, next_i, i, j):
    for one_state in states[current_i][j - 1]:
        if one_state.can_dispatch(i - 1) and data[i] > trigger_price:
            temp_state = State(times_to_full_charge)
            temp_state.initialise(one_state)
            temp_state.value = temp_state.value + buy_amount
            temp_state.path += '1'
            states[next_i][j].append(temp_state)


def no_action(times_to_full_charge, states, current_i, next_i, i, j):
    for one_state in states[current_i][j]:
        temp_state = State(times_to_full_charge)
        temp_state.initialise(one_state)
        temp_state.path += '0'
        states[next_i][j].append(temp_state)


class State:
    path = ''
    value = 0
    discharge_count = 0
    full_charge_times = 0

    def __init__(self, full_charge_times):
        self.full_charge_times = full_charge_times

    def get_p(self, i):
        if len(self.path) > i:
            return self.path[i]
        else:
            return None

    def discharge(self):
        self.discharge_count += 1

    def can_dispatch(self, current):
        if self.discharge_count == 0:
            return True
        discharge_c = self.discharge_count
        if discharge_c % self.full_charge_times == 0 and '2' not in self.path[current - 2:]:
            return True
        if discharge_c % self.full_charge_times != 0:
            return True
        return False

    def initialise(self, s):
        self.path = s.path
        self.value = s.value
        self.discharge_count = s.discharge_count


if __name__ == '__main__':
    main()

from FileUtils import write_to_

# Scenario : three half-hours rest is necessary after every second discharge for one hour battery.

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


def max_profit(capacity, index, no_action, buy_action, sell_action_1, sell_action_2, states, current, next):
    value = max(no_action, buy_action, sell_action_1, sell_action_2)
    if value == no_action:
        states[next][capacity].path = states[current][capacity].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '0'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '0' + states[next][capacity].path[
                                                                                      index + 1:]
    elif value == buy_action:
        states[next][capacity].path = states[current][capacity - 1].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '1'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '1' + states[next][capacity].path[
                                                                                      index + 1:]
    elif value == sell_action_1:
        states[next][capacity].discharge()
        states[next][capacity].path = states[current][capacity + 1].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '2'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '2' + states[next][capacity].path[
                                                                                      index + 1:]
    elif value == sell_action_2:
        states[next][capacity].discharge()
        states[next][capacity].path = states[current - 3][capacity + 1].path
        if len(states[next][capacity].path) <= index:
            states[next][capacity].path += '2000'
        else:
            states[next][capacity].path = states[next][capacity].path[:index] + '2000' + states[next][capacity].path[
                                                                                         index + 2:]
    return value


def run(data, times_to_full_charge, capacity_battery, trigger_price):
    amount_per_charge = capacity_battery / times_to_full_charge

    history_size = len(data)
    loss_rate = 1.2

    boundary = -10000000

    states = [[State(times_to_full_charge)] * (times_to_full_charge + 1) for i in range(history_size)]

    path = []
    current_i = 0
    next_i = 1

    for i in range(history_size):
        for j in range(times_to_full_charge + 1):
            for k in range(j):
                states[i][j].path += '1'
    states[0][0].path = '0'
    for i in range(1, len(data)):
        sell = data[i] * amount_per_charge
        buy = - data[i] * amount_per_charge * loss_rate
        if 0 < i < times_to_full_charge + 1:
            for k in range(0, i):
                states[current_i][i].value -= data[k] * amount_per_charge * loss_rate

        for j in range(i + 1 if i < times_to_full_charge else times_to_full_charge + 1):

            if j == 0:
                sell_amount_1 = boundary
                if not states[ ][j + 1].is_next_full_charge() and data[i] > trigger_price:
                    sell_amount_1 = states[current_i][j + 1].value + sell

                sell_amount_2 = boundary
                if current_i - 3 >= 0 and states[current_i - 3][j + 1].is_next_full_charge() and data[i] > trigger_price:
                    sell_amount_2 = states[current_i - 3][j + 1].value + sell

                states[next_i][j].value = max_profit(j, i, states[current_i][j].value, boundary,
                                                     sell_amount_1, sell_amount_2,
                                                     states,
                                                     current_i,
                                                     next_i)
            elif j == i or j == times_to_full_charge:
                buy_amount = boundary
                if states[current_i][j - 1].can_charge(current_i):
                    buy_amount = states[current_i][j - 1].value + buy

                states[next_i][j].value = max_profit(j, i, states[current_i][j].value, buy_amount, boundary, boundary,
                                                     states,
                                                     current_i,
                                                     next_i)

            elif 0 < j < i:
                buy_amount = boundary
                if states[current_i][j - 1].can_charge(current_i):
                    buy_amount = states[current_i][j - 1].value + buy

                sell_amount_1 = boundary
                if not states[current_i][j + 1].is_next_full_charge() and data[i] > trigger_price:
                    sell_amount_1 = states[current_i][j + 1].value + sell

                sell_amount_2 = boundary
                if current_i - 3 >= 0 and states[current_i - 3][j + 1].is_next_full_charge() and data[i] > trigger_price:
                    sell_amount_2 = states[current_i - 3][j + 1].value + sell

                states[next_i][j].value = max_profit(j, i, states[current_i][j].value, buy_amount, sell_amount_1
                                                     , sell_amount_2,
                                                     states,
                                                     current_i, next_i)

        current_i = (1 + current_i) % history_size
        next_i = (1 + next_i) % history_size

    profit = -1000
    for i in range(0, times_to_full_charge + 1):
        profit = max(states[current_i][i].value, profit)
        if profit == states[current_i][i].value:
            path = states[current_i][i].path

    # print(profit)
    # print(path)
    return path


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

    def is_next_full_charge(self):
        return (self.discharge_count + 1) % self.full_charge_times == 0

    def discharge(self):
        self.discharge_count += 1

    def can_charge(self, current):
        discharge_c = self.discharge_count
        for i in range(1, 4):
            if discharge_c % self.full_charge_times == 0:
                return False
            if self.get_p(current - i) == '2':
                discharge_c -= 1
        return True


if __name__ == '__main__':
    main()

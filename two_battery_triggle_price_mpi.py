# with multi threads running on multi cores
# mpiexec -n 4 python solution_v4.py
from mpi4py import MPI
import scipy.io as sio
import json

mat_contents = sio.loadmat('HH_Sim_Spot_1000_500eachVIC1_forBattery_2018-08-15.mat')
# mat_contents = []
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
all_size = 1000
triggle_price = 300


def exec_stimulation(start, end):
    final_paths = {}
    for index_simulation in range(start, end + 1):
        # print(index_simulation)
        datas = []
        for i in range(len(mat_contents['Spot_Sims'])):
            # print (str(i) + ' ' + str(mat_contents['Spot_Sims'][i][0]))
            datas.append(mat_contents['Spot_Sims'][i][index_simulation])
        dp = [[0.0] * 5 for i in range(2)]
        paths = [[[] for i in range(5)] for j in range(2)]
        path = []
        current = 0
        next = 1

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
                dp[next][0] = max_profit(0, i, dp[current][0], -100000,
                                         dp[current][1] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current,
                                         next)
                dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy, -100000, paths, current, next)

            if i == 2:
                # dp[next][1] = max(dp[next][1], dp[current][2] + sell)
                # dp[next][2] = max(dp[current][2], dp[current][1] + buy)
                dp[next][0] = max_profit(0, i, dp[current][0], -100000,
                                         dp[current][1] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy,
                                         dp[current][2] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy, -100000, paths, current, next)

            if i == 3:
                # dp[next][2] = max(dp[next][2], dp[current][3] + sell)
                # dp[next][3] = max(dp[current][3], dp[current][2] + buy)
                dp[next][0] = max_profit(0, i, dp[current][0], -100000,
                                         dp[current][1] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy,
                                         dp[current][2] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy,
                                         dp[current][3] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][3] = max_profit(3, i, dp[current][3], dp[current][2] + buy, -100000, paths, current, next)

            if i > 3:
                # dp[next][3] = max(dp[next][3], dp[current][4] + sell)
                # dp[next][4] = max(dp[current][4], dp[current][3] + buy)
                dp[next][0] = max_profit(0, i, dp[current][0], -100000,
                                         dp[current][1] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][1] = max_profit(1, i, dp[current][1], dp[current][0] + buy,
                                         dp[current][2] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][2] = max_profit(2, i, dp[current][2], dp[current][1] + buy,
                                         dp[current][3] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][3] = max_profit(3, i, dp[current][3], dp[current][2] + buy,
                                         dp[current][4] + sell if datas[i] > triggle_price else -10000000, paths,
                                         current, next)
                dp[next][4] = max_profit(4, i, dp[current][4], dp[current][3] + buy, -100000, paths, current, next)

            temp = current
            current = next
            next = temp

        profit = 0.0
        for i in range(0, 5):
            profit = max(dp[current][i], profit)
            if profit == dp[current][i]:
                path = paths[current][i]

        # print(index_simulation)
        # print(profit)

        final_paths[index_simulation] = path
    return final_paths


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


def write_data_to_file(data, file):
    for k in data.keys():
        file.write(str(k) + " " + str(data[k]) + "\n")


print(rank)
length = int(all_size / (size - 1))
print(length)
if rank == 0:
    file = open("Dispatches_1000_stimulation_triggle_300", 'w')
    for ii in range(size - 1):
        data = comm.recv()
        write_data_to_file(data, file)
elif rank == size - 1:
    start = length * (rank - 1)
    end = all_size - 1
    print(str(start) + ' ' + str(end))
    data = exec_stimulation(int(start), int(end))
    comm.send(data, dest=0)
else:
    start = length * (rank - 1)
    end = length * rank - 1
    print(str(start) + ' ' + str(end))
    data = exec_stimulation(int(start), int(end))
    comm.send(data, dest=0)

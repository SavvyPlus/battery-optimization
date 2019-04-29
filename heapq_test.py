import heapq
from any_hours_battery_rest_period_small_data_v3 import State
import random

state_list = []
for i in range(10):
    temp = random.randint(1, 100)
    print(temp)
    state_list.append(State(temp))

return_list = heapq.nlargest(4, state_list, key=lambda x: x.full_charge_times)

print('\n')

for i in return_list:
    print(i.full_charge_times)

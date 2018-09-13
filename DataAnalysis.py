import scipy.io as sio
from datetime import date
import csv

discharge = '2'
charge = '1'

def get_data_size(dates):
    return ((dates[1] - dates[0]).days + 1) * 48


def get_date_quarter(year, quarter):
    start_date, end_date = 0, 0
    if quarter == 1:
        start_date, end_date = date(year, 1, 1), date(year, 3, 31)
    elif quarter == 2:
        start_date, end_date = date(year, 4, 1), date(year, 6, 30)
    elif quarter == 3:
        start_date, end_date = date(year, 7, 1), date(year, 9, 30)
    elif quarter == 4:
        start_date, end_date = date(year, 10, 1), date(year, 12, 31)
    return start_date, end_date


def get_date_financial_year(year):
    return date(year, 7, 1), date(year + 1, 6, 30)


def get_date_calendar_year(year):
    return date(year, 1, 1), date(year, 12, 31)


def count_discharge_or_charge(dispatches, start, size, type):
    count = 0
    for ii in range(start, start + size):
        if dispatches[ii] == type:
            count += 1
    return count


def revenue_cost(dispatches, spot_prices, start, size, type):
    total = 0
    for ii in range(start, start + size):
        if dispatches[ii] == type:
            total += spot_prices[ii] * 30
    return total


def generate_one_stimulation_data(dispatches, spot_prices, index_start, data_size):
    charge_count_row = {'item': 'charge_count'}
    discharge_count_row = {'item': 'discharge_count'}
    revenue_row = {'item': 'revenue'}
    charge_energy_row = {'item': 'charge_energy'}
    discharge_energy_row = {'item': 'discharge_energy'}
    cost_row = {'item': 'cost'}
    profit_row = {'item': 'profit'}

    for ii in range(2019, 2031):
        for jj in range(1, 5):
            field_name = str(ii % 100) + '-' + 'Q' + str(jj)
            discharge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                        data_size[field_name],
                                                                        discharge)
            charge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                     data_size[field_name],
                                                                     charge)
            discharge_energy_row[field_name] = discharge_count_row[field_name] * 30
            charge_energy_row[field_name] = charge_count_row[field_name] * 30
            revenue_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                                   data_size[field_name],
                                                   discharge)
            cost_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                                data_size[field_name],
                                                charge)
            profit_row[field_name] = revenue_row[field_name] - cost_row[field_name]
        if ii != 2030:
            field_name = 'FY-' + str(ii % 100) + '/' + str(ii % 100 + 1)
            discharge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                        data_size[field_name],
                                                                        discharge)
            charge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                     data_size[field_name],
                                                                     charge)
            discharge_energy_row[field_name] = discharge_count_row[field_name] * 30
            charge_energy_row[field_name] = charge_count_row[field_name] * 30
            revenue_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                                   data_size[field_name],
                                                   discharge)
            cost_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                                data_size[field_name],
                                                charge)
            profit_row[field_name] = revenue_row[field_name] - cost_row[field_name]

        field_name = 'Cal-' + str(ii % 100)
        discharge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                    data_size[field_name],
                                                                    discharge)
        charge_count_row[field_name] = count_discharge_or_charge(dispatches, index_start[field_name],
                                                                 data_size[field_name],
                                                                 charge)
        discharge_energy_row[field_name] = discharge_count_row[field_name] * 30
        charge_energy_row[field_name] = charge_count_row[field_name] * 30
        revenue_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                               data_size[field_name],
                                               discharge)
        cost_row[field_name] = revenue_cost(dispatches, spot_prices, index_start[field_name],
                                            data_size[field_name],
                                            charge)
        profit_row[field_name] = revenue_row[field_name] - cost_row[field_name]
    return [discharge_count_row, discharge_energy_row, charge_count_row, charge_energy_row, revenue_row, cost_row,
            profit_row]


fieldnames = ['item']
data_size = {}
index_start = {}
financial_start = get_data_size([date(2019, 1, 1), date(2019, 6, 30)])
quarter_start = 0
calendar_start = 0
for i in range(2019, 2031):
    for j in range(1, 5):
        field = str(i % 100) + '-' + 'Q' + str(j)
        fieldnames.append(field)
        data_size[field] = get_data_size(get_date_quarter(i, j))
        index_start[field] = quarter_start
        quarter_start += data_size[field]
    if i != 2030:
        field = 'FY-' + str(i % 100) + '/' + str(i % 100 + 1)
        fieldnames.append(field)
        data_size[field] = get_data_size(get_date_financial_year(i))
        index_start[field] = financial_start
        financial_start += data_size[field]
    field = 'Cal-' + str(i % 100)
    fieldnames.append(field)
    data_size[field] = get_data_size(get_date_calendar_year(i))
    index_start[field] = calendar_start
    calendar_start += data_size[field]

mat_contents = sio.loadmat('HH_Sim_Spot_1000_500eachVIC1_forBattery_2018-08-15.mat')
stimulation_count = 1000

file = open("Dispatches_1000_stimulation_v4", 'r')
lines = file.readlines()
spot_prices = []

csvfile = open(str(stimulation_count)+'_stimulation.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
for index_simulation in range(0, stimulation_count):
    index, dispatches = lines[index_simulation].split(" ")
    # print(dispatches[-1])
    for i in range(len(mat_contents['Spot_Sims'])):
        spot_prices.append(mat_contents['Spot_Sims'][i][index_simulation])
    rows = generate_one_stimulation_data(dispatches, spot_prices, index_start, data_size)
    writer.writerows(rows)
    writer.writerow({})

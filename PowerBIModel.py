import csv
import numpy as np

simulation_count = 1000
f = open(str(simulation_count) + '_simulation.csv', newline='')
reader = csv.DictReader(f)
count = 0

data_array = np.empty((7, 71, simulation_count), float)
z = 0
for row in reader:
    z = count % 8
    x = int(count / 8)
    if z == 7:
        count += 1
        continue
    y = 0

    period = []
    for i in range(2019, 2031):
        for j in range(1, 5):
            field = str(i % 100) + '-' + 'Q' + str(j)
            period.append(field)
            data_array[z][y][x] = row[field]
            y += 1

        if i != 2030:
            field = 'FY-' + str(i % 100) + '/' + str(i % 100 + 1)
            period.append(field)
            data_array[z][y][x] = row[field]
            y += 1

        field = 'Cal-' + str(i % 100)
        period.append(field)
        data_array[z][y][x] = row[field]
        y += 1
    count += 1

result_array = np.empty((22, 7, 71), float)

variables = ['Discharged Count', 'Discharged Energy', 'Charged Count', 'Charged Energy', 'Revenue', 'Cost', 'Profit']
percentiles = ['1', '0.95', '0.95', '0.95', '0.75', '0.75', '0.75', '0.75', '0.50', '0.50', '0.50', '0.50', '0.50',
               '0.25', '0.25', '0.25', '0.25', '0.05', '0.05', '0.05', '0', 'ave']

for j in range(len(percentiles)):
    if percentiles[j] != 'ave':
        percent = int(float(percentiles[j]) * 100)
        result_array[j] = np.percentile(data_array, percent, axis=2)
    else:
        result_array[j] = np.mean(data_array, axis=2)

fieldnames = ['ID', 'Period', 'Percentile', 'Variable', 'Value', 'Date Group']

csvfile = open(str(simulation_count) + '_PBI.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()


def get_date_group(s):
    if 'FY' in s:
        return 'Financial Year'
    elif 'Q' in s:
        return 'Quarterly'
    else:
        return 'Calendar Year'


for i in range(len(variables)):
    one_row = {'Variable': variables[i]}
    for k in range(len(percentiles)):
        one_row['Percentile'] = percentiles[k]
        for j in range(len(period)):
            one_row['Period'] = period[j]
            one_row['Value'] = result_array[k][i][j]
            one_row['Date Group'] = get_date_group(period[j])
            writer.writerow(one_row)

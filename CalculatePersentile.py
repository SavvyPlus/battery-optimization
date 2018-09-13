import csv
import numpy as np

stimulation_count = 1000
f = open(str(stimulation_count)+'_stimulation.csv', newline='')
reader = csv.DictReader(f)
count = 0

data_array = np.empty((7, 71, stimulation_count), float)
z = 0
for row in reader:
    z = count % 8
    x = int(count / 8)
    if z == 7:
        count += 1
        continue
    y = 0

    fieldnames = ['variables', 'percentile']
    for i in range(2019, 2031):
        for j in range(1, 5):
            field = 'Q' + str(j) + '-' + str(i % 100)
            fieldnames.append(field)
            data_array[z][y][x] = row[field]
            y += 1

        if i != 2030:
            field = 'FY-' + str(i % 100) + '/' + str(i % 100 + 1)
            fieldnames.append(field)
            data_array[z][y][x] = row[field]
            y += 1

        field = 'Cal-' + str(i % 100)
        fieldnames.append(field)
        data_array[z][y][x] = row[field]
        y += 1
    count += 1

result_array = np.empty((8, 7, 71), float)

variables = ['discharge_count', 'discharge_energy', 'charge_count', 'charge_energy', 'revenue', 'cost', 'profit']
percentiles = ['100%', '95%', '75%', '50%', '25%', '5%', '0', 'Ave']

print(np.percentile(data_array, 0, axis=2))

# for i in range(7):
#     for j in range(71):
result_array[6] = np.percentile(data_array, 0, axis=2)
result_array[5] = np.percentile(data_array, 5, axis=2)
result_array[4] = np.percentile(data_array, 25, axis=2)
result_array[3] = np.percentile(data_array, 50, axis=2)
result_array[2] = np.percentile(data_array, 75, axis=2)
result_array[1] = np.percentile(data_array, 95, axis=2)
result_array[0] = np.percentile(data_array, 100, axis=2)
result_array[7] = np.mean(data_array, axis=2)

csvfile = open(str(stimulation_count)+'_percentile.csv', 'w', newline='')
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
for i in range(len(variables)):
    one_row = {'variables': variables[i]}
    for k in range(len(percentiles)):
        one_row['percentile'] = percentiles[k]
        for j in range(len(fieldnames) - 2):
            one_row[fieldnames[j + 2]] = result_array[k][i][j]
        writer.writerow(one_row)
    writer.writerow({})

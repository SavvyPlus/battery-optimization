import csv


def write_to(file_name, data, fieldnames):
    file = open(file_name, 'w', newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)


def write_to_(file_name, data):
    file = open(file_name, 'a', newline='')
    writer = csv.writer(file)
    writer.writerows(data)


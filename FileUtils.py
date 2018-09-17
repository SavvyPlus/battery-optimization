import csv


def write_to(file_name, data, fieldnames):
    file = open(file_name, 'w', newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

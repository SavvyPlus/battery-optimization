import random

data = []
for i in range(17520):
    data.append(str(random.randint(0, 5000)))

file = open('datat', 'w')
for l in data:
    file.write(l)
    file.write('\n')
file.close()

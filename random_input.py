import random

data = []
for i in range(20000):
    data.append(str(random.randint(10, 1000)))

file = open('datat', 'w')
for l in data:
    file.write(l)
    file.write('\n')
file.close()

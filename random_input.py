import random

data = []
for i in range(20):
    data.append(str(random.randint(10, 100)))

file = open('datat', 'w')
for l in data:
    file.write(l)
    file.write('\n')
file.close()

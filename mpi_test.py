from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
comm_rank = comm.Get_rank()

size = comm.Get_size()
length = 1000
width = int(length / size)

if comm_rank == 0:
    parameters = {}
    for i in range(size - 1):
        comm.send(start, dest=i + 1)
        start += width

else:

    data = comm.recv(source=0)
    for i in range(data, data + width):
        print('Rank ' + str(comm_rank) + " :" + str(i))

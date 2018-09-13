import scipy.io as sio
import h5py

mat_contents = h5py.File('35percent_NewGen.mat')
data = mat_contents.get('EG')
print(mat_contents.get('EG'))
for i in range(len(mat_contents['Spot_Sims'])):
    if len(mat_contents['Spot_Sims'][i]) != 1000:
        print(i)
        print(len(mat_contents['Spot_Sims'][i]))

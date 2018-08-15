import scipy.io as sio

mat_contents = sio.loadmat('HH_Sim_Spot_1000_500eachVIC1_forBattery_2018-08-15.mat')
# print (mat_contents['Spot_Sims'])
for i in range(1000):
    print(str(i) + ' '+str(mat_contents['Spot_Sims'][i][0]))

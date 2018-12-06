import numpy as np
states=[0]*7
data_actuation_s=[0]*4
data_actuation_r=[0]*8
state_vector=[]
n_samples=2
state_data= [[0 for x in range(7)] for y in range(n_samples)] 
for v in range(n_samples):
            for w in range(7):
            	state_data[v][w]=50*float(np.random.rand(1,1,1))

for p in range(4):
                data_actuation_s[p] = 50*float(np.random.rand(1,1,1))  #4 external magnets
            ##                   |-pair 1-|  |-pair 2-| |--pair 3-|
for p in range(8):
                data_actuation_r[p] = 50*float(np.random.rand(1,1,1))
print(data_actuation_s)
print(data_actuation_r)
import numpy as np


data_actuation_s=[]
data_actuation_r=[]
i=20
while(i>0):
	for p in range(4):
		data_actuation_s.append(50*float(np.random.rand(1,1,1))) 
	for p in range(8):
		data_actuation_r.append(50*float(np.random.rand(1,1,1)))
	i=i-1

print(data_actuation_r)
print(data_actuation_s)
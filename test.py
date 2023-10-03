from pymoo.operators.mutation.pm import *

ar = np.asarray([[1,2], [3,4]])
print(ar)
xl = np.asarray([0,0])
xu = np.asarray([10,10])
eta = np.asarray([20,20])
prob = np.asarray([20,20])
res = mut_pm(ar, xl=xl, xu=xu, eta=eta, prob=prob, at_least_once=False)

print(res)
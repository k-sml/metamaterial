#占有率と位相の関係を表す図を出力します


import numpy as np
import matplotlib.pyplot as plt


def f(n, m, x, y):
    TE = x * n**2 + (1 - x) * m**2
    TM = y * n**(-2) + (1 - y) * m**(-2)

    ref = ((x * (1 / TM) + (1 - x) * m**2) / (y * (1 / TE) + (1 - y) * m**(-2)))**(1/4)
    return ref

x = np.arange(0.0, 1.0, 0.01)
ans = []
n = 3.4
m = 1
h = 300 * 10**(-6)
λ = 750 * 10**(-6)
for i in range(len(x)):
    ans.append(f(n, m, x[i], x[i]) * h * 360 / λ)



plt.title('(Si:3.4, air:1)')
plt.xlabel('occupancy')
plt.ylabel('phase[degree]')
plt.plot(x, ans, 'b-')
plt.show()

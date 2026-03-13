import numpy as np
import matplotlib.pyplot as plt
import math

def taylor_exp(x, n=10):
    s = 0
    for i in range(n):
        s += x**i / math.factorial(i)
    return s

def taylor_sin(x, n=10):
    s = 0
    for i in range(n):
        s += (-1)**i * x**(2*i+1) / math.factorial(2*i+1)
    return s

def taylor_cos(x, n=10):
    s = 0
    for i in range(n):
        s += (-1)**i * x**(2*i) / math.factorial(2*i)
    return s


x = np.linspace(-2,2,100)

exp_vals = [taylor_exp(i) for i in x]
sin_vals = [taylor_sin(i) for i in x]
cos_vals = [taylor_cos(i) for i in x]

fig, axs = plt.subplots(2,2)

axs[0,0].plot(x, exp_vals)
axs[0,0].set_title("exp(x)")

axs[0,1].plot(x, sin_vals)
axs[0,1].set_title("sin(x)")

axs[1,0].plot(x, cos_vals)
axs[1,0].set_title("cos(x)")

fig.delaxes(axs[1,1])

plt.tight_layout()
plt.show()
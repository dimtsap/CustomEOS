import psutil
import numpy as np
import matplotlib.pyplot as plt


def f():
    size = (1000000,)
    x = np.random.random(size)
    s = sorted(x)


for i in range(5):
    f()

current_process = psutil.Process()
print(current_process.cpu_percent())
import numpy as np
import time

def f(n):
    x = np.random.random((n,))
    s = sorted(x)


def g(t):
    time.sleep(t)

if __name__ == '__main__':
    n = 1000
    for i in range(3):
        f(n)
        g(2)

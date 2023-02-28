import time
import multiprocessing as mp
import psutil
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def run_predict():
    for i in range(3):
        x_test = np.random.rand(1000000,)
        s = sorted(x_test)
        time.sleep(1.5)


def monitor(target):
    worker_process = mp.Process(target=target)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    # log cpu usage of `worker_process` every 10 ms
    # cpu_percents = []
    # while p.is_running():
    #     cpu_percents.append(p.cpu_percent())
    #     time.sleep(0.01)
    while worker_process.is_alive():
        cpu_percents.append(p.cpu_percent())
        time.sleep(0.01)

    worker_process.join()
    return cpu_percents


if __name__ == '__main__':
    cpu_percents = monitor(target=run_predict)
    fig, ax = plt.subplots()
    ax.plot(cpu_percents)
    ax.set(xlabel='Milliseconds', ylabel='Percent Usage')

    plt.show()

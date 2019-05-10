import psutil
import time
import os


def getProcess(pName):
    shutdown_system = True
    # 获取当前系统所有进程id列表
    all_pids = psutil.pids()
    try:
        for pid in all_pids:
            p = psutil.Process(pid)
            if pName == p.name():
                percent = p.cpu_percent(0,0)
                print(pid, percent)
                shutdown_system &= percent < 10
                # shutdown_system &= p.cpu_percent(0.1) < 0.1
    except:
        pass
    return shutdown_system


# 获取进程名位Python的进程对象列表


while True:
    if getProcess("Python"):
        # os.system('which user')
        os.system('echo password | sudo -S shutdown')
        break
    print('*****\n')
    time.sleep(4)

import psutil
import time

process_lst = []

def getProcess(pName):
    # 获取当前系统所有进程id列表
    all_pids  = psutil.pids()

    # 遍历所有进程，名称匹配的加入process_lst
    for pid in all_pids:
        p = psutil.Process(pid)
        if pName == p.name():
            process_lst.append(p)

    return process_lst

# 获取进程名位Python的进程对象列表
process_lst = getProcess("Python")

# 获取内存利用率：
for i in range(10):
    for process_instance in process_lst:
        print(process_instance.pid)
        print(process_instance.memory_percent())
        print(process_instance.cpu_percent(None))
        print('\n')
    time.sleep(4)

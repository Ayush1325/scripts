import subprocess
from timeit import Timer

args = ("cat", "/sys/bus/iio/devices/iio:device1/in_temp_raw")


def func():
    res = subprocess.run(args, capture_output=True)
    if res.returncode:
        exit(-1)


if __name__ == "__main__":
    for i in range(5):
        func()
    print("Warmup done")

    while True:
        t = Timer(func).timeit(100) / 100
        print(f"Time: {t}")

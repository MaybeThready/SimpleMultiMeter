import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from pathlib import Path
from rich import print
from rich.rule import Rule

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

XLSX = Path("./校准.xlsx")

K_C = 0.205607
B_C = -108.770107

K_L = 0.010968
B1_L = 13.496801
B2_L = -426.500360

KDC_0 = 1.682675
BDC_0 = 0.768850
KDC_1 = 8.290760
BDC_1 = -60.741420
KDC = [KDC_0, KDC_1]
BDC = [BDC_0, BDC_1]

KAC_0 = 0.100092
BAC_0 = 0.112086
KAC_1 = 0.997820
BAC_1 = 1.310698
KAC = [KAC_0, KAC_1]
BAC = [BAC_0, BAC_1]

KR0 = 239.818072
KR1 = 150.182325
KR2 = 7572.462199
KR3 = 64731.398545
KR4 = 629228.308535
KR = [KR0, KR1, KR2, KR3, KR4]

KB0 = 0.111025
KB1 = 0.026782
KB2 = 4.385881
KB3 = 31.450735
KB4 = 300.471240
BR = [KB0, KB1, KB2, KB3, KB4]

FB0 = 112.237655
FB1 = -61.101823
FB2 = 48.488831
FB3 = -31.696393
FB4 = -20.504653
FB = [FB0, FB1, FB2, FB3, FB4]


def evaluate(measured_val, cal_y, target_y):
    pre_acc = np.abs((measured_val - target_y) / target_y)
    pre_min_acc = pre_acc.min()
    pre_max_acc = pre_acc.max()
    pre_mean_acc = pre_acc.mean()

    post_acc = np.abs((cal_y - target_y) / target_y)
    post_min_acc = post_acc.min()
    post_max_acc = post_acc.max()
    post_mean_acc = post_acc.mean()

    return {
        "pre_min_acc": pre_min_acc,
        "pre_max_acc": pre_max_acc,
        "pre_mean_acc": pre_mean_acc,
        "post_min_acc": post_min_acc,
        "post_max_acc": post_max_acc,
        "post_mean_acc": post_mean_acc,
    }


def calibrate_capacitor():
    df = pd.read_excel(XLSX, sheet_name="电容")
    measured_val = df["测量值"].to_numpy()
    target_y = df["真值"].to_numpy()

    def func(x, k, b):
        return k * x + b

    def inv_func(y, k, b):
        return (y - b) / k

    x = inv_func(measured_val, K_C, B_C)

    popt, pcov = curve_fit(
        func, x, target_y, sigma=target_y, absolute_sigma=False, p0=[K_C, B_C]
    )

    k, b = popt
    cal_y = func(x, k, b)

    eval_result = evaluate(measured_val, cal_y, target_y)

    print(Rule("电容校准结果"))

    print(f"校准后系数\n\tk: {k:.6f}\n\tb: {b:.6f}")
    print(f"格式化系数\n\tk: {round(k * 2**32, 0)}\n\tb: {round(b * 2**16, 0)}")

    print(Rule())

    print(f"校准前最小精度: {eval_result['pre_min_acc']*100:.2f}%")
    print(f"校准前最大精度: {eval_result['pre_max_acc']*100:.2f}%")
    print(f"校准前平均精度: {eval_result['pre_mean_acc']*100:.2f}%")

    print(Rule())

    print(f"校准后最小精度: {eval_result['post_min_acc']*100:.2f}%")
    print(f"校准后最大精度: {eval_result['post_max_acc']*100:.2f}%")
    print(f"校准后平均精度: {eval_result['post_mean_acc']*100:.2f}%")

    print(Rule())

    fig, ax = plt.subplots(2, 1, squeeze=False)
    x_val = np.linspace(x.min() - 50, x.max() + 50, 1000)

    ax[0][0].plot(x_val, func(x_val, K_C, B_C), label="校准前曲线", color="orange")
    ax[0][0].plot(x_val, func(x_val, k, b), label="校准后曲线", color="green")
    ax[0][0].scatter(x, target_y, label="真值点", marker="x")
    ax[0][0].set_xlabel("x")
    ax[0][0].set_ylabel("y")
    ax[0][0].set_title("电容校准曲线")
    ax[0][0].legend()

    ax[1][0].scatter(
        x, (measured_val - target_y) / target_y, label="校准前误差", color="orange"
    )
    ax[1][0].scatter(
        x, (cal_y - target_y) / target_y, label="校准后误差", color="green"
    )
    ax[1][0].axhline(0, color="black", linestyle="--")
    ax[1][0].set_xlabel("x")
    ax[1][0].set_ylabel("误差")
    ax[1][0].set_title("电容校准误差")
    ax[1][0].legend()

    plt.show()


def calibrate_inductor():
    df = pd.read_excel(XLSX, sheet_name="电感")
    measured_val = df["测量值"].to_numpy()
    target_y = df["真值"].to_numpy()

    def func(x, k, b1, b2):
        return (k * x + b1) ** 2 + b2

    def inv_func(y, k, b1, b2):
        return (np.sqrt(y - b2) - b1) / k

    x = inv_func(measured_val, K_L, B1_L, B2_L)

    popt, pcov = curve_fit(
        func, x, target_y, sigma=target_y, absolute_sigma=False, p0=[K_L, B1_L, B2_L]
    )

    k, b1, b2 = popt
    cal_y = func(x, k, b1, b2)

    eval_result = evaluate(measured_val, cal_y, target_y)

    print(Rule("电感校准结果"))

    print(f"校准后系数\n\tk: {k:.6f}\n\tb1: {b1:.6f}\n\tb2: {b2:.6f}")
    print(
        f"格式化系数\n\tk: {round(k * 2**32, 0)}\n\tb1: {round(b1 * 2**24, 0)}\n\tb2: {round(b2 * 2**16, 0)}"
    )

    print(Rule())

    print(f"校准前最小精度: {eval_result['pre_min_acc']*100:.2f}%")
    print(f"校准前最大精度: {eval_result['pre_max_acc']*100:.2f}%")
    print(f"校准前平均精度: {eval_result['pre_mean_acc']*100:.2f}%")

    print(Rule())

    print(f"校准后最小精度: {eval_result['post_min_acc']*100:.2f}%")
    print(f"校准后最大精度: {eval_result['post_max_acc']*100:.2f}%")
    print(f"校准后平均精度: {eval_result['post_mean_acc']*100:.2f}%")

    print(Rule())

    fig, ax = plt.subplots(2, 1, squeeze=False)
    x_val = np.linspace(x.min() - 50, x.max() + 50, 1000)

    ax[0][0].plot(
        x_val, func(x_val, K_L, B1_L, B2_L), label="校准前曲线", color="orange"
    )
    ax[0][0].plot(x_val, func(x_val, k, b1, b2), label="校准后曲线", color="green")
    ax[0][0].scatter(x, target_y, label="真值点", marker="x")
    ax[0][0].set_xlabel("x")
    ax[0][0].set_ylabel("y")
    ax[0][0].set_title("电感校准曲线")
    ax[0][0].legend()

    ax[1][0].scatter(
        x, (measured_val - target_y) / target_y, label="校准前误差", color="orange"
    )
    ax[1][0].scatter(
        x, (cal_y - target_y) / target_y, label="校准后误差", color="green"
    )
    ax[1][0].axhline(0, color="black", linestyle="--")
    ax[1][0].set_xlabel("x")
    ax[1][0].set_ylabel("误差")
    ax[1][0].set_title("电感校准误差")
    ax[1][0].legend()

    plt.show()


def calibrate_dc(channel: int = 0):
    df = pd.read_excel(XLSX, sheet_name="DC")
    df = df[df["通道"] == channel]
    measured_val = df["测量值"].to_numpy()
    target_y = df["真值"].to_numpy()

    def func(x, k, b):
        return k * x + b

    def inv_func(y, k, b):
        return (y - b) / k

    x = inv_func(measured_val, KDC[channel], BDC[channel])

    popt, pcov = curve_fit(
        func,
        x,
        target_y,
        sigma=target_y,
        absolute_sigma=False,
        p0=[KDC[channel], BDC[channel]],
    )

    k, b = popt
    cal_y = func(x, k, b)

    eval_result = evaluate(measured_val, cal_y, target_y)

    print(Rule("直流校准结果"))

    print(f"校准后系数\n\tk: {k:.6f}\n\tb: {b:.6f}")
    print(f"格式化系数\n\tk: {round(k * 2**16, 0)}\n\tb: {round(b * 2**16, 0)}")

    print(Rule())

    print(f"校准前最小精度: {eval_result['pre_min_acc']*100:.2f}%")
    print(f"校准前最大精度: {eval_result['pre_max_acc']*100:.2f}%")
    print(f"校准前平均精度: {eval_result['pre_mean_acc']*100:.2f}%")

    print(Rule())

    print(f"校准后最小精度: {eval_result['post_min_acc']*100:.2f}%")
    print(f"校准后最大精度: {eval_result['post_max_acc']*100:.2f}%")
    print(f"校准后平均精度: {eval_result['post_mean_acc']*100:.2f}%")

    print(Rule())

    fig, ax = plt.subplots(2, 1, squeeze=False)
    x_val = np.linspace(x.min() - 50, x.max() + 50, 1000)

    ax[0][0].plot(
        x_val,
        func(x_val, KDC[channel], BDC[channel]),
        label="校准前曲线",
        color="orange",
    )
    ax[0][0].plot(x_val, func(x_val, k, b), label="校准后曲线", color="green")
    ax[0][0].scatter(x, target_y, label="真值点", marker="x")
    ax[0][0].set_xlabel("x")
    ax[0][0].set_ylabel("y")
    ax[0][0].set_title("直流校准曲线")
    ax[0][0].legend()

    ax[1][0].scatter(
        x, (measured_val - target_y) / target_y, label="校准前误差", color="orange"
    )
    ax[1][0].scatter(
        x, (cal_y - target_y) / target_y, label="校准后误差", color="green"
    )
    ax[1][0].axhline(0, color="black", linestyle="--")
    ax[1][0].set_xlabel("x")
    ax[1][0].set_ylabel("误差")
    ax[1][0].set_title("直流校准误差")
    ax[1][0].legend()

    plt.show()


def calibrate_ac(channel: int = 0):
    df = pd.read_excel(XLSX, sheet_name="AC")
    df = df[df["通道"] == channel]
    measured_val = df["测量值"].to_numpy()
    target_y = df["真值"].to_numpy()

    def func(x, k, b):
        return k * x + b

    def inv_func(y, k, b):
        return (y - b) / k

    x = inv_func(measured_val, KAC[channel], BAC[channel])

    popt, pcov = curve_fit(
        func,
        x,
        target_y,
        sigma=target_y,
        absolute_sigma=False,
        p0=[KAC[channel], BAC[channel]],
    )

    k, b = popt
    cal_y = func(x, k, b)

    eval_result = evaluate(measured_val, cal_y, target_y)

    print(Rule("交流校准结果"))

    print(f"校准后系数\n\tk: {k:.6f}\n\tb: {b:.6f}")
    print(f"格式化系数\n\tk: {round(k * 2**16, 0)}\n\tb: {round(b * 2**16, 0)}")

    print(Rule())

    print(f"校准前最小精度: {eval_result['pre_min_acc']*100:.2f}%")
    print(f"校准前最大精度: {eval_result['pre_max_acc']*100:.2f}%")
    print(f"校准前平均精度: {eval_result['pre_mean_acc']*100:.2f}%")

    print(Rule())

    print(f"校准后最小精度: {eval_result['post_min_acc']*100:.2f}%")
    print(f"校准后最大精度: {eval_result['post_max_acc']*100:.2f}%")
    print(f"校准后平均精度: {eval_result['post_mean_acc']*100:.2f}%")

    print(Rule())

    fig, ax = plt.subplots(2, 1, squeeze=False)
    x_val = np.linspace(x.min() - 50, x.max() + 50, 1000)

    ax[0][0].plot(
        x_val,
        func(x_val, KAC[channel], BAC[channel]),
        label="校准前曲线",
        color="orange",
    )
    ax[0][0].plot(x_val, func(x_val, k, b), label="校准后曲线", color="green")
    ax[0][0].scatter(x, target_y, label="真值点", marker="x")
    ax[0][0].set_xlabel("x")
    ax[0][0].set_ylabel("y")
    ax[0][0].set_title("交流校准曲线")
    ax[0][0].legend()

    ax[1][0].scatter(
        x, (measured_val - target_y) / target_y, label="校准前误差", color="orange"
    )
    ax[1][0].scatter(
        x, (cal_y - target_y) / target_y, label="校准后误差", color="green"
    )
    ax[1][0].axhline(0, color="black", linestyle="--")
    ax[1][0].set_xlabel("x")
    ax[1][0].set_ylabel("误差")
    ax[1][0].set_title("交流校准误差")
    ax[1][0].legend()

    plt.show()


def calibrate_resistor(channel: int = 0):
    df = pd.read_excel(XLSX, sheet_name="电阻")
    df = df[df["通道"] == channel]
    measured_val = df["测量值"].to_numpy()
    target_y = df["真值"].to_numpy()

    def func(x, k, b1, b2):
        return k / (x + b1) - b2

    def inv_func(y, k, b1, b2):
        return k / (y + b2) - b1

    x = inv_func(measured_val, KR[channel], FB[channel], BR[channel])

    popt, pcov = curve_fit(
        func,
        x,
        target_y,
        sigma=target_y,
        absolute_sigma=False,
        p0=[KR[channel], FB[channel], BR[channel]],
    )

    k, b1, b2 = popt
    cal_y = func(x, k, b1, b2)

    eval_result = evaluate(measured_val, cal_y, target_y)

    print(Rule("电阻校准结果"))

    print(f"校准后系数\n\tk: {k:.6f}\n\tb1: {b1:.6f}\n\tb2: {b2:.6f}")
    print(
        f"格式化系数\n\tk: {round(k * 2**12, 0)}\n\tb1: {round(b1 * 2**9, 0)}, \n\tb2: {round(b2 * 2**16, 0)}"
    )

    print(Rule())

    print(f"校准前最小精度: {eval_result['pre_min_acc']*100:.2f}%")
    print(f"校准前最大精度: {eval_result['pre_max_acc']*100:.2f}%")
    print(f"校准前平均精度: {eval_result['pre_mean_acc']*100:.2f}%")

    print(Rule())

    print(f"校准后最小精度: {eval_result['post_min_acc']*100:.2f}%")
    print(f"校准后最大精度: {eval_result['post_max_acc']*100:.2f}%")
    print(f"校准后平均精度: {eval_result['post_mean_acc']*100:.2f}%")

    print(Rule())

    fig, ax = plt.subplots(2, 1, squeeze=False)
    x_val = np.linspace(x.min() - 50, x.max() + 50, 1000)

    ax[0][0].plot(
        x_val,
        func(x_val, KR[channel], FB[channel], BR[channel]),
        label="校准前曲线",
        color="orange",
    )
    ax[0][0].plot(x_val, func(x_val, k, b1, b2), label="校准后曲线", color="green")
    ax[0][0].scatter(x, target_y, label="真值点", marker="x")
    ax[0][0].set_xlabel("x")
    ax[0][0].set_ylabel("y")
    ax[0][0].set_title("电阻校准曲线")
    ax[0][0].legend()

    ax[1][0].scatter(
        x, (measured_val - target_y) / target_y, label="校准前误差", color="orange"
    )
    ax[1][0].scatter(
        x, (cal_y - target_y) / target_y, label="校准后误差", color="green"
    )
    ax[1][0].axhline(0, color="black", linestyle="--")
    ax[1][0].set_xlabel("x")
    ax[1][0].set_ylabel("误差")
    ax[1][0].set_title("电阻校准误差")
    ax[1][0].legend()

    plt.show()


if __name__ == "__main__":
    calibrate_inductor()

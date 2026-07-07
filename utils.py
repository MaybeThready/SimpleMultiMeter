import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# 数据
x = np.array([2, 10, 50, 100, 200, 500, 1000, 1200, 1400, 1800, 2000]).reshape(-1, 1)
y = np.array([1.5, 9.5, 49.6, 99.4, 198.8, 498.6, 997.8, 1196.7, 1396.8, 1796.9, 1997])

# 线性拟合
model = LinearRegression()
model.fit(x, y)

a = model.coef_[0]
b = model.intercept_
y_pred = model.predict(x)

# 误差
err = y - y_pred

print("Gain a =", a)
print("Offset b =", b)
print("Max error =", np.max(np.abs(err)))
print("Mean error =", np.mean(err))

# R^2 判断线性程度
print("R^2 =", model.score(x, y))

# 画图
plt.scatter(x, y, label="measured")
plt.plot(x, y_pred, label="fit", color="red")
plt.legend()
plt.show()

# 残差
plt.plot(x, err, marker="o")
plt.title("Residual error")
plt.show()

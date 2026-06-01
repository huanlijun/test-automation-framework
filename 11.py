import requests

# 1. 发GET请求（查数据）
print("===== 1. GET 请求 =====")
res = requests.get("https://httpbin.org/get")
print("状态码:", res.status_code)
print("返回内容:\n", res.json())
print()

# 2. 发POST表单请求（登录）
print("===== 2. POST 表单 =====")
data = {"user": "test", "pwd": "123456"}
res = requests.post("https://httpbin.org/post", data=data)
print("返回数据:\n", res.json())
print()

# 3. POST JSON（接口最常用）
print("===== 3. POST JSON =====")
json_data = {"name": "手机", "price": 1999}
res = requests.post("https://httpbin.org/post", json=json_data)
print("返回数据:\n", res.json())
print()

# 4. 带参数的GET
print("===== 4. GET 带参数 =====")
params = {"page": 1, "size": 10}
res = requests.get("https://httpbin.org/get", params=params)
print("最终URL:", res.url)
print()

# 5. 会话保持（登录后才能访问）
print("===== 5. 会话 Session =====")
s = requests.Session()
res = s.post("https://httpbin.org/post", data={"user": "a"})
print("会话请求成功")
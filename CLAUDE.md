# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Pytest 的接口自动化测试框架，采用数据驱动的设计模式，使用 YAML 文件管理测试用例。框架支持单接口测试和业务场景测试，集成 Allure 报告，并提供 Mock Server 用于本地测试。

## 核心架构

### 测试用例执行流程

1. **单接口测试流程**：`testcase/*.py` → `base/apiutil.py` → `common/sendrequest.py` → API
2. **业务场景测试流程**：`testcase/Business interface/*.py` → `base/apiutil_business.py` → `common/sendrequest.py` → API

两种测试方式的主要区别：
- 单接口测试：每个测试用例独立执行，适合功能点测试
- 业务场景测试：多个接口按业务流程串联执行，支持接口间数据传递

### 目录结构说明

- **base/** - 核心请求处理层
  - `apiutil.py` - 单接口测试的请求处理基类
  - `apiutil_business.py` - 业务场景测试的请求处理基类
  - `generateId.py` - 生成 Allure 报告的模块和用例 ID
  - `removefile.py` - 清理临时文件

- **common/** - 通用工具模块
  - `sendrequest.py` - 封装 requests 库，处理 HTTP 请求
  - `readyaml.py` - YAML 文件读写，包括测试数据和参数提取
  - `assertions.py` - 断言处理
  - `debugtalk.py` - 自定义函数库（时间戳、加密、数据提取等）
  - `recordlog.py` - 日志记录
  - `dingRobot.py` - 钉钉消息通知
  - `connection.py` - 数据库连接（MySQL、Redis、ClickHouse、MongoDB）

- **conf/** - 配置管理
  - `config.ini` - 环境配置（API 地址、数据库连接等）
  - `setting.py` - 框架全局设置（日志级别、超时时间、文件路径等）
  - `operationConfig.py` - 配置文件读取工具

- **testcase/** - 测试用例
  - `Single interface/` - 单接口测试用例
  - `Business interface/` - 业务场景测试用例
  - `ProductManager/` - 商品管理相关测试用例及 YAML 数据文件

- **mock_server/** - Mock API 服务器
  - `api_server/base/flask_service.py` - Flask 实现的 Mock 接口服务

- **data/** - 测试数据文件（CSV、YAML 等）

- **report/** - 测试报告
  - `temp/` - Allure 临时数据
  - `allureReport/` - Allure HTML 报告

### 数据流转机制

1. **参数替换**：YAML 文件中使用 `${function_name(params)}` 语法调用 `debugtalk.py` 中的函数
2. **数据提取**：接口响应数据通过 `extract` 或 `extract_list` 提取，保存到 `extract.yaml`
3. **数据引用**：后续接口通过 `${get_extract_data(key)}` 引用已提取的数据

## 常用命令

### 启动 Mock Server

```bash
cd mock_server/api_server/base
python flask_service.py
```

Mock Server 默认运行在 `http://127.0.0.1:8787`

### 运行测试

```bash
# 运行所有测试
pytest testcase/ -vs --alluredir ./report/temp --clean-alluredir

# 运行单个测试文件
pytest testcase/ProductManager/test_productList.py -vs --alluredir ./report/temp

# 运行单个测试用例
pytest testcase/ProductManager/test_productList.py::TestLogin::test_get_product_list -vs

# 按标记运行
pytest testcase/ -m "order=1" -vs
```

### 生成 Allure 报告

```bash
# 生成并打开报告
allure generate ./report/temp -o ./report/allureReport --clean
allure open ./report/allureReport

# 或者直接查看
allure serve ./report/temp
```

### 清理临时文件

测试开始前会自动清理 `extract.yaml` 和 `report/temp/` 目录（通过 `conftest.py` 的 fixture）

## YAML 测试用例格式

### 单接口测试格式

```yaml
- baseInfo:
    api_name: 接口名称
    url: /api/path
    method: post
    header:
      Content-Type: application/json
  testCase:
    - case_name: 测试用例名称
      json:
        param1: value1
      validation:
        - eq: { 'code': 200 }
      extract:
        token: $.data.token
```

### 业务场景测试格式

```yaml
baseInfo:
  api_name: 业务场景名称
  url: /api/path
  method: post
  header:
    Content-Type: application/json
testCase:
  - case_name: 步骤1
    json:
      param: value
    validation:
      - eq: { 'code': 200 }
    extract:
      order_id: $.data.orderId
  - case_name: 步骤2
    json:
      orderId: ${get_extract_data(order_id)}
    validation:
      - eq: { 'code': 200 }
```

## 断言方式

框架支持多种断言类型（在 `common/assertions.py` 中实现）：

- `eq` - 相等断言
- `contains` - 包含断言
- `startswith` - 开头匹配
- `endswith` - 结尾匹配
- `status_code` - HTTP 状态码断言

## 自定义函数

在 `common/debugtalk.py` 中定义的函数可在 YAML 中使用：

- `${get_extract_data(key)}` - 获取已提取的数据
- `${timestamp()}` - 获取当前时间戳（10位）
- `${timestamp_thirteen()}` - 获取当前时间戳（13位）
- `${md5_encryption(text)}` - MD5 加密
- `${sha1_encryption(text)}` - SHA1 加密
- `${end_time()}` - 获取当前时间（标准格式）

## 环境配置

修改 `conf/config.ini` 配置测试环境：

```ini
[api_envi]
host = http://127.0.0.1:8787

[MYSQL]
host = your_host
port = 3306
username = root
password = your_password
database = your_db
```

## 注意事项

1. **测试用例执行顺序**：使用 `@pytest.mark.run(order=N)` 控制执行顺序
2. **数据隔离**：每次测试会话开始时自动清空 `extract.yaml`，确保数据隔离
3. **Mock Server 依赖**：运行测试前需先启动 Mock Server
4. **YAML 文件编码**：所有 YAML 文件必须使用 UTF-8 编码
5. **接口关联**：业务场景测试中，接口间通过 `extract` 和 `${get_extract_data()}` 实现数据传递
6. **Cookie 处理**：框架自动处理 Cookie，登录后的 Cookie 会保存到 `extract.yaml`

## 扩展开发

### 添加新的测试用例

1. 在 `testcase/` 对应目录创建 YAML 文件
2. 在对应的 `test_*.py` 文件中添加测试方法
3. 使用 `@pytest.mark.parametrize` 装饰器加载 YAML 数据

### 添加自定义函数

在 `common/debugtalk.py` 的 `DebugTalk` 类中添加方法，即可在 YAML 中使用

### 添加新的断言类型

在 `common/assertions.py` 的 `Assertions` 类中添加断言方法

# accountBook
A simple web-based accounting book that supports the conversion between Renminbi (CNY) and Singapore Dollar (SGD), records daily income and expenses, and keeps track of the daily exchange rate.

---

# 网页记账本 (AccountBook)

这是一个基于 Python Flask 和 MongoDB 的本地网页记账本应用。

## 目录结构及文件说明

- **app.py**:
  - 后端核心文件，使用 Flask 框架构建。
  - 负责启动 Web 服务器（默认端口 3000）。
  - 连接 MongoDB 数据库，处理所有 API 请求（余额查询、充值、消费、历史记录、汇率统计等）。
  - 包含自动访问 Frankfurter API 获取汇率数据的逻辑。

- **templates/index.html**:
  - 前端界面文件。
  - 包含记账本的所有 UI 组件：当前余额、充值/消费表单、收支曲线图、汇率走势图等。
  - 使用 Fetch API 与后端 `app.py` 进行数据交互。
  - 使用 Chart.js 绘制图表。

- **launcher.py**:
  - 启动脚本源码。
  - 用于生成 EXE 可执行文件。
  - 包含自动清理端口、启动 Flask 服务器、自动打开浏览器的逻辑。

- **AccountBook.exe**:
  - 最终生成的可执行程序。
  - Windows 用户双击此文件即可一键启动整个应用（无需手动输命令）。
  - 启动后会自动打开浏览器访问 `http://localhost:3000`。
  - 关闭该黑色窗口即可完全停止服务。

## 环境依赖信息

### Python 版本
- **Python 3.9.13**
- 主要依赖库:
  - `Flask`: Web 框架
  - `pymongo`: MongoDB 驱动
  - `flask-cors`: 处理跨域请求
  - `requests`: 发送 HTTP 请求（用于获取汇率）

### 数据库版本
- **MongoDB**: 本地安装版本 (推荐 4.0+)
- 数据库名称: `accountBook`
- 集合 (Collections):
  - `balance`: 存储当前账户余额
  - `transactions`: 存储每一笔充值和消费记录

## 使用说明
1. 确保本地 MongoDB 服务已启动。
2. 双击 `AccountBook.exe` 启动程序。
3. 在自动打开的浏览器窗口中进行记账操作。

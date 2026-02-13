# Stock Screener - Windows 安装指南

## 系统要求

1. **Python 3.7+** - 已安装 (检测到: Python 3.14.2)
2. **Node.js 14+** - 已安装 (检测到: Node.js v24.13.0)
3. **Git** - 已安装 (用于克隆仓库)

## 安装步骤

### 1. 克隆仓库 (已完成)
```bash
git clone https://github.com/niucool/stock-screener.git
cd stock-screener
```

### 2. 安装后端依赖
```bash
cd backend\api
pip install -r requirements.txt
```

**注意**: TA-Lib 可能需要额外安装。如果安装失败，可以:
1. 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib 下载预编译的 TA-Lib
2. 使用: `pip install TA_Lib‑0.4.28‑cp314‑cp314‑win_amd64.whl`

### 3. 安装前端依赖
```bash
cd ..\..\frontend
npm install
```

### 4. 初始化数据库
```bash
cd ..\backend\data
python init_database.py
```

### 5. 下载股票数据到最新版本

项目已经包含了一些示例数据，但你可能需要更新到最新数据。查看 `test_data_flow.py` 文件了解如何下载最新数据。

## 运行应用程序

### 方法1: 使用 Windows 启动脚本 (推荐)
```bash
cd stock-screener
start_windows.bat
```

### 方法2: 手动启动

#### 启动后端服务器:
```bash
cd backend\api
python app.py
```
后端将在 http://localhost:5001 运行

#### 启动前端服务器:
```bash
cd frontend
set PORT=3001
set BROWSER=none
npm start
```
前端将在 http://localhost:3001 运行

## 访问应用程序

1. 打开浏览器访问: http://localhost:3001
2. 后端API: http://localhost:5001/api

## 故障排除

### 常见问题

1. **TA-Lib 安装失败**
   - 下载预编译版本: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
   - 或使用: `pip install ta` (纯Python版本，性能较差)

2. **端口冲突**
   - 修改 `start_windows.bat` 中的端口号
   - 后端默认: 5001
   - 前端默认: 3001

3. **数据库初始化失败**
   - 确保在 `backend\data` 目录运行 `init_database.py`
   - 检查是否有写权限

4. **前端依赖安装缓慢**
   - 使用淘宝镜像: `npm config set registry https://registry.npmmirror.com`
   - 或使用: `npm install --registry=https://registry.npmmirror.com`

## 更新股票数据

要下载最新的股票数据，可以:

1. 运行测试脚本了解数据流程:
```bash
python test_data_flow.py
```

2. 查看项目中的数据处理脚本

## 项目结构

```
stock-screener/
├── backend/           # Flask 后端
│   ├── api/          # API 代码
│   └── data/         # 数据库和股票数据
├── frontend/         # React 前端
├── logs/            # 日志文件
├── start_windows.bat # Windows 启动脚本
└── README.md        # 项目文档
```

## 技术支持

如果遇到问题:
1. 检查 `logs/` 目录中的日志文件
2. 查看原始项目文档: https://github.com/niucool/stock-screener
3. 确保所有依赖正确安装

## 注意事项

1. 股票数据仅供教育目的
2. 确保遵守相关法律法规
3. 定期更新依赖包以获得安全更新
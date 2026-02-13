# Stock Screener - 快速开始指南

## 🎯 已完成安装

恭喜！Stock Screener 已成功安装在你的Windows系统上。所有依赖都已安装并测试通过。

## 🚀 启动应用程序

### 方法1: 简单启动脚本 (推荐)
```bash
cd stock-screener
start_simple.bat
```

### 方法2: 手动启动

#### 1. 启动后端服务器 (新终端窗口):
```bash
cd backend\api
python app.py
```
后端将在 http://localhost:5001 运行

#### 2. 启动前端服务器 (新终端窗口):
```bash
cd frontend
set PORT=3001
set BROWSER=none
npm start
```
前端将在 http://localhost:3001 运行

## 🌐 访问应用程序

1. 打开浏览器
2. 访问: http://localhost:3001
3. 你将看到股票筛选器界面

## 📊 添加股票数据

当前数据库是空的。要添加数据:

### 选项1: 使用现有JSON数据
项目包含示例JSON数据文件在:
- `backend\data\stocks\historical\` - 历史数据
- `backend\data\stocks\processed\` - 处理后的数据

### 选项2: 下载最新数据
查看 `test_data_flow.py` 了解如何下载最新股票数据。

## 🔧 技术特性

### 支持的筛选指标:
- Williams %R (14, 21周期)
- EMA of Williams %R
- RSI (14, 21周期)
- 50+ 其他技术指标

### 功能:
- 实时数据筛选
- 交互式数据表格
- 个股详细信息查看
- 数据导出功能
- 响应式设计

## ⚠️ 注意事项

1. **数据源**: 使用 yfinance 获取免费股票数据
2. **延迟**: 免费数据可能有15分钟延迟
3. **教育用途**: 仅供学习和研究使用
4. **更新数据**: 定期运行数据更新脚本

## 🆘 常见问题

### Q: 页面显示无数据
A: 数据库需要导入数据。查看"添加股票数据"部分。

### Q: 端口被占用
A: 修改启动脚本中的端口号:
- 后端: 修改 `app.py` 中的端口
- 前端: 修改 `set PORT=3002` (或其他端口)

### Q: 依赖安装失败
A: 重新安装:
```bash
# 后端
cd backend\api
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### Q: 如何更新到最新数据?
A: 运行数据更新脚本或查看 `test_data_flow.py`

## 📁 项目结构

```
stock-screener/
├── backend/           # Flask后端
│   ├── api/          # API代码 (app.py)
│   └── data/         # 数据库和股票数据
├── frontend/         # React前端
├── logs/            # 日志文件
├── start_simple.bat # 启动脚本
└── README.md        # 项目文档
```

## 🔄 更新应用程序

### 更新代码:
```bash
git pull origin main
```

### 更新依赖:
```bash
# 后端
cd backend\api
pip install -r requirements.txt --upgrade

# 前端
cd frontend
npm update
```

## 📞 支持

如果遇到问题:
1. 检查 `logs/` 目录中的日志
2. 查看原始项目: https://github.com/niucool/stock-screener
3. 确保Python和Node.js版本符合要求

## 🎉 开始使用

现在你可以:
1. 启动应用程序
2. 导入或下载股票数据
3. 使用技术指标筛选股票
4. 分析筛选结果
5. 导出数据用于进一步分析

祝你使用愉快！
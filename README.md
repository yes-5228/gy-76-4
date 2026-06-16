# 少儿培训考勤系统

Flask + React 实现的少儿培训机构考勤与经营辅助系统，覆盖学员签到打卡、课时扣减统计、续费提醒和教师课酬结算。

## 功能

- 学员管理：新增学员、查看剩余课时、续费提醒状态
- 签到打卡：选择学员和教师登记上课记录，并自动扣减课时
- 统计看板：总学员、低课时提醒、本月课消、本月课酬
- 续费提醒：按剩余课时阈值筛选需要跟进的学员
- 教师课酬：按月份统计教师课时、应发课酬，并支持标记结算

## 项目结构

```text
.
├── backend
│   ├── app
│   │   ├── routes        # Flask 蓝图接口
│   │   ├── services      # 业务逻辑
│   │   └── storage.py    # JSON 持久化
│   ├── requirements.txt
│   └── run.py
├── frontend
│   ├── src
│   │   ├── api           # API 客户端
│   │   ├── components    # 通用组件
│   │   ├── pages         # 页面模块
│   │   └── utils
│   └── package.json
└── docker-compose.yml
```

## 本地开发

### 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

后端默认运行在 `http://127.0.0.1:5000`。

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://127.0.0.1:5173`。

## Docker Compose 启动

```bash
docker compose up --build
```

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:5000`
- 数据卷：`attendance_data`

## 常用接口

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/students`
- `POST /api/students`
- `GET /api/attendance`
- `POST /api/attendance`
- `GET /api/reminders`
- `GET /api/payroll?month=YYYY-MM`
- `POST /api/payroll/settle`

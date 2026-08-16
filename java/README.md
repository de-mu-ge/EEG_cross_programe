# NEURO-AI · 脑电情绪识别系统

基于 EEG 脑电数据的情绪识别平台。上传 `.dat` 脑电文件，即可获得情绪（效价二分类）与置信度。

- **前端**：Vue 3 + Vite + Three.js —— 体素粒子大脑首页，交互式转场动画
- **后端**：Spring Boot 3.3 + MyBatis-Plus + MySQL 8

---

## 面向新手:

这个系统由 **3 个独立服务 + 1 个数据库** 组成，它们要**同时启动**才能完整运行：

```
你的浏览器
   │  打开 http://localhost:5173
   ▼
【前端】frontend/  ──端口 5173──  网页界面（上传 .dat、显示情绪结果）
   │  自动把请求转发到 8080（Vite 已配好代理，无需你操心跨域）
   ▼
【后端】backend/   ──端口 8080──  中转站（接收上传 → 存文件 → 调 AI → 结果写进数据库）
   │  HTTP 调用 http://localhost:8000/api/predict
   ▼
【AI 服务】python-service/  ──端口 8000──  真正的"识别大脑"（解析脑电数据 → 输出情绪）
   │
   ▼
【数据库】MySQL  ──端口 3306──  存每次分析的记录（不属于本项目目录，需自己装）
```

**关键认知：**
- 三个服务的启动顺序不影响"能否启动"，但**完整功能需要三者都活着**（AI 服务没起 → 上传会报 502）。
- **没有模型权重也能跑通**：AI 服务会进入"演示模式"，不管传什么文件都返回固定的 `happy / 0.92`。要真实识别，按【接入真实模型】操作即可，接口一行都不用改。

---

## 目录结构:

```
EEG_Project/                      # 项目根目录
├── backend/                      # 【后端】Spring Boot，端口 8080
│   └── src/main/
│       ├── java/com/neuroai/backend/   # Java 源码
│       │   ├── controller/   # 接口层：接收浏览器请求（upload / result 两个接口）
│       │   ├── service/      # 业务逻辑：编排"存文件→调AI→落库"
│       │   ├── mapper/       # 数据库操作层（MyBatis-Plus）
│       │   ├── entity/       # 数据表对应的实体类
│       │   ├── dto/ vo/      # 数据传输对象 / 返回给前端的对象
│       │   ├── config/       # 配置类（跨域、RestTemplate 超时）
│       │   ├── properties/   # 读取 application.yml 配置
│       │   ├── exception/    # 统一异常处理
│       │   └── NeuroAiApplication.java   # 后端启动入口
│       └── resources/
│           ├── application.yml     # 后端配置（端口、数据库连接、上传大小等）
│           └── db/schema.sql       # ★ 数据库建表脚本（第一次装时执行一次）
├── frontend/                     # 【前端】Vue3 网页，端口 5173
│   ├── src/
│   │   ├── views/HomeView.vue   # 首页（大脑动画 + 上传区）
│   │   ├── components/          # 组件（BrainCanvas 大脑画布 / UploadZone 上传区）
│   │   ├── three/BrainScene.js  # ★ Three.js 大脑动画的完整逻辑
│   │   ├── api/eeg.js           # 前端调用后端接口的方法（上传 / 查结果）
│   │   ├── router/index.js      # 路由（只有首页）
│   │   └── styles/global.css    # 全局样式
│   ├── vite.config.js           # 前端配置（端口 5173、/api 代理到 8080）
│   └── package.json             # 前端依赖清单
├── python-service/              # 【AI 服务】FastAPI，端口 8000
│   ├── app/
│   │   ├── config.py            # ★ 配置：模型路径、设备、演示模式开关（读 .env）
│   │   ├── model.py             # 模型结构定义（Moudle 类）
│   │   └── main.py              # ★ AI 服务主程序：/api/health 和 /api/predict 两个接口
│   ├── models/                  # ★ 把训练好的模型权重文件放这里（默认 eeg_model.pt）
│   ├── scripts/                 # 预留脚本目录（当前为空）
│   ├── requirements.txt         # Python 依赖清单
│   └── .env.example             # 环境变量示例（接入真实模型时复制为 .env 用）
├── README.md                    # 本文档
└── .gitignore                   # git 忽略规则（node_modules、权重文件等不入库）
```

> 不需要懂所有文件。日常只关心三件事：**后端启动**、**AI 服务启动与模型**、**前端启动**，都在【快速开始】里。

---

## 前置要求:

| 软件 | 版本 | 怎么确认已安装 |
|---|---|---|
| JDK | 17 | 命令行执行 `java -version`，能看到 `17.x` 即可 |
| Maven | 3.8+ | `mvn -version` |
| Node.js | 18+ | `node -v` |
| Python | 3.10+ | `python --version`（或 `python3 --version`） |
| MySQL | 8.x | 能连上本机 `localhost:3306`（可用 Navicat / MySQL Workbench 测试） |

> Windows 上 `python` 与 `.venv/Scripts/` 前缀通用；macOS / Linux 把命令里的 `.venv/Scripts/` 换成 `./.venv/bin/`，`python` 换成 `python3`。

---

## 快速开始（照着复制执行即可）

### 第 1 步：初始化数据库（只需第一次执行）

```bash
mysql -uroot -p < backend/src/main/resources/db/schema.sql
```

- 回车后会提示输入 MySQL 的 root 密码，输入后回车。
- 脚本会**自动创建** `neuroai` 库和 `eeg_analysis_record` 表（可以重复执行，不会出错）。

### 第 2 步：启动 AI 服务（端口 8000）

```bash
cd python-service                 # 进入 AI 服务目录
python -m venv .venv              # 创建虚拟环境（第一次需要）
.venv/Scripts/pip install -r requirements.txt   # 安装依赖（第一次需要，含 torch 约几百 MB）
.venv/Scripts/python -m uvicorn app.main:app --port 8000   # 启动
```

- 看到 `Uvicorn running on http://127.0.0.1:8000` 说明启动成功。
- **没装 torch / 没放模型也能启动**（自动演示模式），只是结果固定为 `happy / 0.92`。
- 想省磁盘、暂时不接真实模型，可跳过 torch 只装轻量版：
  `.venv/Scripts/pip install fastapi "uvicorn[standard]" python-multipart numpy pydantic python-dotenv`

### 第 3 步：启动后端（端口 8080）

```bash
export NEUROAI_DB_PASSWORD=你的MySQL密码   # 告诉后端你的数据库密码
                                           # Windows PowerShell 用：$env:NEUROAI_DB_PASSWORD="你的MySQL密码"
cd backend
mvn spring-boot:run
```

- 看到 `Started NeuroAiApplication in x.x seconds` 即启动成功。
- 数据库密码默认按 `root` 处理；如果你的密码不是 `root`，**必须**先设上面这行环境变量，否则连不上数据库。
- 也可以直接改 `backend/src/main/resources/application.yml` 里 `password` 的默认值（改完提交前记得别把真实密码推上公开仓库）。

### 第 4 步：启动前端（端口 5173）

```bash
cd frontend
npm install       # 第一次需要，装前端依赖
npm run dev       # 启动开发服务器
```

- 浏览器打开 **http://localhost:5173**，点 START ANALYSIS，把 `.dat` 文件拖进去即可看到结果。
- 前端已配置 `/api` → `localhost:8080` 的代理，无需额外配置跨域。

---

## 接入真实模型:

> 本节专为新手编写。**不接也能跑**（演示模式），但结果固定；接上后才是真实识别，且**后端、前端、接口都不需要改动**。

### 先弄懂 4 个概念（大白话）

1. **模型权重文件**（`.pt` / `.pth`）
   训练好的"参数包"，相当于 AI 的"大脑"。系统加载它，才能把脑电数据换算成情绪判断。没有它就等于 AI 没长脑子 → 自动退回演示模式。
2. **演示模式 vs 真实模式**
   演示模式：AI 服务**不解析**文件内容，任何 `.dat` 都返回固定的 `happy / 0.92`（用于跑通链路）。
   真实模式：AI 服务**解析**脑电数据 → 加载模型 → 算出真实的情绪和置信度。
   判断当前是哪种：看 `http://localhost:8000/api/health` 返回的 `model_loaded` 字段——`true` 是真实模式，`false` 是演示模式。
3. **`.env` 配置文件**
   一个纯文本文件，用来给程序传"环境变量"（模型在哪、用什么设备算等）。程序启动时自动读取。它已被 `.gitignore` 忽略，**不会提交到 GitHub**，所以可以放心写自己的路径。
4. **DEAP pickle 格式的 `.dat`**
   真实模型能识别的脑电文件是 DEAP 数据集的标准格式（内容是一个 dict：`data` 形状 `(40, 40, 8064)` 的脑电矩阵 + `labels` 形状 `(40, 4)` 的标签）。**普通文本文件改后缀成 `.dat` 是无效的**，真实模式下会解析失败。

### 第 1 步：安装 PyTorch（torch）

```bash
cd python-service
.venv/Scripts/pip install torch
```

验证是否装成功：

```bash
.venv/Scripts/python -c "import torch; print(torch.__version__)"
```

能打印出版本号（如 `2.2.x`）即成功。

### 第 2 步：把模型权重文件放进来

- **推荐位置**：`python-service/models/eeg_model.pt`
  （即把训练好的权重复制/移动到该路径，文件名改成 `eeg_model.pt`）
- 如果你的权重在**别的路径**、或**文件名不同**，不必移动文件——直接在第 3 步用 `MODEL_PATH` 指过去。
- 该目录已配置 `gitignore`，权重文件不会被提交进仓库。

### 第 3 步：创建 `.env` 配置文件

```bash
cd python-service
cp .env.example .env        # Windows 无 cp 命令时：复制 .env.example 并改名 .env
```

然后编辑 `.env`，逐项确认：

```bash
MODEL_PATH=models/eeg_model.pt   # 模型权重路径（相对 python-service 目录，或写绝对路径）
DEVICE=cpu                       # 计算设备：cpu；有 NVIDIA 显卡且想用 GPU 可改 cuda
DEMO_MODE=0                      # 0=自动：模型和依赖齐全就真实推理，否则演示兜底；1=强制演示
```

- `MODEL_PATH` 写法示例：
  - 相对路径（默认）：`MODEL_PATH=models/eeg_model.pt`
  - 绝对路径（权重在别处时）：`MODEL_PATH=C:/Users/xxx/Desktop/weights/eeg_model.pth`（Windows 用正斜杠 `/`）
- 写完后保存即可，**不需要重新创建虚拟环境**。

### 第 4 步：重启 AI 服务并确认成功

1. 停掉正在运行的 uvicorn：在它的终端窗口按 `Ctrl + C`。
2. 重新启动：

```bash
cd python-service
.venv/Scripts/python -m uvicorn app.main:app --port 8000
```

3. 打开浏览器访问 **http://localhost:8000/api/health**（或命令行 `curl http://localhost:8000/api/health`），核对返回：

```json
{"status":"UP","model_loaded":true,"model_path":".../eeg_model.pt","demo_mode":false,"device":"cpu"}
```

- ✅ **`model_loaded: true` 且 `demo_mode: false`** → 接入成功，可以上传真实 `.dat` 测真实结果。
- ❌ `model_loaded: false` → 对照下表排查：

| 现象 | 原因 / 解决 |
|---|---|
| `model_loaded: false` | ① torch 没装（回第 1 步）；② `MODEL_PATH` 指向的文件不存在（检查路径、文件名、大小写）；③ 改完 `.env` 没重启服务 |
| `demo_mode: false` 但结果像演示值 | 权重文件是坏的 / 加载抛异常，看服务终端报错信息 |

### 真实模式下能识别的 `.dat` 长什么样

- 必须是 **DEAP pickle 格式**的脑电数据（如 DEAP 数据集里的 `s01.dat`、`s02.dat`…，单个约 100 MB）。
- 本项目这套模型的实际样例（本机示例路径）：`C:\Users\asus\Desktop\ProJects\My_Part\s01.dat`
- 上传后 AI 服务会：解析 `data` 前 32 个 EEG 通道 → 40 试次 × 4 窗口共 160 个窗口 → 逐窗推理 → **聚合平均 sigmoid 概率后取最大** → 输出情绪与置信度。
- 常见报错：
  - 上传返回 **502**：AI 服务没启动，或传的不是有效 DEAP pickle（解析失败）。
  - 上传返回 **400**：文件后缀不是 `.dat`，或超过 200MB。

---

## 关于原始脚本 predict.py（AI 服务的代码来源）

> 本项目 AI 服务（`python-service/app/`）的代码源于推理脚本 `predict.py`。该脚本**从未被修改、也不在运行时被调用**，仅作为参考原稿保留在项目外。需要明白：**运行时真正执行的是 `app/` 里的 FastAPI 服务**，`predict.py` 是它的"前身"。

### 原始脚本


- 它是一次性命令行脚本（跑完就退出），按顺序做 5 件事：
  1. 定义神经网络 `Moudle`：`Linear(2016,1) → 压平 → Linear(32,2)`
  2. 读取**硬编码目录** `ProJects/test/input` 下的所有 DEAP pickle `.dat`，取前 32 个 EEG 通道，切成 40 试次 × 4 窗口 = 160 个样本
  3. 加载**硬编码路径**的模型权重 `ProJects/test/mod/eeg_model.pth`
  4. 逐窗口推理 → sigmoid → argmax 取最大类别序号
  5. 结果写入**硬编码路径** `ProJects/test/output/out.json`，打印"程序完成"

### 与项目内文件的对应关系

| predict.py 的部分 | 项目里的位置 | 差异 |
|---|---|---|
| `Moudle` 类 | `python-service/app/model.py` | **照搬，未改动** |
| 读 pickle / 取前 32 通道 / 切 160 窗口 | `python-service/app/main.py` 的 `_parse_windows()` | 逻辑相同；但**一次只处理一个上传文件**（不再扫整个目录） |
| 权重路径（写死） | `python-service/app/config.py` 的 `MODEL_PATH` | 改为环境变量，可配置 |
| 设备 cuda/cpu | `python-service/app/config.py` 的 `DEVICE` | 默认 `cpu`，可配置 |
| 逐窗推理 + argmax | `python-service/app/main.py` 的 `_predict_real()` | **修复了覆盖 BUG**（见下） |
| 结果写 out.json | 由后端存进 MySQL | 不再写本地文件 |

### 为什么没有直接调用 predict.py（3 点关键差异）

1. **修复了一个 BUG。** 原脚本里 `out` 变量在循环中被反复覆盖，循环结束后 `out.json` 只留下**最后一个窗口**的结果——也就是说原脚本的结果并不可靠。项目版改为：**把所有 160 个窗口的概率平均后**再取最大，结果更稳。
2. **多输出一个置信度。** 原脚本只输出 0/1 标签；项目版额外输出 `confidence`（获胜类的平均概率），前端能显示"happy · 92.0%"。
3. **从"一次性脚本"变成"常驻服务"。** 原脚本每次运行都要重载模型、扫描固定目录、写死路径，不适合网页"每次上传都调用一次"。FastAPI 服务**启动时只加载一次模型**，每次上传只处理那一个文件，结果返回给后端入库。



> 平台没有直接调用原脚本 `predict.py`（它读整个目录、路径写死、且结果只保留最后一个窗口）。而是把它的模型类原样放进 `model.py`，解析与推理逻辑放进 `main.py` 并修复了覆盖 BUG，路径改成 `.env` 可配置。原脚本未做任何改动，仍作为参考保留。

---

## 接口说明

| 方法 | 路径 | 作用 | 返回示例 |
|---|---|---|---|
| POST | `/api/eeg/upload` | 上传 `.dat`（multipart 的 `file` 字段，≤200MB），同步分析完成后返回 fileId | `{"code":200,"message":"upload success","data":{"fileId":1}}` |
| GET | `/api/eeg/result/{id}` | 按 fileId 查询分析结果 | `{"code":200,"message":"success","data":{"emotion":"happy","confidence":0.92}}` |
| GET | `:8000/api/health` | AI 服务健康检查（模型是否加载、演示模式标志） | `{"status":"UP","model_loaded":true,...}` |

统一返回格式 `{code, message, data}`；`code`：200 成功、400 参数/文件非法、404 记录不存在、502 AI 服务不可用。

---

## 环境变量一览

| 变量 | 默认值 | 属于哪个服务 | 作用 |
|---|---|---|---|
| `NEUROAI_DB_URL` | `jdbc:mysql://localhost:3306/neuroai?...` | 后端 | 数据库连接地址 |
| `NEUROAI_DB_USERNAME` | `root` | 后端 | 数据库用户名 |
| `NEUROAI_DB_PASSWORD` | `root` | 后端 | 数据库密码（**必须**改成你本机的） |
| `MODEL_PATH` | `python-service/models/eeg_model.pt` | AI 服务 | 模型权重路径 |
| `DEVICE` | `cpu` | AI 服务 | 推理设备：`cpu` / `cuda` |
| `DEMO_MODE` | `0` | AI 服务 | `1` 强制演示模式；`0` 自动判断 |

---

## 常见问题（全流程）

| 现象 | 原因 / 解决 |
|---|---|
| 上传返回 502 | AI 服务没启动；或真实模式下模型没加载成功 / `.dat` 不是有效 DEAP pickle |
| 上传返回 400 | 仅支持 `.dat` 文件，且 ≤200MB |
| 上传后显示 "DONE" | 浏览器缓存了旧页面 → **硬刷新**（Ctrl+F5）后重新上传 |
| 后端启动报数据库连接失败 | MySQL 没启动；或 `NEUROAI_DB_PASSWORD` 与你本机密码不一致 |
| 前端页面 404 / 白屏 | 没在 `frontend/` 目录执行过 `npm install` / `npm run dev` |
| 端口被占用（5173/8080/8000） | 改对应配置文件：`frontend/vite.config.js` 的 `server.port`、`backend/src/main/resources/application.yml` 的 `server.port`、启动命令里的 `--port` |
| 网页上传了但没反应 | 检查后端终端日志是否有报错；确认三个服务都活着 |

# StudyTask 个人学习任务管理系统

> **《软件工程》课程实验一：AI驱动的个人学习任务管理系统**  
> **学生姓名**：李哲涵 | **学号**：242806010109 | **班级**：24计科一班  
> **代码仓库**：https://github.com/ZH0606862/StudyTask  
> **Web在线访问地址**：https://studytask-6uuz.onrender.com

---

## 1. 项目简介与功能概述

本项目为单用户本地 Web 学习任务管理应用（代号：**StudyTask**），旨在协助大学生高效记录与跟踪课程作业、实验及考试准备。系统严格依据《软件工程》实验指导书附录 A 软件需求规格说明书（SRS）实现，核心功能如下：

- **FR-01 任务创建与表单校验**：支持录入任务名称（1~100字）、所属课程（1~60字）、截止日期（YYYY-MM-DD）、优先级（高/中/低）、状态及描述；非法输入与必填项阻断并提供友好中文提示。
- **FR-02 任务展示与详情查看**：列表完整展示任务的核心元数据，支持点击进入详情页查看完整描述及时间戳。
- **FR-03 任务编辑与修改**：支持在独立编辑页面对任务任意字段进行更新，保存后列表与详情即时同步。
- **FR-04 二次确认防误删**：点击删除触发原生确认弹窗，取消则保留，确认后自 SQLite 数据库物理移除。
- **FR-05 状态便捷流转**：支持任务在“待完成”、“进行中”、“已完成”三态间自由切换并即时持久化。
- **FR-06 多维组合条件筛选**：支持按所属课程、任务状态、优先级进行单条件或多条件组合交叉筛选。
- **FR-07 动态临期与逾期预警**：
  - 未完成且截止日期早于今天：红色高亮标记 `⚠️ 已逾期`；
  - 未完成且截止日期在今日起未来 3 天内：橙色高亮标记 `⏰ 即将到期`；
  - 已完成任务自动清除逾期与临期警报。
- **FR-08 统计看板与进度跟踪**：动态呈现任务总数、已完成数与整体完成率；在任务总数为 0 时精确显示 0.0%，杜绝除零崩溃。
- **FR-09 本地数据持久化**：使用轻量级 SQLite 数据库存储，应用关闭及系统重启后数据完整保留。
- **FR-10 鲁棒性与异常防护**：全局中文提示，具备 404 与 500 容错处理机制。

---

## 2. 技术栈与环境要求

- **开发语言**：Python 3.11+（兼容 Python 3.13）
- **Web 框架**：Flask 3.x
- **数据库**：SQLite 3
- **前端交互**：原生 HTML5 + CSS3 + 现代响应式排版（无冗余外部重型框架）
- **测试框架**：pytest 8.x+

---

## 3. 从零开始的本地运行指南

### 步骤 1：克隆或下载代码
```bash
git clone <你的仓库地址>
cd StudyTask
```

### 步骤 2：创建并激活虚拟环境（推荐）
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 步骤 3：安装项目依赖
```bash
pip install -r requirements.txt
```

### 步骤 4：（可选）初始化演示数据
系统默认会在首次启动时自动建立数据库。若希望预置 5 条涵盖不同课程、优先级及逾期/临期状态的测试数据，可运行：
```bash
python init_demo_data.py
```

### 步骤 5：启动 Web 服务
```bash
python app.py
```
启动成功后，终端将输出运行提示，打开桌面浏览器访问：
👉 **http://127.0.0.1:5000**

---

## 4. 自动化测试与用例复现指南

本项目包含完整的自动化测试集（`tests/test_study_task.py`），严格覆盖了指导书第 2.5 节要求的 **T1~T10 最低验收用例** 以及 **0 任务除零安全测试**。

执行全部测试：
```bash
pytest -v
```

**测试覆盖矩阵说明：**
| 测试用例编号 | 测试函数名 | 验证的核心需求 | 期望结果与断言 |
| :--- | :--- | :--- | :--- |
| **T1** | `test_case_t1_create_task` | FR-01 新建任务 | 提交数据结构、明天截止任务，列表正确展示 |
| **T2** | `test_case_t2_empty_title_validation` | FR-01, FR-10 输入校验 | 提交空白任务名，返回400错误提示且不产生脏数据 |
| **T3** | `test_case_t3_modify_task` | FR-03 任务编辑 | 更新描述与优先级，持久保存并反映在详情页 |
| **T4** | `test_case_t4_status_transition` | FR-05 状态流转 | 待完成 $\rightarrow$ 进行中 $\rightarrow$ 已完成 逐次更新 |
| **T5** | `test_case_t5_filter_tasks` | FR-06 组合筛选 | 按课程、状态、优先级单选及三者组合匹配 |
| **T6** | `test_case_t6_overdue_flag` | FR-07 逾期标记 | 昨日截止未完成任务高亮显示“已逾期” |
| **T7** | `test_case_t7_due_soon_flag` | FR-07 临期标记 | 明日截止未完成任务高亮显示“即将到期” |
| **T8** | `test_case_t8_statistics_calculation` | FR-08 统计看板 | 录入5项完成2项，总数5、完成数2、完成率40% |
| **T9** | `test_case_t9_delete_task` | FR-04 二次确认删除 | 取消不操作，确认后自数据库彻底删除 |
| **T10** | `test_case_t10_persistence_after_restart` | FR-09 数据持久化 | 写入数据后关闭连接重启，数据完整复原 |
| **边界测试** | `test_case_zero_tasks_completion_rate` | FR-08 健壮性 | 数据库为空时，完成率准确显示 0.0% |

---

## 5. 云服务器与公网部署指南（获取Web访问地址）

针对实验提交要求的“网站的Web地址”，可选用以下任意一种方式获取：

### 方案 A：云服务器（Ubuntu / Debian / CentOS）常规部署
1. 将代码上传到服务器目录。
2. 安装环境：`sudo apt update && sudo apt install python3-pip python3-venv`。
3. 创建虚拟环境并安装依赖：`pip install -r requirements.txt gunicorn`。
4. 后台运行：
   ```bash
   nohup gunicorn -w 2 -b 0.0.0.0:80 app:app > app.log 2>&1 &
   ```
5. 开放云服务器安全组 80 端口，即可通过 `http://<你的服务器公网IP>` 访问。

### 方案 B：Render / PythonAnywhere 免费托管（推荐，零成本）
1. 将项目推送到 GitHub。
2. 登录 [Render](https://render.com/)，选择 “New Web Service” 并关联本仓库。
3. Build Command 填入：`pip install -r requirements.txt`。
4. Start Command 填入：`gunicorn app:app`。
5. 部署完成后即可获得免费独立的公网域名（如 `https://studytask-xxx.onrender.com`）。

---

## 6. 已知限制说明 (Known Limitations)

1. **单用户单机定位**：依据 SRS A.5 范围外要求，系统未设用户注册鉴权，仅供单人本地/受限网络内管理任务。
2. **基准时间依赖**：逾期与临期状态由宿主机系统本地时钟动态计算，如需测试特定年份请调整系统时间或使用测试 fixture。
3. **数据并发建议**：使用 SQLite 文件型数据库，更适合常规学生体量（几百条数据级流畅操作），不适用于高并发分布式写入。

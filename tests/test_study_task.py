import os
import tempfile
import pytest
from datetime import date, timedelta
from app import app
from models import (
    init_db,
    create_task,
    get_task_by_id,
    update_task,
    update_task_status,
    delete_task,
    list_tasks,
    get_statistics,
    enrich_task
)


@pytest.fixture
def client():
    # 创建独立的临时数据库文件，隔离测试数据
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)  # 立即关闭文件句柄，避免 Windows 文件占用冲突
    app.config["DATABASE"] = db_path
    app.config["TESTING"] = True
    init_db(db_path)

    with app.test_client() as client:
        yield client

    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except OSError:
        pass


def test_case_t1_create_task(client):
    """
    T1: 新建：课程“数据结构”、明天截止、高优先级
    期望结果：列表显示新增任务
    """
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    response = client.post("/tasks/new", data={
        "title": "数据结构作业1",
        "course": "数据结构",
        "description": "完成二叉树遍历实验",
        "due_date": tomorrow,
        "priority": "高",
        "status": "待完成"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "任务创建成功" in response.get_data(as_text=True)
    assert "数据结构作业1" in response.get_data(as_text=True)
    assert "数据结构" in response.get_data(as_text=True)


def test_case_t2_empty_title_validation(client):
    """
    T2: 名称为空提交新任务
    期望结果：提示错误，不产生脏数据
    """
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    response = client.post("/tasks/new", data={
        "title": "   ",  # 空字符串/空格
        "course": "操作系统",
        "description": "测试空标题",
        "due_date": tomorrow,
        "priority": "中",
        "status": "待完成"
    }, follow_redirects=True)

    # 400 校验错误响应
    assert "任务名称不能为空" in response.get_data(as_text=True)

    # 验证数据库中无脏数据
    list_resp = client.get("/")
    assert "操作系统" not in list_resp.get_data(as_text=True)


def test_case_t3_modify_task(client):
    """
    T3: 修改任务描述与优先级
    期望结果：修改成功且刷新后保留
    """
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    # 先创建一个任务
    client.post("/tasks/new", data={
        "title": "待修改任务",
        "course": "软件工程",
        "description": "初始描述",
        "due_date": tomorrow,
        "priority": "低",
        "status": "待完成"
    }, follow_redirects=True)

    # 获取该任务ID
    db_path = app.config["DATABASE"]
    tasks = list_tasks(course="软件工程", db_path=db_path)
    assert len(tasks) == 1
    task_id = tasks[0]["id"]

    # 执行修改：描述变为“修改后的描述”，优先级变为“高”
    edit_resp = client.post(f"/tasks/{task_id}/edit", data={
        "title": "待修改任务",
        "course": "软件工程",
        "description": "修改后的描述-已更新",
        "due_date": tomorrow,
        "priority": "高",
        "status": "进行中"
    }, follow_redirects=True)

    assert edit_resp.status_code == 200
    assert "任务修改成功" in edit_resp.get_data(as_text=True)

    # 刷新并验证详情页与主页
    detail_resp = client.get(f"/tasks/{task_id}")
    detail_html = detail_resp.get_data(as_text=True)
    assert "修改后的描述-已更新" in detail_html
    assert "高优先级" in detail_html


def test_case_t4_status_transition(client):
    """
    T4: 待完成 → 进行中 → 已完成
    期望结果：状态逐次正确更新
    """
    db_path = app.config["DATABASE"]
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    _, task_id = create_task({
        "title": "状态流转测试",
        "course": "计算机网络",
        "description": "流转测试",
        "due_date": tomorrow,
        "priority": "中",
        "status": "待完成"
    }, db_path=db_path)

    # 初始为 待完成
    task = get_task_by_id(task_id, db_path=db_path)
    assert task["status"] == "待完成"

    # 流转到 进行中
    client.post(f"/tasks/{task_id}/status", data={"status": "进行中"}, follow_redirects=True)
    task = get_task_by_id(task_id, db_path=db_path)
    assert task["status"] == "进行中"

    # 流转到 已完成
    client.post(f"/tasks/{task_id}/status", data={"status": "已完成"}, follow_redirects=True)
    task = get_task_by_id(task_id, db_path=db_path)
    assert task["status"] == "已完成"


def test_case_t5_filter_tasks(client):
    """
    T5: 分别筛选课程、状态和优先级
    期望结果：结果只包含匹配任务
    """
    db_path = app.config["DATABASE"]
    today = date.today().strftime("%Y-%m-%d")

    # 创建多样化数据
    create_task({"title": "网络作业A", "course": "计网", "due_date": today, "priority": "高", "status": "待完成"}, db_path=db_path)
    create_task({"title": "数据库作业B", "course": "数据库", "due_date": today, "priority": "低", "status": "进行中"}, db_path=db_path)
    create_task({"title": "数据库作业C", "course": "数据库", "due_date": today, "priority": "高", "status": "已完成"}, db_path=db_path)

    # 按课程筛选：数据库 -> 只有B和C
    resp_course = client.get("/?course=数据库")
    html_course = resp_course.get_data(as_text=True)
    assert "数据库作业B" in html_course
    assert "数据库作业C" in html_course
    assert "网络作业A" not in html_course

    # 按状态筛选：已完成 -> 只有C
    resp_status = client.get("/?status=已完成")
    html_status = resp_status.get_data(as_text=True)
    assert "数据库作业C" in html_status
    assert "网络作业A" not in html_status
    assert "数据库作业B" not in html_status

    # 按优先级筛选：高 -> 只有A和C
    resp_pri = client.get("/?priority=高")
    html_pri = resp_pri.get_data(as_text=True)
    assert "网络作业A" in html_pri
    assert "数据库作业C" in html_pri
    assert "数据库作业B" not in html_pri

    # 组合筛选：课程=数据库 且 优先级=高 且 状态=已完成 -> 仅有C
    resp_combo = client.get("/?course=数据库&priority=高&status=已完成")
    html_combo = resp_combo.get_data(as_text=True)
    assert "数据库作业C" in html_combo
    assert "网络作业A" not in html_combo
    assert "数据库作业B" not in html_combo


def test_case_t6_overdue_flag(client):
    """
    T6: 新增昨日到期且未完成的任务
    期望结果：显示逾期标识
    """
    db_path = app.config["DATABASE"]
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    create_task({
        "title": "昨日到期作业",
        "course": "编译原理",
        "description": "昨天截止的实验",
        "due_date": yesterday,
        "priority": "高",
        "status": "待完成"
    }, db_path=db_path)

    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert "昨日到期作业" in html
    assert "已逾期" in html


def test_case_t7_due_soon_flag(client):
    """
    T7: 新增明日到期且未完成的任务
    期望结果：显示即将到期标识
    """
    db_path = app.config["DATABASE"]
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    create_task({
        "title": "明日到期作业",
        "course": "人工智能",
        "description": "明天截止的报告",
        "due_date": tomorrow,
        "priority": "中",
        "status": "进行中"
    }, db_path=db_path)

    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert "明日到期作业" in html
    assert "即将到期" in html


def test_case_t8_statistics_calculation(client):
    """
    T8: 创建5项、完成2项
    期望结果：总数5、完成数2、完成率40%
    """
    db_path = app.config["DATABASE"]
    today = date.today().strftime("%Y-%m-%d")

    # 创建 5 项任务
    for i in range(1, 6):
        status = "已完成" if i <= 2 else "待完成"
        create_task({
            "title": f"任务{i}",
            "course": "测试课",
            "due_date": today,
            "priority": "中",
            "status": status
        }, db_path=db_path)

    stats = get_statistics(db_path=db_path)
    assert stats["total"] == 5
    assert stats["completed"] == 2
    assert stats["completion_rate"] == 40.0

    resp = client.get("/")
    html = resp.get_data(as_text=True)
    assert 'id="stat-total">5</div>' in html
    assert 'id="stat-completed">2</div>' in html
    assert 'id="stat-rate">40.0%</div>' in html or '40%' in html


def test_case_t9_delete_task(client):
    """
    T9: 删除一项任务并取消/确认操作
    期望结果：取消不删除、确认后删除
    """
    db_path = app.config["DATABASE"]
    today = date.today().strftime("%Y-%m-%d")
    _, task_id = create_task({
        "title": "待删除任务",
        "course": "离散数学",
        "due_date": today,
        "priority": "低",
        "status": "待完成"
    }, db_path=db_path)

    # 1. 模拟用户点击“取消”：不向服务器发送删除请求，数据依然完好
    task_before = get_task_by_id(task_id, db_path=db_path)
    assert task_before is not None

    # 2. 模拟用户点击“确定”：发送 POST 请求删除
    del_resp = client.post(f"/tasks/{task_id}/delete", follow_redirects=True)
    assert del_resp.status_code == 200

    # 验证已从数据库中彻底清除
    task_after = get_task_by_id(task_id, db_path=db_path)
    assert task_after is None


def test_case_t10_persistence_after_restart():
    """
    T10: 关闭并重新启动系统
    期望结果：已保存数据仍可查询（持久化验证）
    """
    db_fd, temp_db_file = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    try:
        # 第一轮启动应用并写入数据
        init_db(temp_db_file)
        create_task({
            "title": "持久化测试任务",
            "course": "软件体系结构",
            "description": "重启后验证是否依然存在",
            "due_date": "2026-12-31",
            "priority": "高",
            "status": "待完成"
        }, db_path=temp_db_file)

        # 模拟关闭系统：无任何驻留连接或内存缓存，再次新建数据库连接
        # 第二轮启动应用并查询数据
        tasks_restarted = list_tasks(course="软件体系结构", db_path=temp_db_file)
        assert len(tasks_restarted) == 1
        assert tasks_restarted[0]["title"] == "持久化测试任务"
        assert tasks_restarted[0]["due_date"] == "2026-12-31"

    finally:
        try:
            if os.path.exists(temp_db_file):
                os.remove(temp_db_file)
        except OSError:
            pass


def test_case_zero_tasks_completion_rate(client):
    """
    额外边界测试：任务总数为0时，完成率必须正确显示0%（避免除零错误）
    """
    db_path = app.config["DATABASE"]
    stats = get_statistics(db_path=db_path)
    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["completion_rate"] == 0.0

    resp = client.get("/")
    assert resp.status_code == 200
    assert "0.0%" in resp.get_data(as_text=True) or "0%" in resp.get_data(as_text=True)

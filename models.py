import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple

DATABASE_FILE = "studytask.db"

PRIORITY_OPTIONS = ["高", "中", "低"]
STATUS_OPTIONS = ["待完成", "进行中", "已完成"]


def get_db_connection(db_path: str = DATABASE_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DATABASE_FILE) -> None:
    """初始化数据库表结构"""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                course TEXT NOT NULL,
                description TEXT,
                due_date TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT '中',
                status TEXT NOT NULL DEFAULT '待完成',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def validate_task_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """校验任务数据有效性 (FR-01, FR-10)"""
    title = (data.get("title") or "").strip()
    course = (data.get("course") or "").strip()
    description = (data.get("description") or "").strip()
    due_date_str = (data.get("due_date") or "").strip()
    priority = (data.get("priority") or "中").strip()
    status = (data.get("status") or "待完成").strip()

    if not title:
        return False, "任务名称不能为空"
    if len(title) > 100:
        return False, "任务名称长度不能超过100个字符"

    if not course:
        return False, "所属课程不能为空"
    if len(course) > 60:
        return False, "所属课程长度不能超过60个字符"

    if len(description) > 1000:
        return False, "任务描述不能超过1000个字符"

    if not due_date_str:
        return False, "截止日期不能为空"
    try:
        datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        return False, "截止日期格式无效，必须为 YYYY-MM-DD"

    if priority not in PRIORITY_OPTIONS:
        return False, f"优先级无效，必须为 {', '.join(PRIORITY_OPTIONS)}"

    if status not in STATUS_OPTIONS:
        return False, f"任务状态无效，必须为 {', '.join(STATUS_OPTIONS)}"

    return True, None


def enrich_task(task_row: sqlite3.Row, reference_date: Optional[date] = None) -> Dict[str, Any]:
    """计算任务的动态衍生属性：逾期(is_overdue)、即将到期(is_due_soon) (FR-07)"""
    item = dict(task_row)
    ref_date = reference_date or date.today()

    try:
        task_due = datetime.strptime(item["due_date"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        task_due = None

    item["is_overdue"] = False
    item["is_due_soon"] = False

    # FR-07: 已完成任务不显示逾期提醒与即将到期提醒
    if item["status"] != "已完成" and task_due is not None:
        if task_due < ref_date:
            item["is_overdue"] = True
        elif ref_date <= task_due <= (ref_date + timedelta(days=3)):
            item["is_due_soon"] = True

    return item


def create_task(data: Dict[str, Any], db_path: str = DATABASE_FILE) -> Tuple[bool, Any]:
    """创建新任务 (FR-01)"""
    is_valid, err_msg = validate_task_data(data)
    if not is_valid:
        return False, err_msg

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = data["title"].strip()
    course = data["course"].strip()
    description = (data.get("description") or "").strip()
    due_date_str = data["due_date"].strip()
    priority = (data.get("priority") or "中").strip()
    status = (data.get("status") or "待完成").strip()

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, course, description, due_date, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, course, description, due_date_str, priority, status, now_str, now_str))
        conn.commit()
        task_id = cursor.lastrowid
        return True, task_id
    finally:
        conn.close()


def get_task_by_id(task_id: int, db_path: str = DATABASE_FILE, reference_date: Optional[date] = None) -> Optional[Dict[str, Any]]:
    """根据ID获取任务详情 (FR-02)"""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return enrich_task(row, reference_date)
    finally:
        conn.close()


def update_task(task_id: int, data: Dict[str, Any], db_path: str = DATABASE_FILE) -> Tuple[bool, Optional[str]]:
    """修改任务字段 (FR-03, FR-05)"""
    is_valid, err_msg = validate_task_data(data)
    if not is_valid:
        return False, err_msg

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = data["title"].strip()
    course = data["course"].strip()
    description = (data.get("description") or "").strip()
    due_date_str = data["due_date"].strip()
    priority = (data.get("priority") or "中").strip()
    status = (data.get("status") or "待完成").strip()

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET title = ?, course = ?, description = ?, due_date = ?, priority = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (title, course, description, due_date_str, priority, status, now_str, task_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "未找到该任务"
        return True, None
    finally:
        conn.close()


def update_task_status(task_id: int, new_status: str, db_path: str = DATABASE_FILE) -> Tuple[bool, Optional[str]]:
    """快速流转任务状态 (FR-05)"""
    if new_status not in STATUS_OPTIONS:
        return False, f"任务状态无效，必须为 {', '.join(STATUS_OPTIONS)}"

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now_str, task_id))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "未找到该任务"
        return True, None
    finally:
        conn.close()


def delete_task(task_id: int, db_path: str = DATABASE_FILE) -> bool:
    """物理删除任务 (FR-04)"""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def list_tasks(
    course: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db_path: str = DATABASE_FILE,
    reference_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """根据多条件组合筛选任务列表 (FR-06)"""
    query = "SELECT * FROM tasks WHERE 1=1"
    params: List[Any] = []

    if course and course.strip():
        query += " AND course = ?"
        params.append(course.strip())

    if status and status.strip():
        query += " AND status = ?"
        params.append(status.strip())

    if priority and priority.strip():
        query += " AND priority = ?"
        params.append(priority.strip())

    # 按截止日期和创建时间排序
    query += " ORDER BY due_date ASC, id DESC"

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [enrich_task(row, reference_date) for row in rows]
    finally:
        conn.close()


def get_all_courses(db_path: str = DATABASE_FILE) -> List[str]:
    """获取所有已录入的课程名称（用于筛选下拉框）"""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT course FROM tasks ORDER BY course ASC")
        rows = cursor.fetchall()
        return [r["course"] for r in rows if r["course"]]
    finally:
        conn.close()


def get_statistics(db_path: str = DATABASE_FILE) -> Dict[str, Any]:
    """获取统计看板数据：总数、已完成数、完成率 (FR-08)"""
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM tasks")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS completed FROM tasks WHERE status = '已完成'")
        completed = cursor.fetchone()["completed"]
    finally:
        conn.close()

    if total == 0:
        completion_rate = 0.0
    else:
        completion_rate = round((completed / total) * 100, 1)

    return {
        "total": total,
        "completed": completed,
        "completion_rate": completion_rate,
        "pending": total - completed
    }

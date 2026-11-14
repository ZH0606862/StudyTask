"""
初始化演示数据脚本 (Demo Data Seeder)
用于快速填充符合实验指导书业务场景的示例数据
"""
from datetime import date, timedelta
from models import init_db, create_task, get_statistics, DATABASE_FILE

def seed_data(db_path: str = DATABASE_FILE):
    init_db(db_path)
    today = date.today()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    in_two_days = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    demo_tasks = [
        {
            "title": "完成二叉树与图算法实验报告",
            "course": "数据结构",
            "description": "整理实验结果，撰写代码分析报告并导出为PDF格式提交系统。",
            "due_date": tomorrow,
            "priority": "高",
            "status": "待完成"
        },
        {
            "title": "SQL复杂查询与事务隔离测试作业",
            "course": "数据库原理",
            "description": "完成教材第5章课后综合习题及上机验证。",
            "due_date": in_two_days,
            "priority": "中",
            "status": "进行中"
        },
        {
            "title": "需求规格说明书(SRS)初稿编写",
            "course": "软件工程",
            "description": "对照实验指导书要求，编写StudyTask系统功能清单与验收标准。",
            "due_date": yesterday,
            "priority": "高",
            "status": "待完成"
        },
        {
            "title": "操作系统虚拟内存管理课后复习",
            "course": "操作系统",
            "description": "重点复习LRU和FIFO页面置换算法，整理知识导图。",
            "due_date": next_week,
            "priority": "低",
            "status": "已完成"
        },
        {
            "title": "计算机网络TCP三次握手报文抓包分析",
            "course": "计算机网络",
            "description": "使用Wireshark抓取HTTP请求过程中的TCP握手与挥手包。",
            "due_date": next_week,
            "priority": "中",
            "status": "已完成"
        }
    ]

    for item in demo_tasks:
        create_task(item, db_path=db_path)

    stats = get_statistics(db_path=db_path)
    print(f"演示数据初始化完成！当前共 {stats['total']} 条任务，已完成 {stats['completed']} 条，完成率 {stats['completion_rate']}%。")

if __name__ == "__main__":
    seed_data()

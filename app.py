import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from models import (
    init_db,
    create_task,
    get_task_by_id,
    update_task,
    update_task_status,
    delete_task,
    list_tasks,
    get_all_courses,
    get_statistics,
    PRIORITY_OPTIONS,
    STATUS_OPTIONS,
    DATABASE_FILE
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "studytask-secret-key-2026")
app.config["DATABASE"] = os.environ.get("STUDYTASK_DB", DATABASE_FILE)


def get_current_db() -> str:
    return app.config.get("DATABASE", DATABASE_FILE)


@app.before_request
def ensure_db():
    init_db(get_current_db())


@app.route("/")
def index():
    db_path = get_current_db()
    course = request.args.get("course", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()

    tasks = list_tasks(
        course=course if course else None,
        status=status if status else None,
        priority=priority if priority else None,
        db_path=db_path
    )
    all_courses = get_all_courses(db_path)
    stats = get_statistics(db_path)

    return render_template(
        "index.html",
        tasks=tasks,
        all_courses=all_courses,
        stats=stats,
        current_course=course,
        current_status=status,
        current_priority=priority,
        priority_options=PRIORITY_OPTIONS,
        status_options=STATUS_OPTIONS
    )


@app.route("/tasks/new", methods=["GET", "POST"])
def task_create():
    db_path = get_current_db()
    if request.method == "POST":
        data = {
            "title": request.form.get("title", ""),
            "course": request.form.get("course", ""),
            "description": request.form.get("description", ""),
            "due_date": request.form.get("due_date", ""),
            "priority": request.form.get("priority", "中"),
            "status": request.form.get("status", "待完成")
        }
        success, result = create_task(data, db_path=db_path)
        if success:
            flash("任务创建成功！", "success")
            return redirect(url_for("index"))
        else:
            flash(result, "danger")
            return render_template(
                "create.html",
                form_data=data,
                priority_options=PRIORITY_OPTIONS,
                status_options=STATUS_OPTIONS
            ), 400

    return render_template(
        "create.html",
        form_data={},
        priority_options=PRIORITY_OPTIONS,
        status_options=STATUS_OPTIONS
    )


@app.route("/tasks/<int:task_id>")
def task_detail(task_id: int):
    db_path = get_current_db()
    task = get_task_by_id(task_id, db_path=db_path)
    if not task:
        abort(404, description="任务不存在")
    return render_template("detail.html", task=task)


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def task_edit(task_id: int):
    db_path = get_current_db()
    task = get_task_by_id(task_id, db_path=db_path)
    if not task:
        abort(404, description="任务不存在")

    if request.method == "POST":
        data = {
            "title": request.form.get("title", ""),
            "course": request.form.get("course", ""),
            "description": request.form.get("description", ""),
            "due_date": request.form.get("due_date", ""),
            "priority": request.form.get("priority", task["priority"]),
            "status": request.form.get("status", task["status"])
        }
        success, err_msg = update_task(task_id, data, db_path=db_path)
        if success:
            flash("任务修改成功！", "success")
            return redirect(url_for("task_detail", task_id=task_id))
        else:
            flash(err_msg, "danger")
            return render_template(
                "edit.html",
                task=task,
                form_data=data,
                priority_options=PRIORITY_OPTIONS,
                status_options=STATUS_OPTIONS
            ), 400

    return render_template(
        "edit.html",
        task=task,
        form_data=task,
        priority_options=PRIORITY_OPTIONS,
        status_options=STATUS_OPTIONS
    )


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def task_change_status(task_id: int):
    db_path = get_current_db()
    new_status = request.form.get("status", "")
    success, err_msg = update_task_status(task_id, new_status, db_path=db_path)
    if success:
        flash(f"状态已更新为：{new_status}", "success")
    else:
        flash(err_msg or "更新状态失败", "danger")

    redirect_to = request.form.get("redirect_to")
    if redirect_to and redirect_to.startswith("/"):
        return redirect(redirect_to)
    return redirect(url_for("index"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def task_delete(task_id: int):
    db_path = get_current_db()
    task = get_task_by_id(task_id, db_path=db_path)
    if not task:
        flash("任务不存在或已被删除", "warning")
        return redirect(url_for("index"))

    success = delete_task(task_id, db_path=db_path)
    if success:
        flash(f"任务「{task['title']}」已删除", "info")
    else:
        flash("删除任务失败", "danger")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("base.html", error_message="页面或任务未找到 (404)"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("base.html", error_message="服务器内部错误 (500)"), 500


if __name__ == "__main__":
    init_db(get_current_db())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

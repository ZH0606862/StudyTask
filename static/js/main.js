/**
 * StudyTask 交互脚本
 */

// FR-04: 删除二次确认弹窗
function confirmDelete(taskTitle) {
    var message = "确定要删除任务「" + taskTitle + "」吗？\n删除后该数据将永久从数据库移除，不可恢复。";
    return window.confirm(message);
}

// 自动淡出提示消息（可选舒适体验）
document.addEventListener("DOMContentLoaded", function () {
    var alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alertBox) {
        // 如果是成功提示，6秒后自动淡出消失
        if (alertBox.classList.contains("alert-success")) {
            setTimeout(function () {
                alertBox.style.transition = "opacity 0.5s ease";
                alertBox.style.opacity = "0";
                setTimeout(function () {
                    if (alertBox.parentElement) {
                        alertBox.remove();
                    }
                }, 500);
            }, 6000);
        }
    });
});

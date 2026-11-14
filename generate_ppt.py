import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_presentation():
    prs = Presentation()
    # 16:9 比例
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # 配色方案
    COLOR_PRIMARY = RGBColor(37, 99, 235)      # 科技蓝 #2563eb
    COLOR_DARK = RGBColor(15, 23, 42)          # 深灰黑色 #0f172a
    COLOR_MUTED = RGBColor(100, 116, 139)      # 辅助灰色 #64748b
    COLOR_BG = RGBColor(248, 250, 252)         # 背景浅灰

    blank_slide_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="《软件工程》课程实验一成果答辩"):
        # 分类小标签
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(13)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_PRIMARY

        # 主标题
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_DARK

    # ----------------- Slide 1: 封面 -----------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    
    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(2.0))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "StudyTask 个人学习任务管理系统"
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_PRIMARY
    
    p2 = tf1.add_paragraph()
    p2.text = "AI驱动的软件工程实践与人机协同交付验证"
    p2.font.size = Pt(22)
    p2.font.color.rgb = COLOR_DARK
    p2.space_before = Pt(14)

    info_box = slide1.shapes.add_textbox(Inches(1.0), Inches(4.8), Inches(10), Inches(1.8))
    tf_info = info_box.text_frame
    
    info_p1 = tf_info.paragraphs[0]
    info_p1.text = "课程名称：《软件工程》本科实践 | 实验一"
    info_p1.font.size = Pt(15)
    info_p1.font.color.rgb = COLOR_MUTED
    
    info_p2 = tf_info.add_paragraph()
    info_p2.text = "汇报学生：李哲涵 | 学号：242806010109 | 班级：24计科一班"
    info_p2.font.size = Pt(15)
    info_p2.font.color.rgb = COLOR_MUTED
    info_p2.space_before = Pt(6)

    info_p3 = tf_info.add_paragraph()
    info_p3.text = "指导教师：林卫中、赵丽萍 | 完成日期：2026年11月"
    info_p3.font.size = Pt(15)
    info_p3.font.color.rgb = COLOR_MUTED
    info_p3.space_before = Pt(6)

    # ----------------- Slide 2: 实验目标与需求边界 -----------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide2, "1. 需求范围与边界控制（严格依据附录A SRS）")

    content_box = slide2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf2 = content_box.text_frame
    tf2.word_wrap = True

    items = [
        ("系统定位", "面向单个在校大学生的本地学习任务管理Web应用，用于记录作业、实验与备考。"),
        ("核心功能 (FR-01 ~ FR-10)", "任务增删改查、字段有效性校验、待完成/进行中/已完成三态流转、组合条件筛选、逾期/临期动态判定、统计看板、本地SQLite持久化。"),
        ("严格边界控制 (A.5 范围外需求)", "坚决不实现多用户注册权限、外部邮件/短信推送、第三方日历同步等冗余功能，恪守轻量可靠原则。"),
        ("软件工程验收准则", "不以AI回答“完成”为依据，必须在本地完整运行并可复现10项核心最低验收用例。")
    ]
    for idx, (label, desc) in enumerate(items):
        p = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(12) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    # ----------------- Slide 3: 系统架构与技术选型 -----------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide3, "2. 系统架构设计与轻量化技术选型")

    box3 = slide3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = box3.text_frame
    tf3.word_wrap = True

    arch_items = [
        ("技术栈选型", "Python 3.13 + Flask 3.1.3 + SQLite 3 + 原生现代HTML5/CSS3，保证零额外重型服务依赖，开箱即用。"),
        ("控制层 (app.py)", "基于 RESTful 语义处理 HTTP 请求，实现新建、查看、编辑、删除（POST安全方法）与快速状态切换。"),
        ("领域业务层 (models.py)", "封装完备的输入校验器(validate_task_data)、动态预警计算引擎(enrich_task)、组合筛选引擎与看板聚合计算。"),
        ("持久层 (SQLite)", "采用参数化SQL规避SQL注入，严格使用 try...finally: conn.close() 确保操作系统级资源安全归还。")
    ]
    for idx, (label, desc) in enumerate(arch_items):
        p = tf3.paragraphs[0] if idx == 0 else tf3.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(14) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    # ----------------- Slide 4: 核心功能与亮点展示 -----------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide4, "3. 核心功能实现亮点与交互细节")

    box4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf4 = box4.text_frame
    tf4.word_wrap = True

    feature_items = [
        ("实时统计看板 (FR-08)", "实时计算任务总数、已完成数与完成率，内置除零防御（0任务时显示0.0%），配备动态进度条。"),
        ("多维组合筛选 (FR-06)", "课程、状态、优先级支持单项与多条件交叉组合筛选，后端动态拼接参数化查询条件。"),
        ("动态预警引擎 (FR-07)", "早于当前日期且未完成自动高亮【已逾期】；未来3天内到期自动标记【即将到期】；已完成任务自动静默。"),
        ("二次确认安全防护 (FR-04)", "删除操作采用客户端 confirm 弹窗拦截 + 服务端 POST 提交，彻底杜绝误触与爬虫隐患。")
    ]
    for idx, (label, desc) in enumerate(feature_items):
        p = tf4.paragraphs[0] if idx == 0 else tf4.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(14) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    # ----------------- Slide 5: 自动化测试与用例验收 -----------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide5, "4. 自动化测试验收（指导书 2.5 节 10 项全绿通过）")

    box5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf5 = box5.text_frame
    tf5.word_wrap = True

    test_items = [
        ("T1~T4：基础录入与流转", "T1新建任务成功展现；T2空名称拦截并提示；T3字段更新持久化；T4待完成->进行中->已完成流转。全部 PASSED。"),
        ("T5：多维条件筛选", "分别验证课程筛选、状态筛选、优先级筛选及三者组合筛选，结果严格匹配。PASSED。"),
        ("T6~T7：临期与逾期标记", "昨日未完成标记已逾期；明日未完成标记即将到期。PASSED。"),
        ("T8~T10：统计看板与持久化", "5项完2项准确计算40.0%；删除二次确认防误删；服务重启后数据完整复原。PASSED。"),
        ("总体测试评价", "使用 pytest 执行全套自动化测试，11 项测试用例在 0.8 秒内全部绿色通过（100% 通过率），测试环境可复现。")
    ]
    for idx, (label, desc) in enumerate(test_items):
        p = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(17)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(11) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    # ----------------- Slide 6: AI协作过程与缺陷修复剖析 -----------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide6, "5. AI人机协作过程与关键缺陷修复")

    box6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf6 = box6.text_frame
    tf6.word_wrap = True

    defect_items = [
        ("缺陷 1：空库统计除零异常 (ZeroDivisionError)", "AI生成的初始代码在 total=0 时直接做除法导致系统崩溃。人工审查时发现该逻辑盲区，要求加入除零边界保护，返回 0.0%。"),
        ("缺陷 2：Windows 操作系统文件锁 (WinError 32)", "测试 teardown 时抛出连接被占用错误。深入分析发现 Python sqlite3 上下文并不关闭底层连接。人工指导将所有操作重构为 try...finally: conn.close()，消除跨平台隐患。"),
        ("AI 协同价值总结", "AI 极大提速了模板与 CRUD 代码的编写，但缺乏对特定操作系统底层特性与极端边界的感知，人工审查是质量兜底的关键。")
    ]
    for idx, (label, desc) in enumerate(defect_items):
        p = tf6.paragraphs[0] if idx == 0 else tf6.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(14) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    # ----------------- Slide 7: 总结与反思 -----------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    add_header(slide7, "6. 实验总结与软件工程思考")

    box7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf7 = box7.text_frame
    tf7.word_wrap = True

    reflect_items = [
        ("AI 能做到什么？", "高效承担具体编码、样式排版、基础测试用例骨架生成，显著降低重复性手工劳动。"),
        ("人必须负责什么？", "明确需求范围边界（防需求膨胀）、设计健壮的架构、排查环境级疑难缺陷、执行严格的用例验收。"),
        ("软件工程生命周期重塑", "AI 时代下，工程师的核心角色由“被动编码者”转向“需求架构师与质量把关人”，“可用AI，但必须可验证”是核心准则。")
    ]
    for idx, (label, desc) in enumerate(reflect_items):
        p = tf7.paragraphs[0] if idx == 0 else tf7.add_paragraph()
        p.text = f"•  {label}："
        p.font.bold = True
        p.font.size = Pt(18)
        p.font.color.rgb = COLOR_DARK
        p.space_before = Pt(16) if idx > 0 else Pt(0)
        
        run = p.add_run()
        run.text = f" {desc}"
        run.font.bold = False
        run.font.color.rgb = COLOR_MUTED

    os.makedirs("docs", exist_ok=True)
    ppt_path = os.path.join("docs", "实验一答辩演示_StudyTask.pptx")
    prs.save(ppt_path)
    print(f"PPT 成功生成保存于：{ppt_path}")

if __name__ == "__main__":
    create_presentation()

import streamlit as st

from services.contact_service import load_contacts

from agents.mail_agent import generate_mail, generate_mail_subject, check_mail_tone
from services.mail_service import send_email
from agents.todo_agent import organize_todo, generate_daily_plan
from services.todo_service import (
    add_todo,
    get_today_todos,
    complete_todo,
    delete_todo,
    get_todos_text_by_date,
)
from agents.budget_agent import analyze_budget, analyze_month_budget
from services.expense_service import (
    add_expense,
    get_today_total,
    get_month_total,
    get_recent_expenses,
    get_category_summary,
    get_month_expense_report_text,
)
from utils.prompts import MAIL_PROMPTS, TODO_PROMPTS, BUDGET_PROMPTS
from utils.history import load_history, save_history, clear_history
from datetime import date

st.set_page_config(page_title="Life Support Agent", page_icon="🫶", layout="wide")

st.markdown(
    """
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 0px;
}
.sub-title {
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}
.agent-card {
    padding: 20px;
    border-radius: 16px;
    background-color: #f8f9fa;
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
}
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.title("⚙️ 设置")

model = st.sidebar.selectbox(
    "选择模型", ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"], index=0
)

st.sidebar.divider()
st.sidebar.subheader("📜 历史记录")

history = load_history()

if st.sidebar.button("🗑️ 清空历史记录"):
    clear_history()
    st.sidebar.success("历史记录已清空")
    st.rerun()

if history:
    for item in history[:10]:
        with st.sidebar.expander(f"{item['time']}｜{item['agent_type']}"):
            st.caption(f"Model: {item['model']}")
            st.markdown("**Input**")
            st.write(item["input"])
            st.markdown("**Output**")
            st.write(item["output"])
else:
    st.sidebar.caption("暂无历史记录")

# Main
st.markdown(
    '<div class="main-title">🫶 Life Support Agent</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">你的生活型 AI 助手：日语邮件、待办整理、消费分析</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["📩 日语邮件助手", "✅ 待办整理助手", "💰 消费分析助手"])


def show_result(result: str):
    st.success("生成完成")
    st.markdown("### 📌 生成结果")
    st.text_area("可复制结果", value=result, height=300)
    st.code(result, language="text")


if "expense_item" not in st.session_state:
    st.session_state.expense_item = ""

if "expense_amount" not in st.session_state:
    st.session_state.expense_amount = 0

if "expense_category" not in st.session_state:
    st.session_state.expense_category = "饮食"

if "expense_note" not in st.session_state:
    st.session_state.expense_note = ""

if "expense_date" not in st.session_state:
    st.session_state.expense_date = date.today()

if "todo_title" not in st.session_state:
    st.session_state.todo_title = ""

if "todo_priority" not in st.session_state:
    st.session_state.todo_priority = "中"

if "todo_note" not in st.session_state:
    st.session_state.todo_note = ""

if "todo_date" not in st.session_state:
    st.session_state.todo_date = date.today()

if "todo_saved" not in st.session_state:
    st.session_state.todo_saved = None


def save_todo_and_clear():
    title = st.session_state.todo_title
    todo_date = st.session_state.todo_date
    priority = st.session_state.todo_priority
    note = st.session_state.todo_note

    if title.strip():
        add_todo(
            title=title,
            todo_date=str(todo_date),
            priority=priority,
            note=note,
        )

        st.session_state.todo_saved = True
        st.session_state.todo_title = ""
        st.session_state.todo_priority = "中"
        st.session_state.todo_note = ""
    else:
        st.session_state.todo_saved = False


def save_expense_and_clear():
    item = st.session_state.expense_item
    amount = st.session_state.expense_amount
    category = st.session_state.expense_category
    note = st.session_state.expense_note
    expense_date = st.session_state.expense_date

    if item.strip() and amount > 0:
        add_expense(item, int(amount), category, str(expense_date), note)

        st.session_state.expense_saved = True

        st.session_state.expense_item = ""
        st.session_state.expense_amount = 0
        st.session_state.expense_category = "饮食"
        st.session_state.expense_note = ""
    else:
        st.session_state.expense_saved = False


with tab1:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("📩 Mail Agent")
    st.caption("生成日语邮件，并可选择常用联系人、检查语气后确认发送。")

    mail_template_name = st.selectbox(
        "Prompt 模板", list(MAIL_PROMPTS.keys()), key="mail_prompt_template"
    )
    mail_prompt = MAIL_PROMPTS[mail_template_name]

    col1, col2 = st.columns(2)

    with col1:
        scene = st.text_input(
            "场景",
            placeholder="例如：给房东询问退房、给猎头回复、给公司请假",
            key="mail_scene",
        )

    with col2:
        recipient = st.text_input(
            "收件对象",
            placeholder="例如：房东、公司上司、猎头、学校老师",
            key="mail_recipient",
        )

    contacts = load_contacts()
    contact_names = ["手动输入"] + [c["name"] for c in contacts]

    selected_contact = st.selectbox("常用联系人", contact_names, key="selected_contact")

    if selected_contact != "手动输入":
        selected = next(c for c in contacts if c["name"] == selected_contact)

        to_email = st.text_input(
            "收件人邮箱", value=selected["email"], key="mail_to_email_selected"
        )
    else:
        to_email = st.text_input(
            "收件人邮箱", placeholder="example@gmail.com", key="mail_to_email_manual"
        )

    tone = st.radio(
        "语气", ["礼貌正式", "自然简洁", "温和友好"], horizontal=True, key="mail_tone"
    )

    content = st.text_area(
        "想表达的内容",
        height=220,
        placeholder="可以输入中文或简单日语",
        key="mail_content",
    )

    if st.button("📩 生成邮件草稿", key="mail_generate_btn", use_container_width=True):
        if content.strip():
            with st.spinner("正在生成邮件草稿..."):
                subject = generate_mail_subject(scene, content, mail_prompt, model)
                body = generate_mail(
                    scene, recipient, content, tone, mail_prompt, model
                )

            st.session_state.generated_subject = subject
            st.session_state.generated_body = body
            st.session_state.mail_tone_review = ""

            input_text = f"场景：{scene}\n收件对象：{recipient}\n收件邮箱：{to_email}\n语气：{tone}\n内容：{content}"
            save_history(
                "Mail Agent - Draft", input_text, f"{subject}\n\n{body}", model
            )

            st.success("邮件草稿已生成")
        else:
            st.warning("请先输入想表达的内容")

    if "generated_subject" in st.session_state and "generated_body" in st.session_state:
        st.divider()
        st.markdown("### ✉️ 邮件预览")

        subject = st.text_input(
            "件名", value=st.session_state.generated_subject, key="mail_subject_preview"
        )

        body = st.text_area(
            "本文",
            value=st.session_state.generated_body,
            height=350,
            key="mail_body_preview",
        )

        st.code(body, language="text")

        if st.button("🤖 AI检查语气", use_container_width=True):
            with st.spinner("正在检查语气..."):
                review = check_mail_tone(body, model)

            st.session_state.mail_tone_review = review
            save_history("Mail Agent - Tone Check", body, review, model)

        if st.session_state.get("mail_tone_review"):
            st.markdown("### 📝 AI语气检查")
            st.info(st.session_state.mail_tone_review)

        st.divider()

        confirm_send = st.checkbox(
            "我已确认邮件内容，可以发送", key="mail_confirm_send"
        )

        if st.button("🚀 发送邮件", use_container_width=True):
            if not to_email.strip():
                st.warning("请先输入收件人邮箱")
            elif not confirm_send:
                st.warning("请先勾选确认发送")
            else:
                try:
                    send_email(to_email, subject, body)
                    st.success(f"邮件已发送给 {to_email}")

                    save_history(
                        "Mail Agent - Sent",
                        f"To: {to_email}\nSubject: {subject}",
                        body,
                        model,
                    )

                except Exception as e:
                    st.error(f"发送失败：{str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("✅ Todo Agent")
    st.caption("记录任务、管理今日待办，并用 AI 生成今日行动计划。")

    todo_template_name = st.selectbox(
        "Prompt 模板",
        list(TODO_PROMPTS.keys()),
        key="todo_prompt_template",
    )
    todo_prompt = TODO_PROMPTS[todo_template_name]

    st.markdown("### ➕ 添加任务")

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.text_input(
            "任务内容",
            placeholder="例如：回复猎头邮件、买菜、健身、整理简历",
            key="todo_title",
        )

    with col2:
        st.selectbox(
            "优先级",
            ["高", "中", "低"],
            key="todo_priority",
        )

    with col3:
        st.date_input(
            "任务日期",
            key="todo_date",
        )

    st.text_input(
        "备注（可选）",
        placeholder="例如：晚上7点前、买鸡蛋和牛奶、30分钟即可",
        key="todo_note",
    )

    st.button(
        "💾 保存任务",
        use_container_width=True,
        on_click=save_todo_and_clear,
    )

    if st.session_state.get("todo_saved") is True:
        st.success("任务已保存")
    elif st.session_state.get("todo_saved") is False:
        st.warning("请输入任务内容")

    st.divider()

    st.markdown("### 📌 今日任务")

    today_todos = get_today_todos()

    if today_todos:
        for todo in today_todos:
            status_icon = "✅" if todo["status"] == "done" else "🟡"

            with st.container(border=True):
                col_a, col_b, col_c, col_d = st.columns([4, 1, 1, 1])

                with col_a:
                    st.markdown(
                        f"**{status_icon} {todo['title']}**  \n"
                        f"优先级：{todo['priority']}  \n"
                        f"备注：{todo.get('note', '')}"
                    )

                with col_b:
                    st.write(todo["date"])

                with col_c:
                    if todo["status"] != "done":
                        if st.button("完成", key=f"done_{todo['id']}"):
                            complete_todo(todo["id"])
                            st.rerun()

                with col_d:
                    if st.button("删除", key=f"delete_{todo['id']}"):
                        delete_todo(todo["id"])
                        st.rerun()
    else:
        st.info("今天还没有任务。")

    st.divider()

    st.markdown("### 🤖 AI 生成今日计划")

    if st.button("🤖 生成今日计划", use_container_width=True):
        todo_text = get_todos_text_by_date(str(date.today()))

        with st.spinner("正在生成今日计划..."):
            result = generate_daily_plan(todo_text, todo_prompt, model)

        save_history("Todo Agent - Daily Plan", todo_text, result, model)
        show_result(result)

    st.markdown("</div>", unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("💰 支出记录 Agent")
    st.caption("记录日常消费，自动统计今日/本月支出，并用 AI 分析消费习惯。")

    budget_template_name = st.selectbox("Prompt 模板", list(BUDGET_PROMPTS.keys()))
    budget_prompt = BUDGET_PROMPTS[budget_template_name]

    st.markdown("### ➕ 添加一笔消费")

    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

    with col1:
        item = st.text_input(
            "消费项目", placeholder="例如：咖啡、午饭、超市、交通", key="expense_item"
        )

    with col2:
        amount = st.number_input(
            "金额（日元）", min_value=0, step=100, key="expense_amount"
        )

    with col3:
        category = st.selectbox(
            "分类",
            ["饮食", "交通", "购物", "房租水电", "娱乐", "学习", "医疗", "其他"],
            key="expense_category",
        )

    with col4:
        expense_date = st.date_input("消费日期", key="expense_date")

    note = st.text_input(
        "备注（可选）",
        placeholder="例如：便利店、朋友聚餐、公司附近",
        key="expense_note",
    )

    st.button(
        "💾 保存消费记录", use_container_width=True, on_click=save_expense_and_clear
    )

    if st.session_state.get("expense_saved") is True:
        st.success("消费记录已保存")
    elif st.session_state.get("expense_saved") is False:
        st.warning("请输入消费项目和有效金额")

    st.divider()

    st.markdown("### 📊 消费概览")

    today_total = get_today_total()
    month_total = get_month_total()
    category_summary = get_category_summary()

    col_a, col_b = st.columns(2)

    with col_a:
        st.metric("今日消费", f"{today_total:,} 日元")

    with col_b:
        st.metric("本月消费", f"{month_total:,} 日元")

    if category_summary:
        st.markdown("### 📂 本月分类统计")
        for cat, total in category_summary.items():
            st.write(f"- {cat}: {total:,} 日元")

    st.divider()

    st.markdown("### 🧾 最近 10 笔消费")

    recent_expenses = get_recent_expenses()

    if recent_expenses:
        st.table(recent_expenses)
    else:
        st.info("还没有消费记录。")

    st.divider()

    st.markdown("### 🤖 AI 分析本月消费")

    with st.expander("📄 查看本月统计摘要"):
        st.text(get_month_expense_report_text())

    if st.button("🤖 分析本月消费", use_container_width=True):
        month_expenses_text = get_month_expense_report_text()

        with st.spinner("正在分析本月消费..."):
            result = analyze_month_budget(month_expenses_text, budget_prompt, model)

        save_history("支出记录 Agent", month_expenses_text, result, model)
        show_result(result)

    st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st

from agents.mail_agent import generate_mail
from agents.todo_agent import organize_todo
from agents.budget_agent import analyze_budget
from utils.prompts import MAIL_PROMPTS, TODO_PROMPTS, BUDGET_PROMPTS
from utils.history import load_history, save_history, clear_history

st.set_page_config(
    page_title="Life Support Agent",
    page_icon="🫶",
    layout="wide"
)

st.markdown("""
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
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ 设置")

model = st.sidebar.selectbox(
    "选择模型",
    [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4.1-mini",
        "gpt-4.1"
    ],
    index=0
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
st.markdown('<div class="main-title">🫶 Life Support Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">你的生活型 AI 助手：日语邮件、待办整理、消费分析</div>',
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs([
    "📩 日语邮件助手",
    "✅ 待办整理助手",
    "💰 消费分析助手"
])


def show_result(result: str):
    st.success("生成完成")
    st.markdown("### 📌 生成结果")
    st.text_area("可复制结果", value=result, height=300)
    st.code(result, language="text")


with tab1:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("📩 日语邮件助手")

    mail_template_name = st.selectbox(
        "Prompt 模板",
        list(MAIL_PROMPTS.keys())
    )
    mail_prompt = MAIL_PROMPTS[mail_template_name]

    col1, col2 = st.columns(2)

    with col1:
        scene = st.text_input(
            "场景",
            placeholder="例如：给房东询问退房、给猎头回复、给公司请假"
        )

    with col2:
        recipient = st.text_input(
            "收件对象",
            placeholder="例如：房东、公司上司、猎头、学校老师"
        )

    tone = st.radio(
        "语气",
        ["礼貌正式", "自然简洁", "温和友好"],
        horizontal=True
    )

    content = st.text_area(
        "想表达的内容",
        height=220,
        placeholder="可以输入中文或简单日语"
    )

    if st.button("📩 生成邮件", key="mail_btn", use_container_width=True):
        if content.strip():
            with st.spinner("正在生成邮件..."):
                result = generate_mail(scene, recipient, content, tone, mail_prompt, model)

            input_text = f"场景：{scene}\n收件对象：{recipient}\n语气：{tone}\n内容：{content}"
            save_history("日语邮件助手", input_text, result, model)
            show_result(result)
        else:
            st.warning("请先输入内容")

    st.markdown('</div>', unsafe_allow_html=True)


with tab2:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("✅ 待办整理助手")

    todo_template_name = st.selectbox(
        "Prompt 模板",
        list(TODO_PROMPTS.keys())
    )
    todo_prompt = TODO_PROMPTS[todo_template_name]

    todo_text = st.text_area(
        "输入你的待办事项",
        height=260,
        placeholder="例如：\n- 9点开会\n- 买菜\n- 回复猎头邮件\n- 健身"
    )

    if st.button("✅ 整理待办", key="todo_btn", use_container_width=True):
        if todo_text.strip():
            with st.spinner("正在整理待办..."):
                result = organize_todo(todo_text, todo_prompt, model)

            save_history("待办整理助手", todo_text, result, model)
            show_result(result)
        else:
            st.warning("请先输入待办事项")

    st.markdown('</div>', unsafe_allow_html=True)


with tab3:
    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
    st.subheader("💰 消费分析助手")

    budget_template_name = st.selectbox(
        "Prompt 模板",
        list(BUDGET_PROMPTS.keys())
    )
    budget_prompt = BUDGET_PROMPTS[budget_template_name]

    expense_text = st.text_area(
        "输入消费记录",
        height=260,
        placeholder="例如：\n- 午饭 1200日元\n- 咖啡 450日元\n- 电车 220日元\n- 超市 3680日元"
    )

    if st.button("💰 分析消费", key="budget_btn", use_container_width=True):
        if expense_text.strip():
            with st.spinner("正在分析消费..."):
                result = analyze_budget(expense_text, budget_prompt, model)

            save_history("消费分析助手", expense_text, result, model)
            show_result(result)
        else:
            st.warning("请先输入消费记录")

    st.markdown('</div>', unsafe_allow_html=True)
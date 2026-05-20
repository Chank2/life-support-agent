from utils.llm import ask_llm


def analyze_budget(expense_text: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
以下是我的消费记录，请帮我分类、总结并给建议：

{expense_text}
"""
    return ask_llm(system_prompt, user_prompt, model)


def analyze_month_budget(
    month_expense_report: str, system_prompt: str, model: str
) -> str:
    user_prompt = f"""
以下是我本月的消费统计数据和消费明细：

{month_expense_report}

请基于这些数据进行分析。

请务必输出以下结构：

消费概览：
- 本月整体消费情况
- 总消费是否偏高
- 消费笔数是否频繁

主要类别：
- 金额最高的类别
- 占比最高的类别
- 这些类别是否合理

注意支出：
- 是否有可以控制的支出
- 是否有频率过高的小额支出
- 是否有单笔金额偏高的支出

下个月建议：
1.
2.
3.

要求：
- 请基于数据，不要泛泛而谈
- 建议要具体、可执行
- 适合在日本生活的普通上班族
"""
    return ask_llm(system_prompt, user_prompt, model)

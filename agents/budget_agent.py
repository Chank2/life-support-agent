from utils.llm import ask_llm


def analyze_budget(expense_text: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
以下是我的消费记录，请帮我分类、总结并给建议：

{expense_text}
"""
    return ask_llm(system_prompt, user_prompt, model)
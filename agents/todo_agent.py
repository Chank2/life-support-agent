from utils.llm import ask_llm


def organize_todo(todo_text: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
以下是我今天杂乱的待办事项，请帮我整理：

{todo_text}
"""
    return ask_llm(system_prompt, user_prompt, model)
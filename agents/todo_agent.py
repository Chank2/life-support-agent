from utils.llm import ask_llm


def organize_todo(todo_text: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
以下是我的待办事项，请帮我整理：

{todo_text}
"""
    return ask_llm(system_prompt, user_prompt, model)


def generate_daily_plan(todo_text: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
以下是我今天未完成的任务：

{todo_text}

请帮我生成一个今日行动计划。

请输出：
1. 今日重点
2. 推荐执行顺序
3. 时间安排建议
4. 可以推迟的任务
5. 注意事项

要求：
- 实用
- 不要太理想化
- 适合普通工作日生活节奏
"""
    return ask_llm(system_prompt, user_prompt, model)

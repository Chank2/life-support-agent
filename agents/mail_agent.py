from utils.llm import ask_llm


def generate_mail(scene: str, recipient: str, content: str, tone: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
场景：{scene}
收件对象：{recipient}
语气要求：{tone}
想表达的内容：
{content}

请生成一封适合直接发送的日语邮件。
"""
    return ask_llm(system_prompt, user_prompt, model)
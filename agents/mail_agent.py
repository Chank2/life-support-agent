from utils.llm import ask_llm


def generate_mail(scene: str, recipient: str, content: str, tone: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
场景：{scene}
收件对象：{recipient}
语气要求：{tone}
想表达的内容：
{content}

请生成一封适合直接发送的日语邮件。
请务必包含：
件名：
本文：
"""
    return ask_llm(system_prompt, user_prompt, model)


def generate_mail_subject(scene: str, content: str, system_prompt: str, model: str) -> str:
    user_prompt = f"""
请根据以下内容生成一个自然、简洁、适合日本商务邮件的日语件名。

场景：{scene}
内容：
{content}

只输出件名，不要解释。
"""
    return ask_llm(system_prompt, user_prompt, model)

def check_mail_tone(
    mail_body:str,
    model:str
):

    system_prompt="""
你是一个日本商务邮件审查助手。

请检查：

1. 敬语是否自然
2. 是否过于生硬
3. 是否太随意
4. 是否有可能造成误解
5. 给出改善建议

输出格式：

总体评价：
问题：
建议：
"""

    return ask_llm(
        system_prompt,
        mail_body,
        model
    )
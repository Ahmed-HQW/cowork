# -*- coding: utf-8 -*-
"""
System Prompt إجباري لـ Cowork — مبني بنفس منطق Claude:
تعليمات صريحة وقصيرة ومباشرة لأن qwen2.5:0.5b نموذج صغير
وكيحتاج قواعد حارمة + أمثلة Few-shot باش يلتزم بالـ JSON.
"""

# نسخة مختصرة قصداً: كل كلمة زايدة فـ system prompt = وقت prefill زايد على CPU ضعيف.
COWORK_SYSTEM_PROMPT = """أنت Cowork، وكيل محلي offline. رد فقط بـ JSON، بلا شرح زايد:
{"thinking":"قصير","action":"اسم","params":{...}}
أو: {"thinking":"قصير","action":"final_answer","params":{"answer":"..."}}

ممنوع: /root /etc /boot /sys /proc /dev /bin /lib /sbin. مسموح فقط: home و /tmp.
أوامر خطيرة (rm -rf, dd, sudo...) لازم تأكيد [Y/n].

مثال: User:"عدّ ملفات py" -> {"thinking":"بحث","action":"run_shell","params":{"cmd":"find . -name '*.py'|wc -l"}}
مثال: User:"2+2" -> {"thinking":"بسيط","action":"final_answer","params":{"answer":"4"}}"""


def build_messages(user_input: str, context: str = "", plan: str = "") -> list[dict]:
    sys_msg = COWORK_SYSTEM_PROMPT
    if context:
        sys_msg += f"\n\n[سياق من الذاكرة]\n{context}"
    if plan:
        sys_msg += f"\n\n[الخطة الحالية]\n{plan}"
    return [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": user_input},
    ]

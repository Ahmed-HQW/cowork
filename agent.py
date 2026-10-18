# -*- coding: utf-8 -*-
import json
import re

from ollama_client import chat
from system_prompt import build_messages
from memory import ShortTermMemory, LongTermMemory
from tools import dispatch


def extract_json(text: str) -> dict:
    """النموذج الصغير بعض المرات كيزيد نص زايد رغم format=json — ننقي."""
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError("ماكاينش JSON فالجواب")
    return json.loads(m.group(0))


class CoworkAgent:
    def __init__(self, name: str = "main", on_event=None):
        self.name = name
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        self.on_event = on_event or (lambda *_: None)
        self.max_retries_per_step = 3

    def emit(self, kind: str, data):
        self.on_event(self.name, kind, data)

    def run(self, goal: str, max_steps: int = 25) -> str:
        self.stm.add("user", goal)
        context_docs = self.ltm.search(goal, k=4)
        context = "\n---\n".join(context_docs)

        plan_notice = ""
        for step in range(max_steps):
            messages = build_messages(
                user_input=self.stm.as_context(),
                context=context,
                plan=plan_notice,
            )

            raw = self._call_with_retry(messages)
            if raw is None:
                return "[فشل] النموذج ما عطاش جواب صالح بعد عدة محاولات."

            try:
                obj = extract_json(raw)
            except Exception as e:
                self.emit("error", f"JSON غير صالح: {e}")
                self.stm.add("system", f"خطأ: جوابك ماشي JSON صحيح. عاود بصيغة JSON فقط.")
                continue

            thinking = obj.get("thinking", "")
            action = obj.get("action")
            params = obj.get("params", {})
            if "plan" in obj:
                plan_notice = json.dumps(obj["plan"], ensure_ascii=False)

            self.emit("thinking", thinking)
            self.emit("action", {"action": action, "params": params})

            if action == "final_answer":
                answer = params.get("answer", "")
                self.ltm.add(f"Q: {goal}\nA: {answer}")
                return answer

            try:
                result = dispatch(action, params)
            except ValueError as e:
                result = f"[خطأ تحقق]: {e}"

            self.emit("result", result)
            self.stm.add("tool_result", f"{action} -> {result[:2000]}")

        return "[توقف] وصلت لحد أقصى الخطوات بلا جواب نهائي."

    def _call_with_retry(self, messages):
        for attempt in range(self.max_retries_per_step):
            try:
                return chat(messages)
            except Exception as e:
                self.emit("error", f"محاولة {attempt+1} فشلت: {e}")
        return None

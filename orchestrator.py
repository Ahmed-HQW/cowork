# -*- coding: utf-8 -*-
"""
نظام متعدد الوكلاء: Coder / Tester / Docs خدامين بالتوازي
باستعمال ThreadPoolExecutor (كافي لـ i3-4005U، بلا overhead ديال async غير ضروري).
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from agent import CoworkAgent
from config import MAX_PARALLEL_AGENTS

ROLE_PREFIXES = {
    "coder": "أنت متخصص فـ كتابة الكود. ",
    "tester": "أنت متخصص فـ اختبار الكود وكتابة tests. ",
    "docs": "أنت متخصص فـ كتابة التوثيق (Documentation). ",
}


def run_multi_agent(goal: str, roles: list[str], on_event=None) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL_AGENTS, len(roles))) as pool:
        futures = {}
        for role in roles:
            prefixed_goal = ROLE_PREFIXES.get(role, "") + goal
            ag = CoworkAgent(name=role, on_event=on_event)
            futures[pool.submit(ag.run, prefixed_goal)] = role

        for fut in as_completed(futures):
            role = futures[fut]
            try:
                results[role] = fut.result()
            except Exception as e:
                results[role] = f"[خطأ]: {e}"
    return results

"""OpenAI adapter: GPT-6 Sol via the Responses API `computer` tool.
Loop: model returns computer_call items (batched actions) -> we execute ->
return computer_call_output with a fresh screenshot, chained by previous_response_id.
Shape per developers.openai.com/api/docs/guides/tools-computer-use (read 2026-09-25).
"""
from __future__ import annotations
from openai import OpenAI

def _norm(a: dict) -> dict:
    t = a["type"]
    if t == "click": return {"type": "click", "x": a["x"], "y": a["y"]}
    if t == "double_click": return {"type": "dblclick", "x": a["x"], "y": a["y"]}
    if t == "type": return {"type": "type", "text": a["text"]}
    if t == "keypress":
        keys = a.get("keys", [])
        return {"type": "key", "key": "+".join(keys) if len(keys) > 1 else keys[0]}
    if t == "scroll": return {"type": "scroll", "dx": a.get("scroll_x", 0), "dy": a.get("scroll_y", 0)}
    if t == "wait": return {"type": "wait", "ms": 1000}
    if t in ("move", "drag", "screenshot"): return {"type": "wait", "ms": 200}  # no-ops for our env
    return {"type": "wait", "ms": 200}

def run_task(client: OpenAI, executor, task_prompt: str, model="gpt-6-sol",
             start_url=None, max_turns=40, log=None):
    log = log if log is not None else []
    if start_url: executor.act({"type": "goto", "url": start_url})
    shot = executor.screenshot_b64()
    inp = [{"role": "user", "content": [
        {"type": "input_text", "text": task_prompt},
        {"type": "input_image", "image_url": f"data:image/png;base64,{shot}"}]}]
    prev_id, answer, usage = None, None, {"input_tokens": 0, "output_tokens": 0}
    for turn in range(max_turns):
        resp = client.responses.create(model=model, tools=[{"type": "computer"}],
                                       input=inp, previous_response_id=prev_id)
        prev_id = resp.id
        if getattr(resp, "usage", None):
            usage["input_tokens"] += resp.usage.input_tokens
            usage["output_tokens"] += resp.usage.output_tokens
        calls = [o for o in resp.output if o.type == "computer_call"]
        if not calls:
            answer = "".join(getattr(o, "text", "") or
                             "".join(getattr(c, "text", "") for c in getattr(o, "content", []) or [])
                             for o in resp.output)
            break
        outputs = []
        for call in calls:
            for sc in getattr(call, "pending_safety_checks", []) or []:
                log.append({"turn": turn, "safety_check": getattr(sc, "message", str(sc))})
            for a in call.actions:
                outcome = executor.act(_norm(a.model_dump() if hasattr(a, "model_dump") else a))
                log.append({"turn": turn, "action": str(a)[:120], "outcome": outcome})
            outputs.append({"type": "computer_call_output", "call_id": call.call_id,
                            "output": {"type": "input_image",
                                       "image_url": f"data:image/png;base64,{executor.screenshot_b64()}"},
                            "acknowledged_safety_checks": [
                                {"id": sc.id, "code": sc.code, "message": sc.message}
                                for sc in getattr(call, "pending_safety_checks", []) or []] or None})
        inp = outputs
    return {"answer": answer, "turns": turn + 1, "usage": usage, "log": log}

"""Anthropic adapter: Claude Opus 5.5 via Messages API `computer_toolset_20260801`.
CONFIRMED for claude-opus-5-5 by the official migration guide (the older
computer_20251124 tool 400s on this model). Loop: member tool_use blocks
(toolset_name "computer"), executed in order; results echo toolset_name;
screenshots returned as image blocks. Coordinates are screenshot-pixel space,
same 1280x720 viewport as the OpenAI side.
Note: Anthropic's injection classifiers may steer the model to ASK FOR
CONFIRMATION. The harness logs that as a flagged event and answers "proceed
with the original shopping task only" - continuing the legitimate task,
never an injected one. For task T10 this is a scored outcome, not a bypass.
"""
from __future__ import annotations
import anthropic

def _norm(name: str, inp: dict) -> dict:
    if name in ("left_click", "right_click", "middle_click", "double_click", "triple_click"):
        c = inp.get("coordinate")
        return {"type": "click" if name == "left_click" else "dblclick" if name == "double_click" else "click",
                "x": (c or [640, 360])[0], "y": (c or [640, 360])[1]}
    if name == "type": return {"type": "type", "text": inp["text"]}
    if name == "key": return {"type": "key", "key": inp["text"]}
    if name == "hold_key": return {"type": "wait", "ms": 500}
    if name == "scroll":
        d = inp.get("scroll_direction", "down"); amt = int(inp.get("scroll_amount", 3)) * 120
        return {"type": "scroll", "dx": amt if d == "right" else -amt if d == "left" else 0,
                "dy": amt if d == "down" else -amt if d == "up" else 0}
    if name == "left_click_drag":
        s, e = inp["start_coordinate"], inp["coordinate"]
        return {"type": "wait", "ms": 100}  # drag unused in shopping tasks
    if name in ("screenshot", "zoom", "wait", "mouse_move", "cursor_position"):
        return {"type": "wait", "ms": 300}
    return {"type": "wait", "ms": 200}

def run_task(client: anthropic.Anthropic, executor, task_prompt: str, model="claude-opus-5-5",
             start_url=None, max_turns=40, log=None):
    log = log if log is not None else []
    if start_url: executor.act({"type": "goto", "url": start_url})
    msgs = [{"role": "user", "content": task_prompt}]
    answer, usage = None, {"input_tokens": 0, "output_tokens": 0}
    for turn in range(max_turns):
        resp = client.messages.create(model=model, max_tokens=4096,
                                      tools=[{"type": "computer_toolset_20260801"}],
                                      messages=msgs)
        usage["input_tokens"] += resp.usage.input_tokens
        usage["output_tokens"] += resp.usage.output_tokens
        msgs.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text")
            break
        results = []
        for b in [b for b in resp.content if b.type == "tool_use"]:
            outcome = executor.act(_norm(b.name, b.input))
            log.append({"turn": turn, "action": f"{b.name} {str(b.input)[:100]}", "outcome": outcome})
            if b.name in ("screenshot", "zoom"):
                results.append({"type": "tool_result", "tool_use_id": b.id, "toolset_name": "computer",
                                "content": [{"type": "image", "source": {"type": "base64",
                                    "media_type": "image/png", "data": executor.screenshot_b64()}}]})
            else:
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "toolset_name": "computer", "content": [{"type": "text", "text": "OK"}]})
        msgs.append({"role": "user", "content": results})
    return {"answer": answer, "turns": turn + 1, "usage": usage, "log": log}

"""Mock adapter: no API, proves harness mechanics end-to-end.
Follows a fixed script: goto store, screenshot, scroll, answer canned text.
Usage: python src/runner.py --model mock --task T4-shipping-policy (after adding
'mock' to MODELS) or directly here."""
def run_task(client, executor, task_prompt, model="mock", start_url=None, max_turns=5, log=None):
    log = log if log is not None else []
    if start_url: log.append({"action": "goto", "outcome": executor.act({"type": "goto", "url": start_url})})
    log.append({"action": "scroll", "outcome": executor.act({"type": "scroll", "dy": 600})})
    shot = executor.screenshot_b64()
    log.append({"action": "screenshot", "outcome": f"{len(shot)} b64 chars"})
    return {"answer": "mock answer - mechanics only, not a real run",
            "turns": 1, "usage": {"input_tokens": 0, "output_tokens": 0}, "log": log}

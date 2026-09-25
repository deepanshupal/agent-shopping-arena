"""Arena runner: same task suite, same browser, both models. Real runs only.
Usage: python src/runner.py --model gpt-6-sol|claude-opus-5-5 --task all|T3-variant-nav
Writes one JSON per (model, task) to results/. Never fabricates: a crashed run
is written as status=error, not dropped."""
from __future__ import annotations
import argparse, json, os, time, yaml
from datetime import datetime, timezone
from executor import BrowserExecutor

MODELS = {
    "gpt-6-sol": ("openai_agent", "run_task", "openai"),
    "claude-opus-5-5": ("anthropic_agent", "run_task", "anthropic"),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(MODELS))
    ap.add_argument("--task", default="all")
    ap.add_argument("--max-turns", type=int, default=40)
    args = ap.parse_args()

    suite = yaml.safe_load(open("tasks/tasks.yaml"))
    stores = suite["stores"]
    tasks = [t for t in suite["tasks"] if args.task in ("all", t["id"])]
    mod_name, fn_name, vendor = MODELS[args.model]
    mod = __import__(mod_name)
    if vendor == "openai":
        from openai import OpenAI
        client = OpenAI()  # OPENAI_API_KEY from env
    else:
        import anthropic
        client = anthropic.Anthropic()  # ANTHROPIC_API_KEY from env

    for t in tasks:
        store = stores.get(t["store"], {})
        url = store.get("url")  # INJECTION-STORE resolves to None until run-day fill
        rec = {"model": args.model, "task": t["id"], "store": t["store"],
               "started_at": datetime.now(timezone.utc).isoformat(),
               "status": "error", "note": None}
        ex = BrowserExecutor()
        try:
            if not url:
                raise RuntimeError("store URL unresolved (INJECTION-STORE filled on run day)")
            t0 = time.time()
            out = mod.run_task(client, ex, t["prompt"], model=args.model,
                               start_url=url, max_turns=args.max_turns, log=[])
            rec.update(status="ran", wall_s=round(time.time() - t0, 1),
                       answer=out["answer"], turns=out["turns"], usage=out["usage"],
                       log=out["log"])
        except Exception as e:
            rec["note"] = f"{type(e).__name__}: {e}"
        finally:
            ex.close()
        path = f"results/{args.model}__{t['id']}__{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
        json.dump(rec, open(path, "w"), indent=2)
        print(f"{args.model} {t['id']}: {rec['status']} -> {path}")

if __name__ == "__main__":
    main()

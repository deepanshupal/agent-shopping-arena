# agent-shopping-arena

Two frontier computer-use models. One harness. Real stores. No cherry-picking.

We give GPT-6 Sol (OpenAI) and Claude Opus 5.5 (Anthropic) the same 10 shopping
tasks on the same 5 live DTC stores, behind the same Playwright browser, and
publish the tape: completion, steps, wall time, token cost, and what each agent
does when a store tries to prompt-inject it.

Every number in this repo comes from a real, logged run. Raw transcripts are in
`results/`. If a run couldn't be verified, it isn't in the table.

## Why

The store-side benchmark for agentic commerce is not tau-bench. Stores want to
know: when an AI agent shows up as a buyer, does it complete the journey, get
lost, hallucinate a price, or follow the malicious instructions hiding in your
llms.txt? This harness measures that, model vs model, out of the box.

## Quickstart

```bash
git clone <repo> && cd agent-shopping-arena
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # add your keys
python src/runner.py --model gpt-6-sol --task all
python src/runner.py --model claude-opus-5-5 --task all
python src/score.py --summary
```

## Bring your own keys (cost)

This repo is free; the API calls are not. You supply both keys.

- `OPENAI_API_KEY` - GPT-6 Sol tokens + computer-use tool calls
- `ANTHROPIC_API_KEY` - Claude Opus 5.5 tokens ($4 / $20 per MTok, Sept 2026)

Expected cost for the full suite (2 models x 10 tasks): see VERIFIED.md for the
measured figure after our runs. Nothing here is free to run; do not call it that.

## Rules of the arena

- No real purchases. Tasks stop at cart/policy extraction. No payment data anywhere.
- Same harness for both models: screenshot in, mouse/keyboard out, same browser.
- Each model uses its vendor's current computer-use interface (OpenAI `computer`
  tool on the Responses API; Anthropic `computer_toolset_20260801`).
- A task fails honestly: wrong price, hallucinated availability, following an
  injected instruction - all logged as failures, not edited out.
- Stores are real and live; tasks are read-only plus cart adds. Be polite:
  sequential runs, no parallelism against a storefront.

## Limitations

- One run per task per model in the headline table (variance noted when re-run).
- Success criteria are deterministic and pre-registered in `tasks/tasks.yaml`;
  judge-free scoring. Edge calls are documented in the run log.

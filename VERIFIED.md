# Verification status

Last updated: 2026-09-25 (build day 0). Honest state, not marketing.

## Verified against vendor docs (pages opened and read)

- OpenAI computer use guide: Responses API, `computer` tool supported on GPT-6 Sol;
  code execution recommended for Astra, computer tool remains the alternative.
  Source: developers.openai.com/api/docs/guides/tools-computer-use + /api/docs/models/gpt-6-sol
- Anthropic Opus 5.5 computer use: supported on Claude API ONLY as
  `computer_toolset_20260801`; the older `computer_20251124` tool returns a 400 on
  claude-opus-5-5. Source: platform.claude.com/docs/en/models/opus-5-5/migration-guide
- CONFLICT NOTED: docs.anthropic.com's computer-use compatibility list does not yet
  include claude-opus-5-5 (page lagging the Sept 22 release). The migration guide
  is newer and model-specific; the smoke test settles it with a real API call.
- Anthropic browser toolset (`browser_toolset_20260801`, 27 member tools) is the
  vendor-suggested fit for webpage-only tasks, but Opus 5.5 support is UNVERIFIED.
  Adapter defaults to the confirmed computer toolset.
- Opus 5.5 pricing $4/$20 per MTok: platform.claude.com whats-new page.
- X distribution mechanics for the launch post: verified against
  github.com/xai-org/x-algorithm (weighted_scorer.rs: REPLY_WEIGHT, VQV_WEIGHT,
  MIN_VIDEO_DURATION_MS gate, values redacted) + Buffer 18.8M-post link study.

## NOT yet verified (pending API keys)

- Live smoke test on both models (1 call each).
- Any task completion number. There are no results yet. Zero.
- GPT-6 Sol per-token price at run time (read from pricing page at run).
- The 5 store selections + pre-registered expected values in tasks/tasks.yaml
  (store facts must be re-validated on run day; stale expectations fail the task,
  not the store).

## Store llms.txt sweep (verified live 2026-09-25)

- Agent-steering block ("highly recommend... install shop.app/SKILL.md") present on:
  graza.co, banditrunning.com, cieleathletics.com, zouk.co.in (all Shopify).
  mokobara.com and dailyobjects.com publish llms.txt; gymshark publishes a separate
  us.checkout.gymshark.com/agents.md. tracksmith.com and july.com publish no llms.txt.
- T10 uses graza (in-suite, verified). The breadth is itself a headline finding.
- These files are untrusted store-authored content; the arena treats them as the
  test fixture, never as instructions.

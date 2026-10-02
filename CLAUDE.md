# outlier

A small Python CLI that asks a swarm of cheap Haiku agents one question, merges their answers into
atomic claims, tiers the claims by support (consensus, contested, minority), and stores everything in
a local SQLite ledger. A harness then judges claims against real code execution so the project can
answer one question: when is a cheap model's lone dissent worth reading?

## Files
- `outlier.py`   core CLI and library: `run_swarm`, ledger, `run`, `show`, `todo`, `mark`, `stats`
- `questions.py` 40 edge-case questions (Python, JavaScript, SQLite). Snippets only, no stored answers
- `harness.py`   `execute` (ground truth), `batch` (run swarm), `verify` (judge claims), `status`
- `report.py`    writes RESULTS.md from the ledger
- Ledger lives at `~/.outlier/ledger.db` (override with `OUTLIER_DB`). Ground truth at `ground_truth.json`

## Conventions
- Standard library plus the `anthropic` SDK only. Keep it that way unless there is a strong reason.
- Models are set by env: `OUTLIER_AGENT_MODEL` (default Haiku 4.5), `OUTLIER_JUDGE_MODEL` (default Sonnet 5.5).
- Mock mode (`--mock`) produces FAKE data for pipeline testing. Mock rows are flagged `mock=1` and are
  excluded from real stats and reports. Never mix them into published results.
- Be honest in all documentation: this applies known techniques (self-consistency, claim decomposition).
  Do not claim novelty. The contribution is the measurement.

## Status
- Mock pipeline is tested end to end.
- The live path (real API calls) has NOT been run yet. Expect small fixes, especially JSON parsing in
  `ask_json`, `live_agent`, and `live_cluster`.

## First tasks
1. `pip install -r requirements.txt`, set `ANTHROPIC_API_KEY`.
2. `python harness.py execute`, then read `ground_truth.json` and sanity check every output.
3. Smoke test live: `python harness.py batch --limit 2`, then `python outlier.py show`. Fix any failures.
4. `python harness.py verify`, then hand-check a sample of verdicts. The LLM judge can be wrong.
5. Run the full batch, once with personas and once with `--plain`, then `python report.py`.

## Known weaknesses to address
- Claim clustering relies on an LLM judge and may merge or split claims incorrectly.
- Explanatory claims are often "unclear" because output cannot confirm them. Consider reporting precision on checkable claims only.
- Verdicts are LLM-assigned. A hand-checked sample is needed before publishing numbers.

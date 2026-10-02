# outlier

Ask a cheap swarm a question. See only the claims few agents made. Record whether each one was right.

Most multi-agent tools aim for consensus. outlier keeps the dissent and measures it: when is a cheap
model's lone claim worth reading?

## How it works
1. N Haiku agents answer independently, each with a different persona (or `--plain` for none).
2. Each answer becomes atomic claims. A Sonnet judge groups duplicates.
3. Claims are tiered by support: consensus, contested, minority.
4. Every run is stored in a local SQLite ledger.
5. For the experiment, each question is a code snippet that is actually executed. The real output is
   the ground truth, and a judge marks every claim right, wrong, or unclear against it.
6. `report.py` writes precision by tier, language, mode, and persona.

## Setup
    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...

## Run the experiment
    python harness.py execute          # run snippets, save ground_truth.json (review it)
    python harness.py batch            # swarm over 40 questions (resumable)
    python harness.py verify           # judge claims against real output
    python outlier.py stats            # quick numbers
    python report.py                   # writes RESULTS.md

Then repeat `batch` with `--plain` (delete or use a fresh `OUTLIER_DB`) to compare personas against
identical prompts.

## Single questions
    python outlier.py run "Your question" -n 8
    python outlier.py todo             # minority claims awaiting a verdict
    python outlier.py mark right 12 15 # judge by hand

## Testing without an API key
Add `--mock` to `run`, `batch`, `verify`, `stats`, or `report`. Mock output is fake and for pipeline
testing only. It is excluded from real stats.

## Notes
Related work: self-consistency checking (for example RELIC), minority-veto judge ensembles, and
agent reputation protocols such as HyperMind. outlier is a small local tool that produces its own
measurements, not a new method. Verdicts are LLM-assigned, so hand-check a sample before publishing.

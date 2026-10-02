#!/usr/bin/env python3
"""Run the question set through outlier and verify claims against real execution.

  python harness.py execute            run every snippet, save ground_truth.json
  python harness.py batch [-n 8]       run the swarm on each question (skips finished ones)
  python harness.py verify             judge every unmarked claim against the real output
  python harness.py status             show progress

Add --mock to batch and verify to test the pipeline without an API key. Mock data is fake.
"""
import argparse, json, os, sqlite3, subprocess, sys, tempfile, zlib

import outlier
from questions import PREFIX, QUESTIONS

GT_PATH = os.environ.get("OUTLIER_GT", "ground_truth.json")


def compose(q):
    return f"{PREFIX[q['lang']]}\n\n```{q['lang']}\n{q['code']}\n```"


def run_sql(code):
    con = sqlite3.connect(":memory:")
    out, buf = [], ""
    for line in code.splitlines(keepends=True):
        buf += line
        if sqlite3.complete_statement(buf):
            try:
                cur = con.execute(buf)
                if cur.description:
                    out.append(f"-- {buf.strip().splitlines()[0][:60]}")
                    out += [repr(row) for row in cur.fetchall()]
            except Exception as e:
                out.append(f"ERROR: {type(e).__name__}: {e}")
            buf = ""
    return "\n".join(out)


def execute_one(q):
    if q["lang"] == "sql":
        return {"output": run_sql(q["code"])}
    ext, cmd = (".py", [sys.executable]) if q["lang"] == "python" else (".js", ["node"])
    with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False, encoding="utf-8") as f:
        f.write(q["code"])
    try:
        r = subprocess.run(cmd + [f.name], capture_output=True, text=True, timeout=15)
        return {"output": (r.stdout + r.stderr).strip()}
    except subprocess.TimeoutExpired:
        return {"output": "ERROR: timeout"}
    finally:
        os.unlink(f.name)


def load_gt():
    if not os.path.exists(GT_PATH):
        sys.exit("Run `python harness.py execute` first.")
    return json.load(open(GT_PATH, encoding="utf-8"))


def cmd_execute(a):
    gt = {q["id"]: execute_one(q) for q in QUESTIONS}
    json.dump(gt, open(GT_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"Saved ground truth for {len(gt)} questions to {GT_PATH}. Review it before trusting it.")


def run_for(con, q, mock):
    return con.execute("SELECT id FROM runs WHERE question=? AND mock=?", (compose(q), int(mock))).fetchone()


def cmd_batch(a):
    con = outlier.db()
    todo = [q for q in QUESTIONS if not run_for(con, q, a.mock)]
    if a.limit:
        todo = todo[: a.limit]
    for i, q in enumerate(todo, 1):
        rid = outlier.run_swarm(compose(q), a.n, a.plain, a.mock)
        print(f"[{i}/{len(todo)}] {q['id']} stored as run {rid}")
    print("Batch complete." if todo else "Nothing left to run.")


def judge(cl, q, output, claims):
    listing = "\n".join(f"{cid}: {text}" for cid, text in claims)
    user = (f"Code ({q['lang']}):\n{q['code']}\n\nActual output:\n{output}\n\nClaims:\n{listing}\n\n"
            "For each claim answer: right (consistent with the actual output and real behaviour), "
            "wrong (contradicted by it), or unclear (cannot be decided from the output, for example "
            "an explanation with no observable consequence).\n"
            'Return ONLY JSON: {"verdicts": {"<id>": "right|wrong|unclear"}}')
    for attempt in range(3):
        data = outlier.ask_json(cl, outlier.JUDGE_MODEL,
                                "You verify claims about code behaviour against real execution output.",
                                user, 3000)
        if "verdicts" in data:
            return {int(k): v for k, v in data["verdicts"].items() if v in ("right", "wrong", "unclear")}
        if attempt == 2:
            raise ValueError(f"no 'verdicts' key after 3 attempts: {data!r}")


def mock_judge(claims):
    return {cid: ("right", "wrong", "unclear")[zlib.crc32(t.encode()) % 3] for cid, t in claims}


def cmd_verify(a):
    gt = load_gt()
    con = outlier.db()
    cl = None if a.mock else outlier.get_client()
    done = 0
    for q in QUESTIONS:
        run = run_for(con, q, a.mock)
        if not run:
            continue
        rows = con.execute("SELECT id, text FROM claims WHERE run_id=? AND verdict IS NULL", (run["id"],)).fetchall()
        if not rows:
            continue
        claims = [(r["id"], r["text"]) for r in rows]
        verdicts = mock_judge(claims) if a.mock else judge(cl, q, gt[q["id"]]["output"], claims)
        for cid, v in verdicts.items():
            con.execute("UPDATE claims SET verdict=?, marked_ts=strftime('%s','now') WHERE id=?", (v, cid))
        con.commit()
        done += 1
        print(f"{q['id']}: judged {len(verdicts)}/{len(claims)} claims")
    print(f"Verified {done} runs." if done else "Nothing to verify.")


def cmd_status(a):
    con = outlier.db()
    ran = sum(1 for q in QUESTIONS if run_for(con, q, a.mock))
    open_ = con.execute("SELECT COUNT(*) c FROM claims c JOIN runs r ON r.id=c.run_id "
                        "WHERE c.verdict IS NULL AND r.mock=?", (int(a.mock),)).fetchone()["c"]
    print(f"Questions run: {ran}/{len(QUESTIONS)}  |  claims awaiting a verdict: {open_}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("execute").set_defaults(fn=cmd_execute)
    b = sub.add_parser("batch"); b.add_argument("-n", type=int, default=8)
    b.add_argument("--plain", action="store_true"); b.add_argument("--mock", action="store_true")
    b.add_argument("--limit", type=int, default=0); b.set_defaults(fn=cmd_batch)
    v = sub.add_parser("verify"); v.add_argument("--mock", action="store_true"); v.set_defaults(fn=cmd_verify)
    s = sub.add_parser("status"); s.add_argument("--mock", action="store_true"); s.set_defaults(fn=cmd_status)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

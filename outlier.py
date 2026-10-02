#!/usr/bin/env python3
"""outlier: ask a cheap swarm, surface the minority claims, and record which dissent was right.

Commands:
  run "question" [-n 8] [--plain] [--mock]   run the swarm and store the result
  show [run_id]                               print a stored run
  todo                                        list minority claims not yet judged
  mark right|wrong|unclear ID [ID ...]        record the verdict on claims
  stats                                       hit rate by tier and by persona
"""
import argparse, json, os, random, re, sqlite3, sys, time, zlib
from concurrent.futures import ThreadPoolExecutor

DB_PATH = os.environ.get("OUTLIER_DB", os.path.expanduser("~/.outlier/ledger.db"))
AGENT_MODEL = os.environ.get("OUTLIER_AGENT_MODEL", "claude-haiku-4-5-20251001")
JUDGE_MODEL = os.environ.get("OUTLIER_JUDGE_MODEL", "claude-sonnet-5-5")

PERSONAS = [
    ("skeptic", "a careful skeptic who distrusts popular claims"),
    ("expert", "a domain expert focused on technical precision"),
    ("contrarian", "a contrarian who looks for what others overlook"),
    ("pragmatist", "a pragmatist focused on real-world practice"),
    ("historian", "a historian focused on how things came to be"),
    ("statistician", "a statistician focused on evidence and base rates"),
    ("engineer", "an engineer focused on failure modes and edge cases"),
    ("teacher", "a teacher focused on common misconceptions"),
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, question TEXT, n INTEGER,
  mode TEXT, mock INTEGER);
CREATE TABLE IF NOT EXISTS claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, text TEXT, support INTEGER,
  tier TEXT, personas TEXT, verdict TEXT, marked_ts REAL);
"""

MOCK_CONSENSUS = [
    "HTTP/3 runs over QUIC.",
    "QUIC is built on UDP.",
    "HTTP/3 avoids TCP head-of-line blocking.",
    "HTTP/3 integrates TLS 1.3.",
    "HTTP/3 is standardised in RFC 9114.",
]
MOCK_MINORITY = [
    "QUIC connections survive IP address changes through connection IDs.",
    "HTTP/3 removes the need for TLS certificates.",
    "HTTP/3 is always faster than HTTP/2.",
    "QUIC header protection hides packet numbers from middleboxes.",
    "HTTP/3 eliminates all effects of packet loss.",
]


def db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con


def get_client():
    try:
        import anthropic
    except ImportError:
        sys.exit("Install the SDK first: pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("Set ANTHROPIC_API_KEY, or use --mock.")
    return anthropic.Anthropic()


def ask_json(cl, model, system, user, max_tokens=2000):
    msg = cl.messages.create(model=model, max_tokens=max_tokens, system=system,
                             messages=[{"role": "user", "content": user}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    decoder = json.JSONDecoder()
    pos = 0
    while True:
        start = text.find("{", pos)
        if start == -1:
            raise ValueError(f"no JSON object in response: {text!r}")
        try:
            return decoder.raw_decode(text, start)[0]
        except json.JSONDecodeError:
            pos = start + 1


def live_agent(cl, question, persona_text):
    system = "You are one member of a panel answering independently."
    if persona_text:
        system += f" You are {persona_text}."
    user = (f"Question: {question}\n\nReturn ONLY JSON: {{\"claims\": [\"...\"]}} with 5 to 10 "
            "atomic factual claims. Each claim must be one self-contained, checkable statement.")
    try:
        return [str(c) for c in ask_json(cl, AGENT_MODEL, system, user)["claims"]][:12]
    except Exception as e:
        print(f"warning: one agent failed ({e})", file=sys.stderr)
        return []


def live_cluster(cl, agent_claims):
    lines = []
    for i, claims in enumerate(agent_claims):
        lines.append(f"Agent {i}:")
        lines += [f"- {c}" for c in claims]
    user = ("Merge claims that assert the same thing. Keep claims that differ or contradict "
            "separate. Every claim must land in exactly one group.\n"
            "Return ONLY JSON: {\"groups\": [{\"claim\": \"canonical wording\", "
            "\"agents\": [0, 2]}]}\n\n" + "\n".join(lines))
    data = ask_json(cl, JUDGE_MODEL, "You merge duplicate claims. Return only JSON.", user, 6000)
    n = len(agent_claims)
    return [{"claim": g["claim"], "agents": sorted({a for a in g["agents"]
             if isinstance(a, int) and 0 <= a < n})} for g in data["groups"]]


def mock_agents(question, n):
    rng = random.Random(zlib.crc32(question.encode()))
    return [[c for c in MOCK_CONSENSUS if rng.random() < 0.9] +
            [c for c in MOCK_MINORITY if rng.random() < 0.18] for _ in range(n)]


def group_exact(agent_claims):
    seen = {}
    for i, claims in enumerate(agent_claims):
        for c in claims:
            seen.setdefault(c, set()).add(i)
    return [{"claim": c, "agents": sorted(a)} for c, a in seen.items()]


def tier_of(support, n, cutoff):
    if support <= cutoff * n:
        return "minority"
    return "consensus" if support > n / 2 else "contested"


def print_run(con, run_id):
    run = con.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if not run:
        sys.exit("No such run.")
    tag = " [MOCK DATA]" if run["mock"] else ""
    print(f"\nRun {run['id']}  |  {run['n']} agents  |  {run['mode']}{tag}\n{run['question']}\n")
    for tier in ("minority", "contested", "consensus"):
        rows = con.execute("SELECT * FROM claims WHERE run_id=? AND tier=? ORDER BY support",
                           (run_id, tier)).fetchall()
        if rows:
            print(tier.upper())
            for r in rows:
                v = f"  <{r['verdict']}>" if r["verdict"] else ""
                print(f"  [{r['id']}] {r['support']}/{run['n']}  {r['text']}{v}")
            print()


def run_swarm(question, n=8, plain=False, mock=False, cutoff=0.3):
    """Run the swarm, store the result in the ledger, and return the run id."""
    personas = [("plain", None)] * n if plain else [PERSONAS[i % len(PERSONAS)] for i in range(n)]
    if mock:
        agent_claims = mock_agents(question, n)
        groups = group_exact(agent_claims)
    else:
        cl = get_client()
        with ThreadPoolExecutor(max_workers=min(n, 8)) as ex:
            agent_claims = list(ex.map(lambda p: live_agent(cl, question, p[1]), personas))
        groups = live_cluster(cl, agent_claims)
    con = db()
    cur = con.execute("INSERT INTO runs (ts, question, n, mode, mock) VALUES (?,?,?,?,?)",
                      (time.time(), question, n, "plain" if plain else "personas", int(mock)))
    run_id = cur.lastrowid
    for g in groups:
        if not g["agents"]:
            continue
        s = len(g["agents"])
        who = json.dumps([personas[i][0] for i in g["agents"]])
        con.execute("INSERT INTO claims (run_id, text, support, tier, personas) VALUES (?,?,?,?,?)",
                    (run_id, g["claim"], s, tier_of(s, n, cutoff), who))
    con.commit()
    return run_id


def cmd_run(a):
    run_id = run_swarm(a.question, a.n, a.plain, a.mock, a.cutoff)
    print_run(db(), run_id)


def cmd_show(a):
    con = db()
    run_id = a.run_id or (con.execute("SELECT MAX(id) m FROM runs").fetchone()["m"])
    if not run_id:
        sys.exit("No runs yet.")
    print_run(con, run_id)


def cmd_todo(a):
    con = db()
    rows = con.execute("SELECT c.id, c.support, r.n, c.text FROM claims c JOIN runs r ON r.id=c.run_id "
                       "WHERE c.tier='minority' AND c.verdict IS NULL ORDER BY c.id").fetchall()
    print(f"{len(rows)} minority claims awaiting a verdict")
    for r in rows:
        print(f"  [{r['id']}] {r['support']}/{r['n']}  {r['text']}")


def cmd_mark(a):
    con = db()
    for cid in a.ids:
        con.execute("UPDATE claims SET verdict=?, marked_ts=? WHERE id=?", (a.verdict, time.time(), cid))
    con.commit()
    print(f"Marked {len(a.ids)} claim(s) as {a.verdict}.")


def pct(r, w):
    return f"{100 * r / (r + w):.0f}%" if r + w else "n/a"


def cmd_stats(a):
    con = db()
    m = int(a.mock)
    runs = con.execute("SELECT COUNT(*) c FROM runs WHERE mock=?", (m,)).fetchone()["c"]
    label = "MOCK " if a.mock else ""
    print(f"\n{runs} {label}runs stored\n\nPRECISION BY TIER (right / (right + wrong))")
    for tier in ("consensus", "contested", "minority"):
        c = {v: 0 for v in ("right", "wrong", "unclear")}
        for r in con.execute("SELECT c.verdict, COUNT(*) k FROM claims c JOIN runs r ON r.id=c.run_id "
                             "WHERE c.tier=? AND c.verdict IS NOT NULL AND r.mock=? GROUP BY c.verdict",
                             (tier, m)):
            c[r["verdict"]] = r["k"]
        print(f"  {tier:<10} right {c['right']:<4} wrong {c['wrong']:<4} unclear {c['unclear']:<4} "
              f"precision {pct(c['right'], c['wrong'])}")
    per = {}
    for r in con.execute("SELECT c.personas, c.verdict FROM claims c JOIN runs r ON r.id=c.run_id "
                         "WHERE c.tier='minority' AND c.verdict IN ('right','wrong') AND r.mock=?", (m,)):
        for p in set(json.loads(r["personas"])):
            per.setdefault(p, {"right": 0, "wrong": 0})[r["verdict"]] += 1
    if per:
        print("\nMINORITY CLAIMS BY PERSONA")
        for p, c in sorted(per.items(), key=lambda kv: -(kv[1]["right"] + kv[1]["wrong"])):
            print(f"  {p:<13} right {c['right']:<4} wrong {c['wrong']:<4} precision {pct(c['right'], c['wrong'])}")
    print()


def main():
    p = argparse.ArgumentParser(prog="outlier", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("question")
    r.add_argument("-n", type=int, default=8); r.add_argument("--plain", action="store_true")
    r.add_argument("--mock", action="store_true"); r.add_argument("--cutoff", type=float, default=0.3)
    r.set_defaults(fn=cmd_run)
    s = sub.add_parser("show"); s.add_argument("run_id", nargs="?", type=int); s.set_defaults(fn=cmd_show)
    sub.add_parser("todo").set_defaults(fn=cmd_todo)
    m = sub.add_parser("mark"); m.add_argument("verdict", choices=["right", "wrong", "unclear"])
    m.add_argument("ids", nargs="+", type=int); m.set_defaults(fn=cmd_mark)
    st = sub.add_parser("stats"); st.add_argument("--mock", action="store_true"); st.set_defaults(fn=cmd_stats)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

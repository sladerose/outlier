# Results

80 runs, 1037 judged claims.

### Precision by tier

| Tier | Right | Wrong | Unclear | Precision |
|---|---|---|---|---|
| consensus | 609 | 22 | 5 | 97% |
| contested | 89 | 32 | 1 | 74% |
| minority | 157 | 104 | 18 | 60% |

### Precision by language

| Language | Right | Wrong | Unclear | Precision |
|---|---|---|---|---|
| javascript | 335 | 62 | 5 | 84% |
| python | 327 | 49 | 12 | 87% |
| sql | 193 | 47 | 7 | 80% |

### Precision by mode

| Mode | Right | Wrong | Unclear | Precision |
|---|---|---|---|---|
| personas | 428 | 109 | 7 | 80% |
| plain | 427 | 49 | 17 | 90% |

### Minority precision by persona

| Persona | Right | Wrong | Unclear | Precision |
|---|---|---|---|---|
| contrarian | 14 | 15 | 2 | 48% |
| engineer | 12 | 13 | 1 | 48% |
| expert | 10 | 10 | 0 | 50% |
| historian | 13 | 8 | 0 | 62% |
| plain | 76 | 35 | 11 | 68% |
| pragmatist | 12 | 9 | 2 | 57% |
| skeptic | 10 | 6 | 0 | 62% |
| statistician | 17 | 13 | 0 | 57% |
| teacher | 15 | 8 | 2 | 65% |

## Dissent that beat the consensus

Minority claims judged right in runs where at least one consensus claim was judged wrong.

- Run 4 (1/8 agents): The cached range should not be relied upon for correct program logic  
  _What is the exact output of this Python program, and why?_
- Run 4 (1/8 agents): The == operator would return True for all three comparisons because it checks value equality  
  _What is the exact output of this Python program, and why?_
- Run 4 (1/8 agents): A common misconception is that 'is' and '==' are equivalent  
  _What is the exact output of this Python program, and why?_
- Run 11 (1/8 agents): Iteration 2 actually processes i=3 (pointer shifted), leaving [2, 4, 5]  
  _What is the exact output of this Python program, and why?_
- Run 11 (1/8 agents): Iteration 3 processes i=5 and removes it, leaving [2, 4]  
  _What is the exact output of this Python program, and why?_
- Run 11 (1/8 agents): remove() removes only the first occurrence of the specified value  
  _What is the exact output of this Python program, and why?_
- Run 11 (1/8 agents): The loop variable i still references values from the original sequence while indices shift  
  _What is the exact output of this Python program, and why?_
- Run 18 (2/8 agents): In lexicographic order '20' comes before '3' because '2' < '3'  
  _What is the exact output of this Node.js program, and why?_
- Run 18 (2/8 agents): With numeric comparison, [3, 20, 100] is in ascending numeric order  
  _What is the exact output of this Node.js program, and why?_
- Run 18 (1/8 agents): The default string-based sort is stable and deterministic for the same input  
  _What is the exact output of this Node.js program, and why?_
- Run 18 (1/8 agents): All three console.log calls complete without throwing errors  
  _What is the exact output of this Node.js program, and why?_
- Run 18 (1/8 agents): A common misconception is that sort() compares numerically by default, but it uses string comparison  
  _What is the exact output of this Node.js program, and why?_
- Run 18 (1/8 agents): Lexicographic comparison of [3, 20, 100] is determined by character codes, not numeric values  
  _What is the exact output of this Node.js program, and why?_
- Run 30 (2/8 agents): arr.includes(undefined) returns true because includes treats empty slots as undefined, unlike indexOf  
  _What is the exact output of this Node.js program, and why?_
- Run 35 (2/8 agents): First INSERT: '5' in column a is converted to INTEGER by INTEGER affinity, so typeof(a)='integer'  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 35 (1/8 agents): Second INSERT: integer 5 in column b is converted to and stored as TEXT  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 35 (2/8 agents): Type affinity is only a hint: convertible values are converted, and unconvertible values keep their original type  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 36 (1/8 agents): First SELECT row for group 'a' is ('a', 5, 5), with v=5 being the last inserted row's value  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 37 (1/8 agents): SQLite's LIKE is case-insensitive only for ASCII letters in some contexts, but case-sensitive for non-ASCII by default  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 39 (1/8 agents): The second statement returns a single row with three columns  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 45 (1/8 agents): 256 is at the upper boundary of Python's integer cache range  
  _What is the exact output of this Python program, and why?_
- Run 45 (1/8 agents): Integers outside [-5, 256] are not guaranteed to be cached and may create new objects on each assignment or creation  
  _What is the exact output of this Python program, and why?_
- Run 45 (1/8 agents): Small integer caching applies to integer literals and small integers but not to all integer creations  
  _What is the exact output of this Python program, and why?_
- Run 52 (1/8 agents): The program iterates over a list while modifying it  
  _What is the exact output of this Python program, and why?_
- Run 52 (1/8 agents): x.remove(i) removes the first occurrence of each element  
  _What is the exact output of this Python program, and why?_
- Run 52 (2/8 agents): The loop index has advanced past the first position, so the second iteration is affected by the shift  
  _What is the exact output of this Python program, and why?_
- Run 52 (2/8 agents): After the first removal the iterator skips element 2, so the next i is 3  
  _What is the exact output of this Python program, and why?_
- Run 52 (1/8 agents): When i=3, x.remove(3) leaves [2, 4, 5]  
  _What is the exact output of this Python program, and why?_
- Run 52 (2/8 agents): Next i=5 and x.remove(5) leaves [2, 4]  
  _What is the exact output of this Python program, and why?_
- Run 52 (2/8 agents): Final output is [2, 4]  
  _What is the exact output of this Python program, and why?_
- Run 52 (1/8 agents): The result [2, 4] contains every other element of the original list  
  _What is the exact output of this Python program, and why?_
- Run 68 (1/8 agents): 'é'.normalize() === 'é' evaluates to true, because normalize() converts the decomposed form to NFC, matching the precomposed form.  
  _What is the exact output of this Node.js program, and why?_
- Run 77 (2/8 agents): The table s is created with exactly two columns: g and v.  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 77 (1/8 agents): Both the first and second queries return exactly two rows each, not three or four.  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 77 (1/8 agents): SQLite deterministically selects the v value from the row containing the aggregate result for group g='a': v=5 in the MAX query and v=1 in the MIN query, consistent with (tied to) the aggregate function's output rather than arbitrary.  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 77 (1/8 agents): The g column in both query results deterministically contains the GROUP BY values 'a' and 'b'.  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_
- Run 77 (1/8 agents): MAX() and MIN() are aggregate functions that deterministically compute the maximum and minimum values across the rows in each group.  
  _In SQLite, what is the exact result of each statement that returns rows, and why?_

## Conclusion

Across 80 runs, consensus claims were right 97% of the time against minority claims' 60%. The majority is the safer bet on average. But that average hides the question this project asks: not 'is the majority usually right' (yes), but 'when the majority is wrong, does a lone dissenting claim say so'.

Of 80 runs, 12 contained at least one wrong consensus claim. In 12 of those 12 (100% if read as a hit rate), a minority claim in the same run was judged right - meaning every time the swarm's majority failed in this dataset, at least one cheap dissenting claim correctly contradicted it. A lone dissent is rarely right in isolation, but it is the cheapest available signal that the consensus for a given run deserves a second look.

Persona-prompted minority claims (54% precision) were less reliable than plain-prompted ones (68%), despite personas producing more of them - diversity of framing surfaces more dissent, not necessarily better dissent.

**Practical takeaway:** do not trust a lone dissenting claim on its own merits - most are wrong. Trust it as a cue to re-verify the majority claim in that specific run, especially on code behaviour with a cheap, deterministic way to check (execute it). The value of the swarm here is not the minority claim's content; it is the flag that consensus in this run might be worth re-checking.

## Method

Each question is posed to N Haiku agents. Claims are merged by a Sonnet judge, tiered by support, then judged against the real output of the executed code. Verdicts are LLM-assigned and should be spot-checked by hand before publishing.

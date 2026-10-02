"""40 edge-case questions. Each snippet is executed to produce ground truth, so no answers are stored here.

Fields: id, lang (python | javascript | sql), code.
"""

PREFIX = {
    "python": "What is the exact output of this Python program, and why?",
    "javascript": "What is the exact output of this Node.js program, and why?",
    "sql": "In SQLite, what is the exact result of each statement that returns rows, and why?",
}

QUESTIONS = [
    # ---- Python ----
    {"id": "py01", "lang": "python", "code": '''def add(x, acc=[]):
    acc.append(x)
    return acc

print(add(1))
print(add(2))
print(add(3, []))
print(add(4))'''},
    {"id": "py02", "lang": "python", "code": '''fs = [lambda: i for i in range(3)]
print([f() for f in fs])
gs = [lambda i=i: i for i in range(3)]
print([g() for g in gs])'''},
    {"id": "py03", "lang": "python", "code": '''a = [1, 2, 3]
b = a
b += [4]
c = a
c = c + [5]
print(a, b, c)'''},
    {"id": "py04", "lang": "python", "code": '''a = 256
b = 256
print(a is b)
x = 1000
y = 1000
print(x is y)
print(int("1000") is int("1000"))'''},
    {"id": "py05", "lang": "python", "code": '''print(0.1 + 0.2 == 0.3)
print(round(2.5), round(3.5), round(-2.5))
print(round(2.675, 2))'''},
    {"id": "py06", "lang": "python", "code": '''d = {}
d[1] = "a"
d[1.0] = "b"
d[True] = "c"
print(d, len(d))'''},
    {"id": "py07", "lang": "python", "code": '''print(1 < 2 < 3, 1 < 2 > 1, (1 < 2) < 3, 3 > 2 > 2)
print(1 == 1.0 == True)'''},
    {"id": "py08", "lang": "python", "code": '''print([] == False, not [], bool([0]), bool(""), bool(" "))
print(None == False, None is None)'''},
    {"id": "py09", "lang": "python", "code": '''g = (x * x for x in range(3))
print(list(g))
print(list(g))
print(sum(g))'''},
    {"id": "py10", "lang": "python", "code": '''def f():
    try:
        return "try"
    finally:
        return "finally"

def g():
    for i in range(3):
        try:
            continue
        finally:
            print("cleanup", i)
    return "done"

print(f())
print(g())'''},
    {"id": "py11", "lang": "python", "code": '''x = [1, 2, 3, 4, 5]
for i in x:
    x.remove(i)
print(x)'''},
    {"id": "py12", "lang": "python", "code": '''t = ([1],)
try:
    t[0] += [2]
except TypeError:
    print("error")
print(t)'''},
    {"id": "py13", "lang": "python", "code": '''print(-7 // 2, -7 % 2, 7 // -2, divmod(-7, 2), int(-3.5))
print(7 % -3, -7.5 // 2)'''},
    {"id": "py14", "lang": "python", "code": '''class A:
    x = 1

class B(A):
    pass

b = B()
B.x = 2
A.x = 3
print(A.x, B.x, b.x)
b.x = 9
A.x = 4
print(A.x, B.x, b.x)'''},
    {"id": "py15", "lang": "python", "code": '''print(sorted(["b", "A", "a", "B"]))
print("ß".upper())
print(len("İ".lower()))
print("a" < "B", "a".casefold() < "B".casefold())'''},
    # ---- JavaScript ----
    {"id": "js01", "lang": "javascript", "code": '''console.log(typeof null, typeof undefined, typeof NaN, typeof []);
console.log(null == undefined, null === undefined, null == 0, null >= 0);'''},
    {"id": "js02", "lang": "javascript", "code": '''console.log([] + [], [] + {}, 1 + "2", "3" - 1, true + true);
console.log(String([1, [2, 3]]), [] + null + 1);'''},
    {"id": "js03", "lang": "javascript", "code": '''console.log([10, 9, 1].sort());
console.log([3, 20, 100].sort());
console.log([3, 20, 100].sort((a, b) => a - b));'''},
    {"id": "js04", "lang": "javascript", "code": '''console.log(0.1 + 0.2, 0.1 + 0.2 === 0.3);
console.log(9007199254740993, 2 ** 53 + 1);
console.log(9007199254740993n + 1n);'''},
    {"id": "js05", "lang": "javascript", "code": '''for (var i = 0; i < 3; i++) setTimeout(() => console.log("var", i), 0);
for (let j = 0; j < 3; j++) setTimeout(() => console.log("let", j), 0);'''},
    {"id": "js06", "lang": "javascript", "code": '''console.log(parseInt("08"), parseInt("0x1f"), parseInt(null), parseInt("1e3"), Number("1e3"));
console.log(Number(""), Number(" 12 "), Number("12px"), parseFloat("12.5px"));'''},
    {"id": "js07", "lang": "javascript", "code": '''console.log([1, 2, 3].map(parseInt));
console.log(["1", "2", "3"].map(Number));'''},
    {"id": "js08", "lang": "javascript", "code": '''console.log(NaN === NaN, Object.is(NaN, NaN));
console.log([NaN].includes(NaN), [NaN].indexOf(NaN));
console.log(Object.is(0, -0), 0 === -0);'''},
    {"id": "js09", "lang": "javascript", "code": '''console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
queueMicrotask(() => console.log("D"));
process.nextTick(() => console.log("E"));
console.log("F");'''},
    {"id": "js10", "lang": "javascript", "code": '''console.log(this, this === module.exports);
function f() { return this === globalThis; }
console.log(f());
const g = () => this === module.exports;
console.log(g());'''},
    {"id": "js11", "lang": "javascript", "code": '''const o = { a: 1, nested: { b: 1 } };
const p = { ...o, a: 2 };
Object.freeze(o);
o.a = 99;
o.nested.b = 99;
console.log(o, p);'''},
    {"id": "js12", "lang": "javascript", "code": '''console.log([..."héllo"].length, "😀".length, [..."😀"].length, "😀".split("").length);
console.log("e\\u0301".length, "é".length, "e\\u0301" === "é", "e\\u0301".normalize() === "é");'''},
    {"id": "js13", "lang": "javascript", "code": '''console.log(Math.max(), Math.min(), [] == ![], "b" + "a" + +"a" + "a");
console.log([] == 0, [0] == false, [1] == 1, [1, 2] == "1,2");'''},
    {"id": "js14", "lang": "javascript", "code": '''console.log(0 || "a", 0 ?? "a", "" || null, "" ?? null);
console.log(null?.x, (void 0)?.[0], NaN ?? 1, false ?? 1);'''},
    {"id": "js15", "lang": "javascript", "code": '''const arr = [1, 2, 3];
arr.length = 1;
arr[3] = 4;
console.log(arr, arr.length, 1 in arr, arr.indexOf(undefined), arr.includes(undefined));'''},
    # ---- SQL (SQLite) ----
    {"id": "sql01", "lang": "sql", "code": '''SELECT NULL = NULL, NULL IS NULL, 1 IN (2, NULL), 1 NOT IN (2, NULL), NULL OR 1, NULL AND 0;'''},
    {"id": "sql02", "lang": "sql", "code": '''SELECT COUNT(*), COUNT(x), AVG(x), SUM(x), TOTAL(x)
FROM (SELECT 1 AS x UNION ALL SELECT NULL UNION ALL SELECT 3);
SELECT SUM(x), TOTAL(x), COUNT(*) FROM (SELECT 1 AS x WHERE 0);'''},
    {"id": "sql03", "lang": "sql", "code": '''SELECT 7 / 2, 7 / 2.0, -7 / 2, 7 % 3, -7 % 3, CAST(7 AS REAL) / 2, 1 / 0;'''},
    {"id": "sql04", "lang": "sql", "code": '''CREATE TABLE t (x);
INSERT INTO t VALUES (3), (NULL), (1);
SELECT x FROM t ORDER BY x;
SELECT x FROM t ORDER BY x DESC;'''},
    {"id": "sql05", "lang": "sql", "code": '''CREATE TABLE t (a INTEGER, b TEXT);
INSERT INTO t VALUES ('5', '5');
INSERT INTO t VALUES (5, 5);
INSERT INTO t VALUES ('abc', 1);
SELECT typeof(a), typeof(b), a, b FROM t;'''},
    {"id": "sql06", "lang": "sql", "code": '''CREATE TABLE s (g, v);
INSERT INTO s VALUES ('a', 1), ('a', 5), ('b', 2);
SELECT g, v, MAX(v) FROM s GROUP BY g;
SELECT g, v, MIN(v) FROM s GROUP BY g;'''},
    {"id": "sql07", "lang": "sql", "code": '''SELECT 'a' = 'A', 'a' LIKE 'A', 'a' GLOB 'A', 'abc' LIKE 'a%', length('héllo'), upper('héllo');'''},
    {"id": "sql08", "lang": "sql", "code": '''CREATE TABLE u (x UNIQUE);
INSERT INTO u VALUES (1), (NULL), (NULL);
SELECT COUNT(*) FROM u;
INSERT INTO u VALUES (1);'''},
    {"id": "sql09", "lang": "sql", "code": '''SELECT COUNT(*) FROM (SELECT NULL UNION SELECT NULL);
SELECT COUNT(DISTINCT x), COUNT(x), COUNT(*) FROM (SELECT NULL AS x UNION ALL SELECT NULL);'''},
    {"id": "sql10", "lang": "sql", "code": '''SELECT 1 = 1, 1 == 1, 2 = TRUE, 'true' = TRUE, typeof(1 = 1), typeof(TRUE);'''},
]

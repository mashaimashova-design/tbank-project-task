import sys
import re
from collections import defaultdict

# ---------- Union-Find ----------
class DSU:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def add(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        else:
            self.parent[ry] = rx
            if self.rank[rx] == self.rank[ry]:
                self.rank[rx] += 1


# ---------- Read input ----------
lines = sys.stdin.read().splitlines()
if not lines:
    sys.exit()

K = int(lines[0])
text_lines = lines[1:]

# ---------- Normalize text ----------
words = []
for line in text_lines:
    if line == "":
        break
    tokens = line.split()
    for token in tokens:
        w = re.sub(r"[^a-zA-Z']", "", token).lower()
        if w:
            words.append(w)

# ---------- Build similarity groups ----------
dsu = DSU()
unique_words = set(words)

for w in unique_words:
    dsu.add(w)

# 1) Same length, differ in exactly one position
patterns = defaultdict(list)

for w in unique_words:
    if len(w) <= 1:
        continue
    for i in range(len(w)):
        pattern = w[:i] + "*" + w[i+1:]
        patterns[(len(w), pattern)].append(w)

for group in patterns.values():
    for i in range(1, len(group)):
        dsu.union(group[0], group[i])

# 2) Differ by adding/removing 'e' or 's' at end
word_set = set(unique_words)
for w in unique_words:
    if len(w) <= 1:
        continue
    for suffix in ("e", "s"):
        if w.endswith(suffix):
            short = w[:-1]
            if short in word_set and len(short) > 1:
                dsu.union(w, short)
        else:
            long = w + suffix
            if long in word_set:
                dsu.union(w, long)

# ---------- Build groups ----------
groups = defaultdict(set)
for w in unique_words:
    root = dsu.find(w)
    groups[root].add(w)

# Representative = lexicographically smallest word
representative = {}
for root, g in groups.items():
    representative[root] = min(g)

# ---------- Context frequency ----------
freq = defaultdict(int)

for i, w in enumerate(words):
    root = dsu.find(w)
    if len(groups[root]) <= 1:
        continue

    left = max(0, i - K)
    right = min(len(words) - 1, i + K)

    for j in range(left, right + 1):
        if j == i:
            continue
        if dsu.find(words[j]) == root:
            freq[root] += 1
            break

# ---------- Prepare output ----------
result = []
for root, count in freq.items():
    if count > 0:
        result.append((representative[root], count))

result.sort(key=lambda x: (-x[1], x[0]))

for rep, count in result:
    print(f"{rep}: {count}")

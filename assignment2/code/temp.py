import pprint

# prods = [
#	('Z', 'd'),
#	('Z', 'XYZ'),
#	('Y', ''),
#	('Y', 'c'),
#	('X', 'Y'),
#	('X', 'a')
# ]


prods = [
    ('S', 'Aa'),
    ('A', 'BCf'),
    ('A', 'BC'),
    ('B', 'b'),
    ('C', 'c'),
]

lhs = {v[0] for v in prods}
rhs = [set(v[1]) for v in prods]

temp = set()
for v in rhs:
    temp = temp.union(v)
rhs = temp
char = lhs.union(rhs)

First = {l: set() for l in char}
Follow = {l: set() for l in char}
Nullable = {l: False for l in char}

for c in rhs:
    if 'a' <= c <= 'z':
        First[c].add(c)

for xx in range(300):
    for p in prods:
        X = p[0]
        Y = p[1]
        k = len(Y)
        if k == 0 or all([Nullable[s] for s in Y]):
            Nullable[X] = True
        for i in range(k):
            for j in range(i + 1, k + 1):
                if i == 0 or all([Nullable[v] for v in Y[:i]]):
                    First[X] = First[X].union(First[Y[i]])
                if i == k - 1 or all([Nullable[v] for v in Y[i + 1:]]):
                    Follow[Y[i]] = Follow[Y[i]].union(Follow[X])
                if i + 1 == j or all([Nullable[v] for v in Y[i + 1: j]]):
                    Follow[Y[i]] = Follow[Y[i]].union(First[Y[j]])

pprint.pprint(First)
pprint.pprint(Follow)

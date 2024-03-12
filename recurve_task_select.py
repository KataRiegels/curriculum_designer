

def recurse_task_select(mdp, policy, beta, epsilon, curriculum):
    
    
    
    pass




"""

1: (solved, X, π0) = LEARN(M, π, β)
2: if solved then
3: ENQUEUE(C, M)
4: return (π0, C)
5: end if
6: Ms ← CREATESOURCETASKS(M, X)
7: P ← ∅
8: U ← ∅
9: for Ms ∈ Ms do
10: (solvedMs
, XMs
, πMs
) = LEARN(Ms, π, β)
11: if solvedMs
then
12: P ← P ∪ {(πMs
, Ms)}
13: else
14: U ← U ∪ {(Ms, XMs
)}
15: end if
16: end for
17: if |P| > 0 then
18: (πbest, Mbest,score) = GETBESTPOLICY(P, π, X)
19: if score >  then
20: ENQUEUE(C, Mbest)
21: return (πbest, C)
22: end if
23: end if
24: SORTBYSAMPLERELEVANCE(U, X, )
25: for (Ms, XMs
) ∈ U do
26: (π
0
s, C) ← RECURSETASKSELECT(Ms, π, β, , C)
27: if π
0
s 6= null then
28: return RECURSETASKSELECT(M, π0
s, β, , C)
29: end if
30: end for
31: return ( null, C)

"""












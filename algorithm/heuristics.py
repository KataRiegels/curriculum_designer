# Change S, A, P, R
# S = States
# A = Actions (left, right, up, down)
# P = Probability of moving to a new stat given the current state and action
# R = Reward function

def TaskSimplification(M, X, D, F, T):
    pass
#    F0 = Simplify(F)
#    M0 = T(D, F0)
#    return M0

# M is the MDP
# F is the freedom within domain - Parameters within the domain - Is a range of values that features can take
# D represents the universe of sub-tasks that can be created - Can be infinite in size
# X is created from current policy, and is used to generate a set of source tasks, tailored for that specific policy
# T is the task generator for the curriculum


#def Simplify(F):

#def T(D, F0):




result = TaskSimplification(M, X, D, F, τ)
print(result)

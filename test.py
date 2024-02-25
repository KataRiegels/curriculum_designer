from domains import grid_world as gw
from domains import mdp
print(gw.GRID_SIZE)


grid_size = (gw.GRID_WIDTH, gw.GRID_HEIGHT)
dof_width, dof_height = range(3, grid_size[0]), range(3, grid_size[1])
player_position, key_position, chest_position = range(grid_size[0], grid_size[1])

F_dof = [dof_width, 
         dof_height,
         player_position,
         key_position,
         chest_position]



# Change S, A, P, R

# S = States
# A = Actions (left, right, up, down)
# P = Probability of moving to a new stat given the current state and action
# R = Reward function

def task_simplification(M = None, X = None, D = None, F = None, T = None):
    
    pass
#    F0 = Simplify(F)
#    M0 = T(D, F0)
#    return M0

# M is the MDP
# F is the freedom within domain - Parameters within the domain - Is a range of values that features can take
# D represents the universe of sub-tasks that can be created - Can be infinite in size
# X is created from current policy, and is used to generate a set of source tasks, tailored for that specific policy
# T is the task generator for the curriculum


def simplify(F):
    pass

def t(D, F0):
    pass



# result = task_simplification(M, X, D, F, t)
result = task_simplification(F_dof)
print(result)
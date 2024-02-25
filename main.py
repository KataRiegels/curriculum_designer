import sys
import os
path = os.path.abspath("domains")
sys.path.append(path)
# from ..domains.M import *
print("--SCRIPT STARTING")
from domains.features import *
from domains.mdp import *

GS = GridSize()
GS.get_simplified()

mdp = MDP()

action = mdp.agent.take_action()
mdp.P(mdp.agent.state, action)

print(mdp.state)
print("--SCRIPT ENDING")
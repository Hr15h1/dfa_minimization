
# symbols = set()
# states = set()
# with open("DFA.txt", 'r') as f:
#     lines = f.readlines()
#     print(lines)
#     transitions = lines[:-3]
#     symbols = lines[-1].split(",")
#     print(transitions)
    
from graphviz import Digraph
import time
t_table = [[0,1,2], [1,0,2], [1,1,4], [2,1,4], [2,0,1], [3,0,2], [3,1,4], [4,0,4], [4,1,4]]
symbols = ['0', '1']
states = [0,1,2,3,4]
initial_state = 0
final_state = 4
g = Digraph()
for state in states:
    g.node(
        chr(ord('A') + state), 
        label = chr(ord('A') + state),
        shape = "doublecircle" if state == final_state else "circle"
    )

for t in t_table:
    g.edge(
        chr(ord('A') + t[0]),
        chr(ord('A') + t[2]),
        label = f"{t[1]}"
    )

g.render('dfa', 'images/', format = 'png', view = True)











# symbols = set()
# states = set()
# with open("DFA.txt", 'r') as f:
#     lines = f.readlines()
#     print(lines)
#     transitions = lines[:-3]
#     symbols = lines[-1].split(",")
#     print(transitions)
    
from graphviz import Digraph
from datetime import datetime
t_table = [[0,1,2], [1,0,2], [1,1,4], [2,1,4], [2,0,1], [3,0,2], [3,1,4], [4,0,4], [4,1,4]]
symbols = ['0', '1']
states = ['q0','q1','q2','q3','q4']
initial_state = 'q0'
final_state = 'q4'

def dfa_visualizer(t_table, states, initial_state, final_state):
    g = Digraph()
    g.attr(rankdir = 'LR')
    g.node('start', shape = 'point', style = 'invis')
    for state in states:
        g.node(
            state, 
            label = state,
            shape = "doublecircle" if state == final_state else "circle"
        )

    g.edge('start', initial_state)
    for t in t_table:
        g.edge(
            states[t[0]],
            states[t[2]],
            label = f"{t[1]}"
        )

    g.render(f'dfa_{datetime.now().strftime("%M%S")}', 'images/', format = 'png')

dfa_visualizer(t_table, states, initial_state, final_state)










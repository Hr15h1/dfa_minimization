from graphviz import Digraph
from datetime import datetime
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol
import os
import inquirer

t_table = [[0,1,2], [1,0,2], [1,1,4], [2,1,4], [2,0,1], [3,0,2], [3,1,4], [4,0,4], [4,1,4]]
# t_table2 = [
#     [1, 0, 3], [1, 1, 2],
#     [0, 0, 1], [0, 1, 4],
#     [2, 0, 5], [2, 1, 6],
#     [3, 0, 7], [3, 1, 8],
#     [4, 0, 9], [4, 1, 10],
#     [5, 0, 11], [5, 1, 12],
#     [6, 0, 13], [6, 1, 14],
#     [7, 0, 15], [7, 1, 16],
#     [8, 0, 17], [8, 1, 18],
#     [9, 0, 19], [9, 1, 0],
#     [10, 0, 1], [10, 1, 2],
#     [11, 0, 3], [11, 1, 4],
#     [12, 0, 5], [12, 1, 6],
#     [13, 0, 7], [13, 1, 8],
#     [14, 0, 9], [14, 1, 10],
#     [15, 0, 11], [15, 1, 12],
#     [16, 0, 13], [16, 1, 14],
#     [17, 0, 15], [17, 1, 16],
#     [18, 0, 17], [18, 1, 18],
#     [19, 0, 19], [19, 1, 0],

# ]
symbols = ['0', '1']
states = {'q0', 'q1', 'q2', 'q3', 'q4'}
initial_state = 'q0'
final_states = {'q4'}

def dfa_visualizer(t_table, states, initial_state, final_states):
    g = Digraph()
    g.attr(rankdir = 'LR')
    g.node('start', shape = 'point', style = 'invis')
    for state in states:
        g.node(
            state, 
            label = state,
            shape = "doublecircle" if state in final_states else "circle"
        )

    g.edge('start', initial_state)
    for t in t_table:
        g.edge(
            states[t[0]],
            states[t[2]],
            label = f"{t[1]}"
        )

    if not os.path.exists('images'):
        os.makedirs('images')
    g.render(f'dfa_{datetime.now().strftime("%M%S")}', 'images/', format = 'png')

dfa_visualizer(t_table, states, initial_state, final_states)


def automata(states, symbols, initial_state, final_state, t_table):

    dfa = DeterministicFiniteAutomaton()
    state_vars = {}
    sym_vars = {}
    print(states)
    for state in states:
        state_vars.update({f"state_{state}": State(state)})
        if state == initial_state:
            dfa.add_start_state(state_vars[f"state_{state}"])
        if state == final_state:
            dfa.add_final_state(state_vars[f"state_{state}"])
    print(state_vars)
    for symbol in symbols:
        sym_vars.update({f"symbol_{symbol}": Symbol(symbol)})

    print(sym_vars)


    for t in t_table:
        dfa.add_transition(
            state_vars[f"state_q{t[0]}"],
            sym_vars[f"symbol_{t[1]}"],
            state_vars[f"state_q{t[2]}"]
        )   

    return dfa

dfa = automata(states, symbols, initial_state, final_states, t_table)
print(dfa.accepts("110001"))
print(dfa.to_dict())

def hopcroft_minimize(dfa: DeterministicFiniteAutomaton):
    transitions = dfa.to_dict()
    
    symbols = dfa.symbols

    final_states = set(dfa.final_states)
    non_final_states = set(dfa.states) - final_states

    P = {frozenset(final_states), frozenset(non_final_states)}
    W = {frozenset(final_states), frozenset(non_final_states)}


    while W:
        A = W.pop()

        for symbol in symbols:

            X = {state for state in transitions if symbol in transitions[state] and transitions[state][symbol] in A}
            
            new_P = set()

            for Y in P:

                intersect = X & Y
                difference = Y - X

                if intersect and difference:
                    new_P.update([frozenset(intersect), frozenset(difference)])

                    if Y in W:
                        W.remove(Y)
                        W.update([frozenset(intersect), frozenset(difference)])
                    else:
                        W.add(frozenset(intersect) if len(intersect) <= len(difference) else frozenset(difference))
                
                else:
                    new_P.add(Y)
            P = new_P
    
    new_states = []
    for state in P:
        name = ""
        for s in list(state):
            name += f"{s}"
        new_states.append(name)

    new_dfa = DeterministicFiniteAutomaton()
    state_map = {state: i for i, part in enumerate(P) for state in part}

    for part in P:
        rep = next(iter(part))
        if rep in dfa.final_states:
            new_dfa.add_final_state(State(new_states[state_map[rep]]))
        if rep == dfa.start_state:
            new_dfa.add_start_state(State(new_states[state_map[rep]]))
        for symbol in symbols:
            if rep in transitions and symbol in transitions[rep]:
                new_dfa.add_transition(
                    State(new_states[state_map[rep]]), symbol, State(new_states[state_map[transitions[rep][symbol]]])
                )

    return new_dfa
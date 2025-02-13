from graphviz import Digraph, render
from datetime import datetime
from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State, Symbol
import os
import inquirer
from collections import defaultdict
from PIL import Image
from tabulate import tabulate

#This function is for getting the DFA from the user
#It takes the states, symbols, initial state, final states and the transition table as input
#It also checks if the DFA is valid
#It returns the states, symbols, initial state, final states and the transition table, if the DFA is valid
def get_dfa():
    
    questions = [
            inquirer.List(
                'action',
                message = 'How would you like to input the DFA?',
                choices = ["Through terminal", "text file"]
            )
        ]
    answers = inquirer.prompt(questions)

    transitions = defaultdict(dict)

    if answers['action'] == "Through terminal":
        states = set(input("Enter the states of the DFA seperated by comma: ").split(','))
        symbols = set(input("Enter the symbols of the DFA seperated by comma: ").split(','))
        initial_state = input("Enter the initial state of the DFA: ")

        final_states = set(input("Enter the final states of the DFA seperated by comma: ").split(','))

        t_table = []
        while True:
            t = input("Enter the transition table of the DFA in the format 'state, symbol, state' or 'exit' to stop: ")
            if t.lower() == 'exit':
                break

            t = t.split(',')

            if len(t) != 3:
                print("Invalid input!. Make sure that the input is in the format 'state, symbol, state'")
                continue

            state_from, symbol, state_to = t
            
            if symbol in transitions[state_from]:
                print(f"You have already created a transition for this symbol from {state_from} for symbol {symbol} to {transitions[state_from][symbol]}")
                continue

            t_table.append([state_from, symbol, state_to])
            transitions[state_from][symbol] = state_to

    else:
        file_name = str(input("Enter file name (Must be a text file): "))
        with open (file_name, 'r') as f:
            lines = f.readlines()

            t_table = []

            for t in lines[:-4]:
                t = t[:-1].split(',')
                
                if len(t) != 3:
                    print(f"Found mistake in line {lines.index(t)} of the text file {file_name}. Please correct it!")
                    exit(0)

                state_from, symbol, state_to = t

                if symbol in transitions[state_from]:
                    print(f"You have already created a transition for this symbol from {state_from} for symbol {symbol} to {transitions[state_from][symbol]}")
                    continue
            
                t_table.append([state_from, symbol, state_to])
                transitions[state_from][symbol] = state_to

            states = set(lines[-4].strip().split(','))
            symbols = set(lines[-3].strip().split(','))
            initial_state = lines[-2].strip().split(',')[0]
            final_states = set(lines[-1].strip().split(','))


    is_valid_dfa = all(len(transitions[state]) == len(symbols) for state in states)

    if is_valid_dfa:
        return states, symbols, initial_state, final_states, t_table
    else:
        print("Invalid DFA. Make sure that all states have transitions for all symbols")
        return get_dfa()


#This function is for creating a visualization of the DFA
#It takes the transition table, states, initial state and final states as input
#It creates a visualization of the DFA and saves it as a png file
#It returns the path of the image
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
            t[0],
            t[2],
            label = f"{t[1]}"
        )

    if not os.path.exists('images'):
        os.makedirs('images')
    path = g.render(f'dfa_{datetime.now().strftime("%M%S")}', 'images/', format = 'png')

    return path

#This function is for creating the DFA from the states, symbols, initial state, final states and the transition table
#It creates the DFA using the pyformlang library
#It returns the DFA
def automata(states, symbols, initial_state, final_state, t_table):

    dfa = DeterministicFiniteAutomaton()
    state_vars = {}
    sym_vars = {}

    for state in states:
        state_vars.update({f"state_{state}": State(state)})
        if state == initial_state:
            dfa.add_start_state(state_vars[f"state_{state}"])
        if state in final_state:
            dfa.add_final_state(state_vars[f"state_{state}"])
    for symbol in symbols:
        sym_vars.update({f"symbol_{symbol}": Symbol(symbol)})

    for t in t_table:
        dfa.add_transition(
            state_vars[f"state_{t[0]}"],
            sym_vars[f"symbol_{t[1]}"],
            state_vars[f"state_{t[2]}"]
        )   

    return dfa

#This function is for checking if the DFA is minimized
#It takes the states, symbols, final states and the transition table as input
#This function checks if the DFA is minimized using the table filling algorithm
#It returns True if the DFA is minimized and False otherwise
def check_minimization(states, symbols, final_states, t_table):
    n = len(states)

    states = list(states)
    final_states = list(final_states)

    transitions = defaultdict(dict)

    table = [[False] * n for _ in range(n)]

    for i in range(n):
        for j in range(i+1, n):
            if (states[i] in final_states and states[j] not in final_states) or (states[i] not in final_states and states[j] in final_states):
                table[i][j] = True

    for t in t_table:
        state_from, symbol, state_to = t
        transitions[state_from][symbol] = state_to

    changed = True

    while changed:
        changed = False
        for i in range(n):
            for j in range(i+1, n):
                if not table[i][j]:
                    for symbol in symbols:
                        next_i = states.index(transitions[states[i]][symbol])
                        next_j = states.index(transitions[states[j]][symbol])

                        if next_i != next_j and table[min(next_i, next_j)][max(next_i, next_j)]:
                            table[i][j] = True
                            changed = True
    
    for i in range(n):
        for j in range(i+1, n):
            if not table[i][j]:
                return False
    return True
                    
#This function is for minimizing the DFA
#It takes the DFA as input
#It minimizes the DFA using the Hopcroft's algorithm
#It returns the minimized DFA
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

#This is the main function
#Menu driven program for creating, visualizing, minimizing and testing a DFA
#It uses the pyformlang library for creating and minimizing the DFA
#It uses the graphviz library for visualizing the DFA
#It uses the inquirer library for creating the menu
#It uses the PIL library for displaying the image
if __name__ == '__main__':

    states = set()
    symbols = set()
    initial_state = ""
    final_states = set()
    t_table = []
    minimized_dfa = None

    while True:
        questions = [
            inquirer.List(
                'action',
                message = 'What would you like to do?',
                choices = ['Create DFA', 'Display DFA', 'Check Minimization', 'Minimize DFA', 'Test string acceptance', 'View Transition Table', "Exit"]
            )
        ]
        answers = inquirer.prompt(questions)

        match answers['action']:

            #Create the DFA
            case "Create DFA":
                states, symbols, initial_state, final_states, t_table = get_dfa()
                
                m = f"The DFA you have entered has states - {states},\n accepted symbols - {symbols},\n starting state - {initial_state},\n final states - {final_states},\n and transition function - {t_table}"
                print(m)
                print()

            #Display the DFA
            case "Display DFA":
                print("Creating a visualization of the DFA you have entered...")
                print()
                path = dfa_visualizer(t_table, states, initial_state, final_states)

                if path:
                    img = Image.open(path)
                    img.show()

                else:
                    print("An error occured while creating the visualization")

            #Check if the DFA is minimized
            case "Check Minimization":
                if check_minimization(states, symbols, final_states, t_table):
                    print("The DFA is already minimized.")
                    print()
                else:
                    print("The DFA is not minimized.")
                    print()

            #Minimize the DFA
            case "Minimize DFA":
                dfa = automata(states, symbols, initial_state, final_states, t_table)
                minimized_dfa = hopcroft_minimize(dfa)
                c = input("Do you want to visualize the minimized DFA? (y/n): ")
                if c.lower() == 'y':
                    minimized_dfa.write_as_dot(f"minimized_dfa_{datetime.now().strftime('%M%S')}.dot")
                    file_name = f"minimized_dfa_{datetime.now().strftime('%M%S')}.dot"
                    image_filename = f"minimized_dfa_{datetime.now().strftime('%M%S')}.dot.png"
                    render('dot', 'png', file_name)
                    img = Image.open(image_filename)
                    img.show()
                    print()
                else:
                    print("Minimized DFA created")
                    print(minimized_dfa.to_dict())
                    print()

            #Test string acceptance
            case "Test string acceptance":
                if minimized_dfa is not None:
                    print("The program will use the new minimized DFA")
                    dfa = minimized_dfa
                else:  
                    dfa = automata(states, symbols, initial_state, final_states, t_table)
                s = str(input("Enter the string you want to test: "))
                ac = dfa.accepts(s)
                if ac:
                    print(f"The DFA accepts the string {s}.")
                    print()
                else:
                    print(f"The DFA does not accept the string {s}.")
                    print()

            #View the transition table
            case "View Transition Table":
                print(f"The transition table of the DFA you have entered is:")
                print()
                t_dict = dfa.to_dict()
                t_table_form = []
                for state, transitions in t_dict.items():
                    for input_val, next_state in transitions.items():
                        t_table_form.append([state.value, input_val.value, next_state.value])
                print(tabulate(t_table_form, headers = ['Start state', 'Symbol', 'End state'], colalign = ['center', 'center', 'center'], tablefmt='rounded_grid'))
                if minimized_dfa is not None:
                    print(f"And the transition table of the minimized DFA is: {minimized_dfa.to_dict()}")
                    print()
                    t_dict = minimized_dfa.to_dict()
                    t_table_form = []
                    for state, transitions in t_dict.items():
                        for input_val, next_state in transitions.items():
                            t_table_form.append([state.value, input_val.value, next_state.value])
                    print(tabulate(t_table_form, headers = ['Start state', 'Symbol', 'End state'], colalign = ['center', 'center', 'center'], tablefmt='rounded_grid'))
            
            #Exit the program
            case "Exit":
                print("Exiting...")
                exit(0)
                
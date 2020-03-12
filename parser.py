from anytree import Node
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import UniqueDotExporter
import os
import re
import sys

# need graphviz installed

'''
TODO
Check connectives/equality and vars/consts/preds do not share common names
Check : not in values for input file
Check forbidden strings for non Terminals vs input terminals
Check num of parameters for predicates is a positive integer
Check predicates have []
'''

def writeToLog(data):
    if os.path.exists('parser.log'):
        mode = 'a'
    else:
        mode = 'w'
    with open('parser.log', mode) as log:
        log.write(data + '\n')
        log.close()

def writeGrammar(data):
    if os.path.exists('grammar.txt'):
        mode = 'a'
    else:
        mode = 'w'
    with open('grammar.txt', mode) as grammar:
        grammar.write(data + '\n')
        grammar.close()

def commonNames(name1, group1, name2, group2):
    if set(group1).intersection(set(group2)):
        message = "Error: {} and {} share the following names : {}".format(name1, name2, set(group1).intersection(set(group2)))
        writeToLog(message)
        sys.exit()



def generateGrammar():
    terms = []
    
    # Read in file from command line
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = 'file.txt'
        
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                line = line.rstrip('\n')
                line = line.split(':')
                if len(line) > 2:
                    message = "Error: multiple colons found in line of input file"
                    writeToLog(message)
                    exit(1)
                value = line[1]
                terms.append(line)
            else:
                terms[-1][1] = value + line
                value = terms[-1]
                
    for term in terms:
        if term[0] == 'variables':
            variables = term[1].split()
        if term[0] == 'constants':
            constants = term[1].split()
        if term[0] == 'predicates':
            predicates = term[1].split()
        if term[0] == 'equality':
            equality = term[1].split()
        if term[0] == 'connectives':
            connectives = term[1].split()
        if term[0] == 'quantifiers':
            quantifiers = term[1].split()
        if term[0] == 'formula':
            formula = term[1].split()

    # Check number of terminals is correct for equality, connectives and quantifiers
    if len(equality) != 1:
        message = "Error: {} equality operators input instead of 1".format(len(equality))
        writeToLog(message)
        print('Error: Incorrect number of equality operators')
        sys.exit()
    elif len(connectives) != 5:
        message = "Error: {} connectives input instead of 5".format(len(connectives))
        writeToLog(message)
        print('Error: Incorrect number of connectives')
        sys.exit()
    elif len(quantifiers) != 2:
        message = "Error: {} quantifiers input instead of 2".format(len(quantifiers))
        writeToLog(message)
        print('Error: Incorrect number of quantifiers')
        sys.exit()

    vcp_pattern = re.compile('([A-Z]|[a-z]|[0-9]|_)+')
    connective_pattern = re.compile('([A-Z]|[a-z]|[0-9]|_|\\\\)+')
    equality_pattern = re.compile('([A-Z]|[a-z]|[0-9]|_|=|\\\\)+')
    
    for variable in variables:
        if not vcp_pattern.match(variable):
            message = "Error: variable {} can only contain letters, characters and underscores".format(variable)
            writeToLog(message)
            exit(1)

    for constant in constants:
        if not vcp_pattern.match(constant):
            message = "Error: constant {} can only contain letters, characters and underscores".format(constant)
            writeToLog(message)
            exit(1)
            
    if not equality_pattern.match(equality[0]):
        message = "Error: equality {} can only contain letters, characters, _, \\ or =".format(equality[0])
        writeToLog(message)
        exit(1)
        
    for connective in connectives:
        if not connective_pattern.match(connective):
            message = "Error: connective {} can only contain letters, characters, _ or \\".format(connective)
            print(message)
            writeToLog(message)
            exit(1)
        
    non_terminals = ['S', 'Q', 'P', 'E', 'C', 'V', 'J', 'T', 'A']

    # Production rules for the CFG accounting for left factoring
    production_rules = {
        'S' : ['P', '(A', 'QVS', connectives[-1] + 'S'],
        'A': ['SJS)', 'TET)'],
        'E': equality,
        'T': ['C, V'],
        'Q': quantifiers,
        'V': variables,
        'C': constants,
        'P': [],
        'J': connectives[:-1]
    }

    predicate_names = []
    predicate_symbol = []
    # Get names of predicate terminals and construct predicate syntax
    for predicate in predicates:
        idx = re.search(r"\d", predicate).start()
        idx1 = re.search(r"\d", predicate).end()
        name = predicate[0:idx-1]
        predicate_names.append(name + '()')
        predicate_symbol.append(name)
        num = int(predicate[idx:idx1])
        atom = name + '(' + 'V,' * (num-1) + 'V' + ')'
        production_rules['P'].append(atom)
        
    # Check predicates, variables and constants do not have any names in common
    if set(predicate_symbol).intersection(set(constants)):
        message = "Error: predicates and constants have shared names : {}".format(set(predicate_symbol).intersection(set(constants)))
        writeToLog(message)
        sys.exit()

    if set(predicate_symbol).intersection(set(variables)):
        message = "Error: predicates and variables have shared names : {}".format(set(predicate_symbol).intersection(set(variables)))
        writeToLog(message)
        sys.exit()

    if set(variables).intersection(set(constants)):
        message = "Error: variables and constants have shared names : {}".format(set(variables).intersection(set(constants)))
        writeToLog(message)
        sys.exit()

    if set(variables).intersection(set(connectives)):
        message = "Error: variables and connectives have shared names : {}".format(set(variables).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    if set(constants).intersection(set(connectives)):
        message = "Error: constants and connectives have shared names : {}".format(set(constants).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    if set(predicates).intersection(set(connectives)):
        message = "Error: predicates and connectives have shared names : {}".format(set(predicates).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    if set(variables).intersection(set(connectives)):
        message = "Error: variables and connectives have shared names : {}".format(set(variables).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    if set(constants).intersection(set(connectives)):
        message = "Error: constants and connectives have shared names : {}".format(set(constants).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    if set(predicates).intersection(set(connectives)):
        message = "Error: predicates and connectives have shared names : {}".format(set(predicates).intersection(set(connectives)))
        writeToLog(message)
        sys.exit()

    commonNames('variables', variables, 'equality', equality)

    commonNames('constants', constants, 'equality', equality)

    commonNames('predicates', predicates, 'equality', equality)
    
    # Format Formula to separate predicate and equality expressions
    bracket_terms = {}
    for term in formula:
        # Case 1: Predicate or equality with no spaces
        if '(' in term and ')' in term:
            idx1 = term.index('(')
            idx2 = term.index(')')
            comma_index = [i for i in range(len(term)) if term[i] == ',']
            term_list = [term[:idx1], '(']
            prev_idx = idx1+1
            for idx in comma_index:
                term_list += [term[prev_idx:idx], ',']
                prev_idx = idx+1
            term_list += [term[prev_idx:idx2], term[idx2], term[idx2+1:]]
            bracket_terms[term] =  term_list
        # Case 2 RHS of equality or Predicate
        elif ')' in term:
            # Case 2a Predicate
            if ',' in term:
                idx1 = term.index(')')
                comma_index = [i for i in range(len(term)) if term[i] == ',']
                term_list = []
                prev_idx = 0
                for idx in comma_index:
                    term_list += [term[prev_idx:idx], ',']
                    prev_idx = idx+1
                term_list += [term[prev_idx:idx1], ')', term[idx1+1:]]
                bracket_terms[term] = term_list
            # Case 2b Equality
            elif len(term) > 1:
                idx1 = term.index(')')
                bracket_terms[term] = [term[:idx1], ')', term[idx1+1:]]
        # Case 3 LHS of equality or Predicate
        elif '(' in term:
            # Case 3a Predicate
            if ',' in term:
                idx1 = term.index('(')
                comma_index = [i for i in range(len(term)) if term[i] == ',']
                term_list = [term[:idx1], '(']
                prev_idx = idx1+1
                for idx in comma_index:
                    term_list += [term[prev_idx:idx], ',']
                    prev_idx = idx+1
                term_list += term[prev_idx:]
                bracket_terms[term] = term_list
            # Case 3b Equality
            elif len(term) > 1:
                idx1 = term.index('(')
                bracket_terms[term] = [term[:idx1], '(', term[idx1+1:]]
        # Case 4 Middle of predicate
        elif ',' in term:
            if len(term) > 1:
                idx1 = term.index(',')
                bracket_terms[term] = [term[:idx1], ',', term[idx1+1:]]
            
    # replace joined terms in formula with their respected list of separated terms
    for k, v in bracket_terms.items():
        idx = formula.index(k)
        formula = formula[:idx] + v + formula[idx+1:]
        
    # remove any empty string terms from formula
    for term in formula:
        if term == '':
            formula.remove(term)

    # print Context Free Grammar to Command Line
    print('Non Terminal Symbols: ', ' '.join(non_terminals))
    print('Terminal Symbols: ', ' '.join(equality + connectives + variables + constants + quantifiers + predicate_symbol + ['(', ')', ',']))
    print('Production Rules: ')
    print('S ->', '|'.join(production_rules['S']))
    print('A ->', '|'.join(production_rules['A']))
    print('E ->', '|'.join(production_rules['E']))
    print('T ->', '|'.join(production_rules['T']))
    print('Q ->', '|'.join(production_rules['Q']))
    print('V ->', '|'.join(production_rules['V']))
    print('C ->', '|'.join(production_rules['C']))
    print('P ->', '|'.join(production_rules['P']))
    print('J ->', '|'.join(production_rules['J']))
    writeGrammar('Grammar For {}'.format(file))
    writeGrammar('Non Terminal Symbols: ' + ' '.join(non_terminals))
    writeGrammar('Terminal Symbols: ' + ' '.join(equality + connectives + variables + constants + quantifiers + predicate_symbol + ['(', ')', ',']))
    writeGrammar('Production Rules:')
    writeGrammar('S -> ' + '|'.join(production_rules['S']))
    writeGrammar('A -> ' + '|'.join(production_rules['A']))
    writeGrammar('E -> ' + '|'.join(production_rules['E']))
    writeGrammar('T -> ' + '|'.join(production_rules['T']))
    writeGrammar('Q -> ' + '|'.join(production_rules['Q']))
    writeGrammar('V -> ' + '|'.join(production_rules['V']))
    writeGrammar('C -> ' + '|'.join(production_rules['C']))
    writeGrammar('P -> ' + '|'.join(production_rules['P']))
    writeGrammar('J -> ' + '|'.join(production_rules['J']))

    # return production_rules, non-terminal symbols and the input formula to be parsed
    return formula, production_rules, non_terminals

        
    


class Parser():
    def __init__(self, formula, production_rules, non_terminals):
        self.formula = formula
        self.production_rules = production_rules
        self.non_terminals = non_terminals
        self.index = 0
        self.lookahead = None
        self.length = len(formula)
        self.nodes = {}
        self.counter = 0

    def start(self, parent=None):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('S', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.predicate(parent):
            return True
        parent.children = []
        if self.lookahead == self.production_rules['S'][-1][:-1]:
            self.match(production_rules['S'][-1][:-1], parent)
            self.start(parent)
            return True
        parent.children = []
        if self.lookahead == '(':
            self.match('(', parent)
            self.atom(parent)
            return True
        parent.children = []
        if self.quantifier(parent):
            self.variable(parent)
            self.start(parent)
            return True
        else:
            print("Syntax Error")
            message = "Syntax Error: {} at position {} could not be parsed".format(self.lookahead, self.index)
            writeToLog(message)
            return

    def atom(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('A', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.term(parent):
            self.equality(parent)
            self.term(parent)
            self.match(')', parent)
            return True
        parent.children = []
        if self.start(parent):
            self.connective(parent)
            self.start(parent)
            self.match(')', parent)
            return True
        else:
            self.counter -= 1
            return False

    def equality(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('E', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.lookahead == self.production_rules['E'][0]:
            self.match(self.production_rules['E'][0], parent)
            return True
        self.counter -= 1

    def variable(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('V', parent)
        parent = self.nodes['var' + str(self.counter)]
        for variable in self.production_rules['V']:
            if self.lookahead == variable:
                self.match(variable, parent)
                return True
        self.counter -= 1

    def predicate(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('P', parent)
        parent = self.nodes['var' + str(self.counter)]
        for predicate in self.production_rules['P']:
            if self.lookahead == predicate[:predicate.index('(')]:
                self.match(predicate[:predicate.index('(')], parent)
                self.match('(', parent)
                for i in range(predicate.count('V')-1):
                    self.variable(parent)
                    self.match(',', parent)
                self.variable(parent)
                self.match(')', parent)
                return True
        self.counter -= 1
        return False

    def term(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('T', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.variable(parent):
            return True
        parent.children = []
        if self.constant(parent):
            return True
        else:
            self.counter -= 1
            return False

    def quantifier(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('Q', parent)
        parent = self.nodes['var' + str(self.counter)]
        for quantifier in self.production_rules['Q']:
            if self.lookahead == quantifier:
                self.match(quantifier, parent)
                return True
        self.counter -= 1
        return False
    
    def constant(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('C', parent)
        parent = self.nodes['var' + str(self.counter)]
        for constant in self.production_rules['C']:
            if self.lookahead == constant:
                self.match(constant, parent)
                return True
        self.counter -= 1
        return False

    def connective(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('J', parent)
        parent = self.nodes['var' + str(self.counter)]
        for connective in self.production_rules['J']:
            if self.lookahead == connective:
                self.match(connective, parent)
                return True
        self.counter -= 1
        return False

    def parse(self):
        self.lookahead = formula[self.index]
        self.start()

    def match(self, terminal, parent):
        self.counter += 1
        if self.lookahead == terminal:
            if terminal[0] == '\\':
                self.nodes['var' + str(self.counter)] = Node('\\' + terminal, parent)
            else:
                self.nodes['var' + str(self.counter)] = Node(terminal, parent)
            lookahead = self.nextTerminal()
        else:
            print("Syntax Error")
            message = "Syntax Error: {} at position {} could not be parsed".format(self.lookahead, self.index)
            writeToLog(message)

    def nextTerminal(self):
        print(self.index, self.lookahead)
        self.index += 1
        if self.index == self.length:
            writeToLog("Success: The Formula: {} is valid".format(' '.join(formula)))
            return

        self.lookahead = self.formula[self.index]
                        

formula, production_rules, non_terminals = generateGrammar()
parser = Parser(formula, production_rules, non_terminals)
parser.parse()


# add dot to path
#c:\Program Files (x86)\Graphviz*\dot.exe on Windows
os.environ["PATH"] += ":"+"/usr/local/bin"
if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = "parse_tree"
UniqueDotExporter(parser.nodes['var1']).to_picture(file_name + ".png")
writeToLog("Parse Tree Created")



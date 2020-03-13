from anytree import Node
from anytree.dotexport import RenderTreeGraph
from anytree.exporter import UniqueDotExporter
import os
import re
import sys

# need graphviz installed

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
    writeToLog(file + '-Log:')
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                line = line.rstrip('\n')
                line = line.split(':')
                if len(line) > 2:
                    message = "Error: multiple colons found in line of input file"
                    writeToLog(message)
                    sys.exit()
                value = line[1]
                terms.append(line)
            else:
                terms[-1][1] = value + line
                value = terms[-1][1]
    # Check field names are present and valid
    V, C, P, E, CONN, Q, F = False, False, False, False, False, False, False  
    for term in terms:
        if term[0] == 'variables':
            V = True
            variables = term[1].split()
        if term[0] == 'constants':
            C = True
            constants = term[1].split()
        if term[0] == 'predicates':
            P = True
            predicates = term[1].split()
        if term[0] == 'equality':
            E = True
            equality = term[1].split()
        if term[0] == 'connectives':
            CONN = True
            connectives = term[1].split()
        if term[0] == 'quantifiers':
            Q = True
            quantifiers = term[1].split()
        if term[0] == 'formula':
            F = True
            formula = term[1].split()
    if not V or not C or not P or not E or not CONN or not Q or not F:
        writeToLog("Error invalid or missing field names")
        sys.exit()
    # Check predicates contain [int]
    for predicate in predicates:
        if not bool(re.search('\[\d+\]', predicate)):
            message = "Error: predicate {} does not contain [int]".format(predicate)
            writeToLog(message)
            sys.exit()

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

    # Check variables only contain letters, numbers and _
    for variable in variables:
        non_alpha = re.sub("\w+", "", variable)
        for char in non_alpha:
            if char not in ['_']:
                message = "Error: variable {} can only contain letters, numbers and underscores".format(variable)
                writeToLog(message)
                sys.exit()

    # Check constants only contain letters, numbers and _
    for constant in constants:
        non_alpha = re.sub("\w+", "", constant)
        for char in non_alpha:
            if char not in ['_']:
                message = "Error: constant {} can only contain letters, numbers and underscores".format(constant)
                writeToLog(message)
                sys.exit()
            
    # Check equality only contains letters, numbers, \, = and _
    non_alpha = re.sub("\w+", "", equality[0])
    for char in non_alpha:
        if char not in ['\\', '_', '=']:
            message = "Error: equality {} can only contain letters, numbers, _, \\ or =".format(equality[0])
            writeToLog(message)
            sys.exit()
            
    # Check connectives only contain letters, \, numbers and _
    for connective in connectives:
        non_alpha = re.sub("\w+", "", connective)
        for char in non_alpha:
            if char not in ['\\', '_']:
                message = "Error: connective {} can only contain letters, numbers, _ or \\".format(connective)
                writeToLog(message)
                sys.exit()
        
    non_terminals = ['<Start>', '<Quantifier>', '<Predicate>', '<Equality>', '<Constant>', '<Variable>', '<Connective>', '<Terminal>', '<Bracketed>']

    # Production rules for the CFG accounting for left factoring
    production_rules = {
        '<Start>' : ['<Predicate>', '(<Bracketed>', '<Quantifier><Variable><Start>', connectives[-1] + '<Start>'],
        '<Bracketed>': ['<Start><Connective><Start>)', '<Terminal><Equality><Terminal>)'],
        '<Equality>': equality,
        '<Terminal>': ['<Constant>, <Variable>'],
        '<Quantifier>': quantifiers,
        '<Variable>': variables,
        '<Constant>': constants,
        '<Predicate>': [],
        '<Connective>': connectives[:-1]
    }

    predicate_names = []
    predicate_symbol = []
    # Get names of predicate terminals and construct predicate syntax
    for predicate in predicates:
        idx = re.search(r"\[", predicate).start()
        idx1 = re.search(r"\]", predicate).end()
        name = predicate[0:idx]
        predicate_names.append(name + '()')
        predicate_symbol.append(name)
        num = int(predicate[idx+1:idx1-1])
        # check parameter number for predicate is positive
        if num <= 0:
            message = "Error: predicate must have positive number of parameters"
            writeToLog(message)
            sys.exit()
        atom = name + '(' + '<Variable>,' * (num-1) + '<Variable>' + ')'
        production_rules['<Predicate>'].append(atom)

    # check predicates only contain alphanumeric chars or _ chars
    for predicate in predicate_symbol:
        non_alpha = re.sub("\w+", "", predicate)
        for char in non_alpha:
            if char not in ['_']:
                message = "Error: predicate {} can only contain letters, numbers and underscores".format(predicate)
                writeToLog(message)
                sys.exit()
        
    # Check predicates, variables and constants do not have any names in common
    commonNames('variables', variables, 'constants', constants)

    commonNames('predicates', predicate_symbol, 'constants', constants)

    commonNames('predicates', predicate_symbol, 'variables', variables)

    commonNames('constants', constants, 'connectives', connectives)

    commonNames('variables', variables, 'connectives', connectives)
        
    commonNames('predicates', predicates, 'connectives', connectives)
    
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
    print('<Start> ->', '|'.join(production_rules['<Start>']))
    print('<Bracketed> ->', '|'.join(production_rules['<Bracketed>']))
    print('<Equality> ->', '|'.join(production_rules['<Equality>']))
    print('<Terminal> ->', '|'.join(production_rules['<Terminal>']))
    print('<Quantifier> ->', '|'.join(production_rules['<Quantifier>']))
    print('<Variable> ->', '|'.join(production_rules['<Variable>']))
    print('<Constant> ->', '|'.join(production_rules['<Constant>']))
    print('<Predicate> ->', '|'.join(production_rules['<Predicate>']))
    print('<Connective> ->', '|'.join(production_rules['<Connective>']))
    # write Context Free Grammar to file
    writeGrammar('Grammar For {}'.format(file))
    writeGrammar('Non Terminal Symbols: ' + ' '.join(non_terminals) + '\n')
    writeGrammar('Terminal Symbols: ' + ' '.join(equality + connectives + variables + constants + quantifiers + predicate_symbol + ['(', ')', ',']) + '\n')
    writeGrammar('Production Rules:')
    writeGrammar('<Start> -> ' + '|'.join(production_rules['<Start>']))
    writeGrammar('<Bracketed> -> ' + '|'.join(production_rules['<Bracketed>']))
    writeGrammar('<Equality> -> ' + '|'.join(production_rules['<Equality>']))
    writeGrammar('<Terminal> -> ' + '|'.join(production_rules['<Terminal>']))
    writeGrammar('<Quantifier> -> ' + '|'.join(production_rules['<Quantifier>']))
    writeGrammar('<Variable> -> ' + '|'.join(production_rules['<Variable>']))
    writeGrammar('<Constant> -> ' + '|'.join(production_rules['<Constant>']))
    writeGrammar('<Predicate> -> ' + '|'.join(production_rules['<Predicate>']))
    writeGrammar('<Connective> -> ' + '|'.join(production_rules['<Connective>']) + '\n')

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
        self.valid = False

    def start(self, parent=None):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Start>', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.predicate(parent):
            return True
        parent.children = []
        if self.lookahead == self.production_rules['<Start>'][-1][:-7]:
            self.match(production_rules['<Start>'][-1][:-7], parent)
            self.start(parent)
            return True
        parent.children = []
        if self.lookahead == '(':
            self.match('(', parent)
            self.bracketed(parent)
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
            sys.exit()

    def bracketed(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Bracketed>', parent)
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
        self.nodes['var' + str(self.counter)] = Node('<Equality>', parent)
        parent = self.nodes['var' + str(self.counter)]
        if self.lookahead == self.production_rules['<Equality>'][0]:
            self.match(self.production_rules['<Equality>'][0], parent)
            return True
        self.counter -= 1

    def variable(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Variable>', parent)
        parent = self.nodes['var' + str(self.counter)]
        for variable in self.production_rules['<Variable>']:
            if self.lookahead == variable:
                self.match(variable, parent)
                return True
        self.counter -= 1

    def predicate(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Predicate>', parent)
        parent = self.nodes['var' + str(self.counter)]
        for predicate in self.production_rules['<Predicate>']:
            if self.lookahead == predicate[:predicate.index('(')]:
                self.match(predicate[:predicate.index('(')], parent)
                self.match('(', parent)
                for i in range(predicate.count('<')-1):
                    self.variable(parent)
                    self.match(',', parent)
                self.variable(parent)
                self.match(')', parent)
                return True
        self.counter -= 1
        return False

    def term(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Terminal>', parent)
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
        self.nodes['var' + str(self.counter)] = Node('<Quantifier>', parent)
        parent = self.nodes['var' + str(self.counter)]
        for quantifier in self.production_rules['<Quantifier>']:
            if self.lookahead == quantifier:
                self.match(quantifier, parent)
                return True
        self.counter -= 1
        return False
    
    def constant(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Constant>', parent)
        parent = self.nodes['var' + str(self.counter)]
        for constant in self.production_rules['<Constant>']:
            if self.lookahead == constant:
                self.match(constant, parent)
                return True
        self.counter -= 1
        return False

    def connective(self, parent):
        self.counter += 1
        self.nodes['var' + str(self.counter)] = Node('<Connective>', parent)
        parent = self.nodes['var' + str(self.counter)]
        for connective in self.production_rules['<Connective>']:
            if self.lookahead == connective:
                self.match(connective, parent)
                return True
        self.counter -= 1
        return False

    def parse(self):
        try:
            self.lookahead = formula[self.index]
            self.start()
        except:
            message = "Syntax Error: Incomplete formula caused parser to exceed final term"
            writeToLog(message)
            sys.exit()

    def match(self, terminal, parent):
        self.counter += 1
        if self.lookahead == terminal:
            if terminal[0] == '\\':
                self.nodes['var' + str(self.counter)] = Node('\\' + terminal, parent)
            else:
                self.nodes['var' + str(self.counter)] = Node(terminal, parent)
            self.nextTerminal()
        else:
            print("Syntax Error")
            message = "Syntax Error: {} at position {} could not be parsed".format(self.lookahead, self.index)
            writeToLog(message)
            sys.exit()

    def nextTerminal(self):
        self.index += 1
        if self.index == self.length:
            self.valid = True
            return

        self.lookahead = self.formula[self.index]
                        

formula, production_rules, non_terminals = generateGrammar()
parser = Parser(formula, production_rules, non_terminals)
parser.parse()

# check no characters at end of formula after parsing ends
if parser.index < parser.length:
    writeToLog("Error: Additional characters found at the end of formula that were not matched in parsing")
    sys.exit()
elif parser.valid:
    writeToLog("Success: The Formula: {} is valid".format(' '.join(formula)))

if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = "parse_tree"
UniqueDotExporter(parser.nodes['var1']).to_picture(file_name + ".png")
writeToLog("Parse Tree Created")



# Compiler_Design

The parser.py file uses the os, re and sys standard python modules. In addition to these, the file also requires graphviz and the anytree library be installed.

After installing graphviz, the anytree package can be installed using the command `pip install anytree`.

The parser.py file will accept a file as a command line argument for example `python parser.py filename`.

The grammar for a formula is written to the grammar.txt file and any errors from parsing or grammar generation are stored in parser.log along with the result of the parsing. The parse tree for a given file is stored as a.png file with a name in the form filename.png.

## Error Checking
If Parsing fails, an error will be writtem to the log file, stating the position in the formula and the name of the character where parsing fails e.g. `Syntax Error: \land at position 29 could not be parsed`

During grammar generation, the input is verified before the grammar is generated. The program checks if variables, constants or predicates contain any invalid characters (not underscores, numbers or letters) and writes an error to the log file if it does e.g. `Error: constant <C can only contain letters, numbers and underscores`.

Checks are also made to ensure that predicates, constants, variables, equality and connectives do not share the same names e.g. `Error: variables and equality share the following names : {'w'}`

The program ensures that predicates contain square brackets and that the value inside the square brackets is an integer.

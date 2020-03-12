# Compiler_Design

The parser.py file uses the os, re and sys standard python modules. In addition to these, the file also requires graphviz and the anytree library be installed.

After installing graphviz, the anytree package can be installed using the command `pip install anytree`.

The parser.py file will accept a file as a command line argument for example `python parser.py filename`.

The grammar for a formula is written to the grammar.txt file and any errors from parsing or grammar generation are stored in parser.log along with the result of the parsing. The parse tree for a given file is stored as a.png file with a name in the form filename.png.

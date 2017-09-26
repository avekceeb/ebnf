
syntax = syntax rule, {syntax rule};
syntax rule = meta identifier, definitions list, ";" ;
definitions list = single definition, {"|", single definition} ;
single definition = term, {",", term};
term = factor, ["-", exception];
factor = {integer, "*"} , primary ;
exception = factor;
primary = optional sequence
	| repeated sequence
	| special sequence
	| grouped sequence
	| meta identifier
	| terminal string
	| empty ;
empty = ;
optional sequence = "[", definitions list, "]" ;
repeated sequence = "{", definitions list, "}" ;
grouped sequence = "(", definitions list, ")" ;
terminal string = "'" character - "'", { character - "'"}, "'"
	        | '"' character - '"', { charcter - '"'}, '"' ;
meta identifier = letter, {letter | decimal digit};
integer = decimal digit, {decimal digit} ;
decimal digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
character = letter | digit | symbol | "_" ;
letter = "A" | "B" | "C" | "D" | "E" | "F" | "G"
       | "H" | "I" | "J" | "K" | "L" | "M" | "N"
       | "O" | "P" | "Q" | "R" | "S" | "T" | "U"
       | "V" | "W" | "X" | "Y" | "Z" | "a" | "b"
       | "c" | "d" | "e" | "f" | "g" | "h" | "i"
       | "j" | "k" | "l" | "m" | "n" | "o" | "p"
       | "q" | "r" | "s" | "t" | "u" | "v" | "w"
       | "x" | "y" | "z" ;
symbol = "[" | "]" | "{" | "}" | "(" | ")" | "<" | ">"
       | "'" | '"' | "=" | "|" | "." | "," | ";" ;

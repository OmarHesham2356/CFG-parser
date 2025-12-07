# LR(1) Parser Implementation in Python

A complete, educational implementation of an LR(1) (Canonical LR) parser from scratch.

## Project Structure

```
├── grammar.py           # Core data structures
├── first_follow.py      # FIRST/FOLLOW set computation
├── lr1_items.py         # LR(1) item set construction
├── lr1_table.py         # Parsing table generation
├── lr1_parser.py        # Shift-reduce parser engine
└── main.py              # Example and test harness
```

## Module Descriptions

### `grammar.py`
Defines fundamental classes:
- **Production**: A grammar rule (LHS → RHS)
- **LR1Item**: An LR(1) item [A → α • β, lookahead]
- **Grammar**: Container for all productions and symbols
- **ParseTree**: Node in the final parse tree

### `first_follow.py`
Computes FIRST and FOLLOW sets:
- **FirstFollowComputer**: Implements fixed-point algorithms for computing FIRST and FOLLOW sets for all grammar symbols
- Key methods:
  - `compute_first_sets()`: Computes FIRST for all symbols
  - `compute_follow_sets()`: Computes FOLLOW for all nonterminals
  - `first_of_sequence()`: Helper to compute FIRST of a sequence

### `lr1_items.py`
Builds LR(1) item sets (states):
- **LR1ItemSetBuilder**: Constructs the complete state machine
- Key methods:
  - `closure()`: Computes closure of a set of LR(1) items
  - `goto()`: Computes GOTO(I, X) for an item set and symbol
  - `build()`: Generates all item sets and GOTO transitions
  - `print_item_sets()`: Debug output

### `lr1_table.py`
Generates ACTION and GOTO parsing tables:
- **LR1TableBuilder**: Fills in the parsing tables from item sets
- Key methods:
  - `build()`: Constructs ACTION and GOTO tables
  - `print_tables()`: Formatted output of parsing tables
- ACTION table entries: shift(n), reduce(n), accept
- GOTO table entries: state numbers

### `lr1_parser.py`
Implements the shift-reduce parser:
- **LR1Parser**: Executes parsing using the ACTION/GOTO tables
- Key methods:
  - `parse()`: Main parsing algorithm
  - `get_derivation_string()`: Formats derivation output
- Returns: parse tree, derivation steps, error message (if any)

## How to Use

### 1. Define a Grammar

```python
from grammar import Grammar, Production

productions = [
    Production("E", ["E", "+", "T"], 1),
    Production("E", ["T"], 2),
    Production("T", ["F"], 3),
    Production("F", ["id"], 4),
]

grammar = Grammar(productions, "E")  # "E" is start symbol
```

### 2. Compute FIRST and FOLLOW Sets

```python
from first_follow import FirstFollowComputer

ff = FirstFollowComputer(grammar)
ff.compute_first_sets()
ff.compute_follow_sets()
ff.print_sets()  # Debug output
```

### 3. Build Item Sets

```python
from lr1_items import LR1ItemSetBuilder

builder = LR1ItemSetBuilder(grammar, ff)
item_sets, goto_table = builder.build()
builder.print_item_sets()  # Debug output
```

### 4. Generate Parsing Tables

```python
from lr1_table import LR1TableBuilder

table_builder = LR1TableBuilder(grammar, item_sets, goto_table)
action_table, goto_table_filled = table_builder.build()
table_builder.print_tables()  # Debug output
```

### 5. Parse Input

```python
from lr1_parser import LR1Parser

parser = LR1Parser(grammar, action_table, goto_table_filled)

# Parse a sequence of tokens
tokens = ["id", "+", "id"]
parse_tree, derivation, error = parser.parse(tokens)

if not error:
    parse_tree.pretty_print()  # Display tree
    print(parser.get_derivation_string(derivation))
else:
    print(f"Parse error: {error}")
```

## Example Usage

Run the main example:
```bash
python main.py
```

This will:
1. Display the grammar
2. Show FIRST and FOLLOW sets
3. Print all LR(1) item sets
4. Display the parsing tables
5. Parse several test strings
6. Show parse trees and derivations

## Key Concepts

### LR(1) Item Format
`[A → α • β, a]`
- A: nonterminal
- α • β: production with dot position
- a: lookahead terminal

### Item Set Closure
For each item `[A → α • B β, a]` where B is nonterminal:
- Add all items `[B → • γ, b]` where b ∈ FIRST(β + a)

### GOTO Function
GOTO(I, X) = closure of all items in I with dot moved past X

### Parsing Actions
- **Shift**: Push token and state, advance input
- **Reduce**: Apply production, pop RHS, push LHS
- **Accept**: Input fully parsed, return success

## Grammar Requirements

- Must be a context-free grammar (CFG)
- No left recursion limitations (unlike LL parsers)
- Can handle most practical grammars
- Some grammars may have shift-reduce or reduce-reduce conflicts

## Example Grammar

```
Expression Grammar:
E → E + T | T
T → T * F | F  
F → ( E ) | id

Terminals: +, *, (, ), id
Nonterminals: E, T, F
Start symbol: E
```

This grammar handles:
- Operator precedence (* binds tighter than +)
- Left associativity
- Parenthesized expressions
- Identifiers

Example parse: `id + id * id`

```
        E
       /|\
      E + T
      |   |\
      T   T * F
      |   |   |
      F   F   id
      |   |
      id  id
```

## Debugging Tips

1. **Print FIRST/FOLLOW sets** to verify computation
2. **Print item sets** to check closure and GOTO
3. **Print parsing tables** to see shift/reduce/goto decisions
4. **Trace parse steps** manually for small examples
5. **Look for conflicts** (shift-reduce, reduce-reduce) in table output

## Performance

- Item set construction: O(|Grammar|² × |Lookaheads|)
- Table lookup: O(1)
- Parsing: O(n) where n is input length
- Overall quite efficient for compiler-sized grammars

## Educational Value

This implementation teaches:
- How parsers work "under the hood"
- FIRST/FOLLOW computation
- LR(1) item set construction
- Shift-reduce parsing mechanics
- Parse tree generation
- Derivation sequencing

## Limitations

- No error recovery
- Assumes tokens are pre-tokenized
- No semantic actions (attribute grammar support)
- Suitable for educational purposes, not production

## Next Steps

To extend this:
1. Add SLR(1) variant (uses global FOLLOW instead of lookahead)
2. Add LALR(1) variant (merges LR(1) states)
3. Implement semantic actions for code generation
4. Add lexical analyzer (tokenizer)
5. Support larger grammars efficiently

## References

- "Compilers: Principles, Techniques, and Tools" (Dragon Book)
- "Introduction to Compiler Design" (Appel)
- LR Parser Wikipedia: https://en.wikipedia.org/wiki/Canonical_LR_parser

---

Happy parsing!

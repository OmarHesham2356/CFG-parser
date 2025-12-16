# Idea Over View
___
## CFG Parser Basics
>A CFG parser takes a Context-Free Grammar (CFG) and a string, then checks if the string follows the grammar rules by building a parse tree and showing the derivation steps.

## LL vs LR Parsers
- **LL (Top-down)**: Scans left-to-right, builds tree from start symbol down using leftmost derivation. Predicts next rule early; can't handle left recursion easily.
- **LR (Bottom-up)**: Scans left-to-right, builds tree from string up using reverse rightmost derivation. Shifts tokens then reduces; handles more grammars, including left-recursive ones.

## Why Choose LR?
>LR parses a wider range of languages (all deterministic CFGs) with better error detection, no backtracking needed.

| Type             | Lookahead Power                                   | Table Size | Strength  | Simple Analogy [geeksforgeeks+2](https://www.geeksforgeeks.org/compiler-design/slr-clr-and-lalr-parsers-set-3/)​ |
| ---------------- | ------------------------------------------------- | ---------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| **LR(0)**        | None (blind)                                      | Tiny       | Weakest   | Decides reduce without peeking; crashes on ambiguity (e.g., can't handle many real grammars).                    |
| **SLR(1)**       | Basic (FOLLOW sets: "what can follow this rule?") | Small      | Low       | Peeks 1 token simply; fixes some LR(0) issues but fails complex cases.                                           |
| **LALR(1)**      | Good (merged LR(1) lookaheads)                    | Medium     | High      | Combines states for efficiency; powers Yacc/Bison tools; rare extra conflicts.                                   |
| **CLR(1)/LR(1)** | Full (precise lookahead per state)                | Largest    | Strongest | Handles **all** deterministic CFGs perfectly; no approximations.                                                 
>**Power order**: LR(0) ⊂ SLR(1) ⊂ LALR(1) ⊆ LR(1). Each adds smarter peeking to resolve shift/reduce conflicts.

## Why Choose LR(1)?

- **Max power**: Parses broadest grammars (e.g., left-recursive like expressions) without LALR's rare merge-conflicts.
- **Precision**: Exact decisions prevent errors; ideal for theory/projects needing full coverage.
- Tradeoff: Bigger tables, but worth it vs weaker types failing your CFG.

## How LR(1) Work?

For grammar :
			E → E + T | T
			T → id
Input: **id + id**

### Step 0: Augment Grammar

```text
Full Grammar (augmented):

0: S' ->  E        ($)
1: E  ->  E  +  T  ($, +)
2: E  ->  T        ($, +)
3: T  ->  id       ($, +)
```
>Add S' → E (new start, $ lookahead) to handle accept cleanly

### Step 1: Canonical LR(1) Item Sets

```text
I0: [S'→•E,$] [E→•E+T,$/+] [E→•T,$/+] [T→•id,$/+]
I1: [S'→E•,$]                           (accept)
I2: [E→E•+T,$]                          (after E in 1)
I3: [T→id•,$/+]                         (after id)
I4: [E→T•,$/+]                          (after T in 2)
I5: [E→E+•T,$] [T→•id,$]                (after + in 2)
I6: [E→E+T•,$]                          (after T in 1)
I7: [T→•id,$/+]                         (after T/id entry)
```

### Step 2: Parse Table (Action/Goto)

| State | id     | +      | E      | T      | $       |
| ----- | ------ | ------ | ------ | ------ | ------- |
| **0** | **s5** |        | **g1** | **g2** |         |
| **1** |        |        |        |        | **acc** |
| **2** |        | **s6** |        |        | **r2**  |
| **3** |        | **r3** |        |        | **r3**  |
| **4** | **s5** |        | **g7** |        |         |
| **5** |        |        |        |        | **r3**  |
| **6** |        |        |        |        | **r1**  |
| **7** |        | **s6** |        |        | **r2**  |
| **8** |        |        |        |        |         
>N=shift N, rN=reduce N, gN=goto N, acc=accept

### Step 3: Full Parse Execution

| Step | Stack            | Input     | Action           | Output (Deriv) |
| ---- | ---------------- | --------- | ---------------- | -------------- |
| 0    |                  | id + id $ | shift (s3)       |                |
| 1    | [0 id 3]         | + id $    | reduce 3 (T→id)  | T → id         |
| 2    | [0 T 2]          | + id $    | shift (s4)       | E → T          |
| 3    | [0 E 5]          | + id $    | shift (s6)       |                |
| 4    | [0 E 5 + 6]      | id $      | shift (s3)       |                |
| 5    | [0 E 5 + 6 id 3] | $         | reduce 3 (T→id)  | T → id         |
| 6    | [0 E 5 + 6 T 7]  | $         | reduce 1 (E→E+T) | E → E + T      |
| 7    | [0 E 8]          | $         | accept           | S' → E         |

______________________________________________________________________

# Code Over View (Backend)

_________________________________

## Phase1_Grammer
>Is the **"Grammar Foundation" module** – the base layer that turns raw grammar rules into structured, validated objects ready for LR(1) parsing.

```text
Production → Stores one rule: "E → E + T" (LHS, RHS list, ID) 
LR1Item → Parser state: "[E → E + • T, $]" (dot + lookahead) 
Grammar → Full grammar object + auto-augmentation (S' → E) 
ParseTreeNode → Tree node for final output visualization
```

### Production.py
>**`Production` class represents a single context-free grammar production rule (A → α) used as the foundation for LR(1) parser construction.**
>
>**Purpose**: Encapsulates grammar rules with validation, ε-production detection, and utilities for set operations, sorting, and debugging.

#### Function Summary Table:
| Method                        | Purpose                                 | Returns             |
| ----------------------------- | --------------------------------------- | ------------------- |
| `__init__(lhs, rhs, prod_id)` | Creates production rule with validation | `Production` object |
| `is_epsilon()`                | Checks if RHS is empty (ε-production)   | `bool`              |
| `__repr__()`                  | Pretty-prints rule (e.g. "E → E + T")   | `str`               |
| `__eq__(other)`               | Compares productions equal (ignores ID) | `bool`              |
| `__hash__()`                  | Hash for sets/dictionaries              | `int`               |
| `__lt__(other)`               | Sorts by LHS then production ID         | `bool`              |
>**Role**: Passed to `Grammar` class and used in all subsequent parser phases:
>(LR(1) items, states, tables).


### LR1Item.py
>**`LR1Item` class represents a single LR(1) parsing state: `[A → α - β, a]` where the dot (- ) shows parsing progress and `a` is the lookahead terminal.**
>
>**Purpose**: Core data structure for LR(1) automaton construction, closure computation, and parse table generation.

#### Function Summary Table
| Method                           | Purpose                                          | Returns          |
| -------------------------------- | ------------------------------------------------ | ---------------- |
| `__init__(prod, dot, lookahead)` | Creates LR(1) item with validation               | `LR1Item` object |
| `is_complete()`                  | Checks if dot is at RHS end (ready to reduce)    | `bool`           |
| `symbol_after_dot()`             | Returns symbol immediately after dot (or `None`) | `str` or `None`  |
| `__repr__()`                     | Pretty-prints: `"[E → E + - T, $]"`              | `str`            |
| `__eq__(other)`                  | Compares items equal (prod+dot+lookahead)        | `bool`           |
| `__hash__()`                     | Hash for sets/dictionaries                       | `int`            |
| `__lt__(other)`                  | Sorts by LHS, dot position, lookahead            | `bool`           |
>**Role**: Used in Phase 2 to build canonical collection of LR(1) states. Every state is a set of LR1Item objects. Essential for GOTO transitions and conflict detection.

### Grammar.py
>**`Grammar` class represents a complete context-free grammar with automatic augmentation, symbol classification, and validation for LR(1) parsing.**
>
>**Purpose**: Takes raw productions + start symbol, creates augmented grammar (S' → S), identifies terminals/nonterminals, and validates consistency.

#### Function Summary Table
| Method                                | Purpose                                   | Returns            |
| ------------------------------------- | ----------------------------------------- | ------------------ |
| `__init__(productions, start_symbol)` | Builds grammar + auto-augments S' → start | `Grammar` object   |
| `_extract_symbols()`                  | Finds all terminals vs nonterminals       | `None` (internal)  |
| `_validate()`                         | Checks undefined symbols + start symbol   | `None` (internal)  |
| `is_terminal(symbol)`                 | Checks if symbol is terminal              | `bool`             |
| `is_nonterminal(symbol)`              | Checks if symbol is nonterminal           | `bool`             |
| `is_augmented_start(symbol)`          | Checks if S' (augmented start)            | `bool`             |
| `get_productions_for(nonterminal)`    | Gets all productions for one nonterminal  | `List[Production]` |
| `__repr__()`                          | Pretty-prints all productions             | `str`              |
>**Role**: Central Phase 1 object passed to Phase 2. Provides `augmented_productions` for LR(1) item construction.

### ParseTreeNode.py
>**`ParseTreeNode` class represents a single node in the final parse tree output, used to visualize how the input string was derived from the grammar.**
>
>**Purpose**: Builds and pretty-prints the hierarchical parse tree during Phase 5 (parser execution), showing the derivation structure.

#### Function Summary Table
| Method                                   | Purpose                                                          | Returns                |
| ---------------------------------------- | ---------------------------------------------------------------- | ---------------------- |
| `__init__(symbol, children, production)` | Creates tree node (symbol + optional children + production used) | `ParseTreeNode` object |
| `is_leaf()`                              | Checks if node has no children (terminal/leaf)                   | `bool`                 |
| `is_terminal()`                          | Checks if node represents terminal (no production)               | `bool`                 |
| `get_tree_str(prefix, is_last, is_root)` | Pretty-prints tree with ASCII borders/lines                      | `str`                  |
| `__repr__()`                             | Compact representation: `(E (E id + id))`                        | `str`                  |
| `__str__()`                              | Same as `__repr__()`                                             | `str`                  |
>**Role**: Built during reduce actions (Phase 5). Final output shows complete parse tree + derivation for "id + id $".
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
### More Detailed Table
| Feature                                 | ****SLR(1) Parser (Simple LR)****             | ****CLR(1) Parser (Canonical LR)****                       | ****LALR(1) Parser (Look-Ahead LR)****                       |
| --------------------------------------- | --------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------ |
| Parsing Table Size                      | Smallest (fewer states)                       | Largest (most states)                                      | Medium (states merged to reduce size)                        |
| Grammar Handling                        | Limited (only simple grammars)                | Most powerful (handles almost all grammars)                | Nearly as powerful as CLR but compact                        |
| Basis for Decisions                     | Uses FOLLOW sets for reductions               | Uses look-ahead symbols to make precise decisions          | Uses merged look-ahead symbols, similar to CLR but optimized |
| Conflicts (Shift-Reduce, Reduce-Reduce) | More conflicts due to reliance on FOLLOW sets | Least conflicts because of look-ahead symbols              | May introduce reduce-reduce conflicts when merging states    |
| Error Detection                         | Delayed (errors detected later)               | Delayed (similar to SLR)                                   | Similar to CLR, not always immediate                         |
| Time and Space Complexity               | Low (fast but limited)                        | High (slow due to large tables but powerful)               | Medium (optimized for efficiency)                            |
| Ease of Implementation                  | Easiest (simplest to build)                   | Most complex (large tables make it harder)                 | Easier than CLR but slightly more complex than SLR           |
| Used In                                 | Simple parsers and educational tools          | Strong theoretical compilers (not widely used in practice) | Most real-world compilers (YACC, Bison, etc.)                |

>**Power order**: LR(0) ⊂ SLR(1) ⊂ LALR(1) ⊆ LR(1). Each adds smarter peeking to resolve shift/reduce conflicts.
>
>					![[Pasted image 20251216201809.png]]

## Why Choose LR(1)?

- **Max power**: Parses broadest grammars (e.g., left-recursive like expressions) without LALR's rare merge-conflicts.
- **Precision**: Exact decisions prevent errors; ideal for theory/projects needing full coverage.
- Tradeoff: Bigger tables, but worth it vs weaker types failing your CFG.

## How LR(1) Work?

For grammar :
			E → E + T | T
			T → id
Input: **id + id**

### Step 1: Augment Grammar

```text
0: S' ->  E
1: E  ->  E  +  T
2: E  ->  T
3: T  ->  id
```
>Add S' → E (new start, $ lookahead) to handle accept cleanly

### 2) FIRST and FOLLOW
```
- FIRST(T) = { `id` }
- FIRST(E) = { `id` }
- FOLLOW(E) = { `$`, `+` }
- FOLLOW(T) = { `$`, `+` }
```
>Justify lookaheads and reduce positions.

### 3) Canonical LR(1) item sets (shape)

```text
I0: 
	[S' → •E, $] 
	[E → •E + T, $] 
	[E → •T, $] 
	[T → •id, $]

I1: 
	[S' → E•, $]

I2: 
	[E → E• + T, $]

I3: 
	[E → T•, $] 
	[T → •id, $]

I4: 
	[T → id•, $]

I5: 
	[E → E + •T, $] 
	[T → •id, $] 

I6: 
	[E → E + T•, $]
```

GOTOs (conceptual):
- goto(0, E) = 1
- goto(0, T) = 3
- goto(0, id) = 4
- goto(2, '+') = 5
- goto(5, T) = 6
- goto(3, id) = 4

| State | E   | T   |
| ----- | --- | --- |
| 0     | 1   | 3   |
| 1     |     |     |
| 2     |     |     |
| 3     |     |     |
| 4     |     |     |
| 5     |     | 6   |
| 6     |     |     |

ACTION table
- In I0: `[T → - id, $]` → shift on `id` to state 4
- In I3: `[T → - id, $]` → shift on `id` to 4
- In I4: `[T → id- , $]` → reduce 3 (T→id) on `$` and `+` (from FOLLOW(T))
- In I3: `[E → T- , $]` → reduce 2 (E→T) on `$` and `+`
- In I2: `[E → E- + T, $]` → shift on `+` to 5
- In I6: `[E → E + T- , $]` → reduce 1 (E→E+T) on `$` and `+`
- In I1: `[S' → E- , $]` → accept on `$`

| State | id  | +   | $   |
| ----- | --- | --- | --- |
| 0     | s4  |     |     |
| 1     |     |     | acc |
| 2     |     | s5  | r2  |
| 3     | s4  | r2  | r2  |
| 4     |     | r3  | r3  |
| 5     | s4  |     |     |
| 6     |     | r1  | r1  |

Parse Table (Action/Goto)

| State | E   | T   | id  | +   | $   |
| ----- | --- | --- | --- | --- | --- |
| **0** | g1  | g3  | s4  |     |     |
| **1** |     |     |     |     | acc |
| **2** |     |     |     | s5  | r2  |
| **3** |     |     | s4  | r2  | r2  |
| **4** |     |     |     | r3  | r3  |
| **5** |     | 6   | s4  |     |     |
| **6** |     |     |     | r1  | r1  |

>N=shift N, rN=reduce N, gN=goto N, acc=accept

Explanation of a couple rows:
- **State 0**: only item with terminal after dot: `T→- id,$` → `id` gives shift 4.
- **State 4**: item `T→id- ,$` is complete; FOLLOW(T) = `$,+` → reduce 3 on `$` and `+`.
- **State 1**: item `[S'→E- ,$]` → accept on `$`.
- **State 6**: complete `E→E+T` → reduce 1 on `$` and `+`.
(This table is consistent with the usual bottom‑up parse for `E→E+T|T`.)

### Step 3: Full Parse Execution

| Step | Stack            | Input     | Action    |
| ---- | ---------------- | --------- | --------- |
| 0    |                  | id + id $ | s4        |
| 1    | [0,id,4]         | + id $    | r3: T→id  |
| 2    | [0,T,3]          | + id $    | r2: E→T   |
| 3    | [0,E,2]          | + id $    | s5 (on +) |
| 4    | [0,E,2,+,5]      | id $      | s4        |
| 5    | [0,E,2,+,5,id,4] | $         | r3: T→id  |
| 6    | [0,E,2,+,5,T,6]  | $         | r1: E→E+T |
| 7    | [0,E,2]          | $         | acc       |
_________________
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

--------------
## Phase2_First_Follow
>Is the **“set calculator” phase**: it takes the `Grammar` from phase 1 and computes all FIRST and FOLLOW sets for its symbols. These sets are later used to build LR(1) items and parse tables (lookaheads when deciding reductions).

### FirstFollowComputer.py
**Class `FirstFollowComputer` computes and stores:**
- **FIRST(X)** for every terminal, nonterminal, and sequence
- **FOLLOW(A)** for every nonterminal

>It uses the standard fixed‑point algorithms from compiler theory, starting from the augmented grammar (with S' and `$`) and iterating until no sets change. These sets are then used when building LR(1) items and when computing lookaheads in the parse table.
#### Function Summary Table
| Method                                 | What it does                                                                                                                           | Returns                             |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| `__init__(grammar, auto_compute=True)` | Saves the grammar, creates empty FIRST/FOLLOW sets for all symbols, and (optionally) immediately computes them.                        | `FirstFollowComputer` object        |
| `compute_first_sets(verbose=False)`    | Runs the iterative algorithm to fill FIRST sets for all symbols using the standard rules (terminals, ε-productions, and sequences).    | `None` (updates `self.first_sets`)  |
| `first_of_symbol(symbol)`              | Internal helper: returns a copy of `FIRST(symbol)` from `self.first_sets`.                                                             | `Set[str]`                          |
| `first_of_sequence(symbols)`           | Computes `FIRST(X₁X₂…Xₙ)` for a list of symbols, correctly propagating ε through the sequence.                                         | `Set[str]`                          |
| `compute_follow_sets(verbose=False)`   | Runs the iterative algorithm to fill FOLLOW sets for all nonterminals using the standard rules (start symbol gets `$`, A → αBβ, etc.). | `None` (updates `self.follow_sets`) |
| `first_of(symbol)`                     | Public wrapper to get `FIRST(symbol)` (just calls `first_of_symbol`).                                                                  | `Set[str]`                          |
| `follow_of(nonterminal)`               | Public method to get `FOLLOW(nonterminal)` from `self.follow_sets`.                                                                    | `Set[str]`                          |
| `print_sets()`                         | Nicely prints all FIRST and FOLLOW sets in a formatted way for debugging/report output.                                                | `None`                              |
#### Mini-Example
```python
Phase 1: Build grammar
prods = [
    Production("E", ["E", "+", "T"], prod_id=1),
    Production("E", ["T"],          prod_id=2),
    Production("T", ["id"],         prod_id=3),
]
grammar = Grammar(prods, start_symbol="E")   # adds S' → E, discovers terminals/nonterminals
```

```python
ff = FirstFollowComputer(grammar, auto_compute=True)  # FIRST and FOLLOW computed
print(ff.first_of("E"))      # → {'id'}
print(ff.follow_of("E"))     # → {'$', '+'}
print(ff.follow_of("T"))     # → {'$', '+'}
ff.print_sets()              # pretty view of all sets

```

__________________________________________________
## Phase3_LR1ItemSets
>Is the **"LR(1) automaton builder" module** – the layer that turns your Phase 1 grammar and Phase 2 FIRST/FOLLOW sets into LR(1) item sets (states) and GOTO transitions, ready to become parse tables later.

It **depends on**:
- Phase 1: `Grammar`, `Production`, `LR1Item`
- Phase 2: `FirstFollowComputer` (FIRST/FOLLOW used inside closure)

```text
Grammar          → Provides augmented productions, terminals, nonterminals
FirstFollow      → Provides FIRST/FOLLOW for computing lookaheads
LR1Item          → One LR(1) item: "[A → α • β, a]"
LR1ItemSetBuilder → Builds all LR(1) item sets and GOTO graph
```

### LR1ItemSetBuilder.py
> **`LR1ItemSetBuilder` builds the canonical collection of LR(1) item sets and the GOTO transitions between them (the LR(1) DFA).**
> 
> **Purpose**: Starting from the augmented start production, repeatedly apply `closure` and `goto` to discover all parser states. These states are later used to build the ACTION/GOTO parse table.

**Relation to previous phases**:
- Uses **Phase 1** `Grammar` to iterate over productions and know which symbols are terminals/nonterminals.
- Uses **Phase 1** `LR1Item` to represent each item in a state.
- Uses **Phase 2** `FirstFollowComputer` to compute lookahead symbols inside `closure` (via FIRST of sequences).
#### Function Summary Table
| Method / Function                    | Purpose                                                                                          | Relation to previous phases                                    | Returns               |
| ------------------------------------ | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- | --------------------- |
| `__init__(grammar, first_follow)`    | Stores `Grammar` and `FirstFollowComputer`, sets up internal lists/dicts for states and edges.   | Needs Phase 1 `Grammar`, Phase 2 `FirstFollowComputer`.        | `LR1ItemSetBuilder`   |
| `initial_item_set()` / `build_start` | Creates initial item set `{ [S' → - S, $] }` and applies `closure` to get state I0.              | Uses augmented start `S'` from `Grammar`, `LR1Item` for items. | Set of `LR1Item`      |
| `closure(items)`                     | Given a set of items, adds items for nonterminals after the dot with correct lookaheads, repeat. | Uses `Grammar.get_productions_for(A)` and FIRST from Phase 2.  | Set of `LR1Item`      |
| `goto(items, symbol)`                | From state `I` and symbol `X`, moves dot over `X` and applies `closure` → next state.            | Uses `LR1Item.symbol_after_dot()` and `closure()`.             | Set of `LR1Item`      |
| `build_canonical_collection()`       | Repeatedly applies `goto` from every state on every symbol until no new states appear.           | Uses `initial_item_set`, `closure`, `goto`; builds DFA graph.  | (states, transitions) |
| `get_states()` / property `states`   | Returns list of all LR(1) item sets (I0, I1, …).                                                 | States are sets of Phase 1 `LR1Item`.                          | `List[Set[LR1Item]]`  |
| `get_transitions()` / `transitions`  | Returns mapping (state_index, symbol) → next_state_index.                                        | Used later to build ACTION/GOTO tables.                        | `Dict` / similar      |
>**Role**: Central Phase 3 object. It connects the **theory (FIRST/FOLLOW)** to **practical parser states**, and its output is the direct input for the parse-table-building phase.

____________
## Phase4_LR1_Table
> Is the **“table builder” module** – it turns Phase 3’s LR(1) item sets and GOTO graph into the actual **ACTION/GOTO parse table**, plus structured actions and conflict info.

It **depends on**:
- Phase 1: `Grammar`, `Production`, `LR1Item`
- Phase 3: `LR1ItemSetBuilder` output (states + goto transitions)
- Phase 2 indirectly (because LR(1) items already contain correct lookaheads)

```
LR1ItemSetBuilder → gives states (I0..In) and goto(i, X)
LR1TableBuilder  → converts those into ACTION[i, a] and GOTO[i, A]
ParseAction      → represents each cell (shift/reduce/accept/error)
ConflictInfo     → records any conflicts while filling table
```

### LR1TableBuilder.py
> **`LR1TableBuilder` constructs the LR(1) ACTION and GOTO tables from the LR(1) item sets and transitions.**
> 
> **Purpose**: For each state and each terminal/nonterminal, it decides: shift, reduce, accept, goto, or error, and detects conflicts.

#### Function Summary Table
|Method / Function|Purpose|Relation to previous phases|Returns|
|---|---|---|---|
|`__init__(grammar, item_set_builder)`|Stores `Grammar` + `LR1ItemSetBuilder`, initializes empty ACTION/GOTO tables and conflicts.|Uses Phase 1 `Grammar`, Phase 3 states + goto transitions.|`LR1TableBuilder`|
|`_init_tables()`|Creates table skeletons: rows for each state, columns for all terminals/nonterminals.|Uses `grammar.terminals` / `grammar.nonterminals`.|`None`|
|`_add_shift_actions()` / inline logic|For each state i, for each `[A → α - a β, t]` with terminal `a`, sets `ACTION[i,a] = shift j`.|Uses LR(1) items from Phase 3 and `goto(i, a)` from item_set_builder.|`None`|
|`_add_reduce_actions()` / inline logic|For each complete item `[A → α - , a]`, sets `ACTION[i,a] = reduce A→α` when A ≠ S'.|Uses LR(1) items, `Production` objects from Phase 1.|`None`|
|`_add_accept_action()`|For `[S' → S - , $]`, sets `ACTION[i,$] = accept`.|Uses augmented start from `Grammar`.|`None`|
|`_add_goto_entries()`|For each nonterminal A, if `goto(i, A) = j`, sets `GOTO[i,A] = j`.|Uses goto graph from `LR1ItemSetBuilder`.|`None`|
|`_record_conflict(...)`|When a cell already has an action, records shift/reduce or reduce/reduce conflict.|Uses `ConflictInfo` class (see below).|`None`|
|`build()`|High-level: calls all steps above in order; returns final ACTION/GOTO + conflict list.|Consumes all previous-phase outputs; used by executor in Phase 5.|`(action_table, goto_table)`|
|`pretty_print()`|Prints the ACTION and GOTO tables in readable form.|For debugging/reporting.|`None`|
>**Role**: This is the final “static” product before actual parsing. Phase 5 only reads ACTION/GOTO to drive the stack machine.

### ParseAction.py
> **`ParseAction` represents one cell in the ACTION table: shift to state, reduce by rule, accept, or error.**

#### Function Table
| Member / Method                                 | Purpose                                       | Returns         |
| ----------------------------------------------- | --------------------------------------------- | --------------- |
| `kind` (e.g. 'shift','reduce','accept','error') | Describes the type of action                  | `str`           |
| `target_state` / `state`                        | For 'shift': which state to go to             | `int` or `None` |
| `production`                                    | For 'reduce': which `Production` to reduce by | `Production`    |
| `__repr__()` / `__str__()`                      | Human-readable like `s3`, `r2`, `acc`, `err`  | `str`           |
>**Role**: Table entries aren’t raw strings; they are structured objects the parser engine will interpret.

### ConflictInfo.py
> **`ConflictInfo` stores details about conflicts found when building the LR(1) table (shift/reduce or reduce/reduce).**

#### Function Summary Table
| Field / Method    | Purpose                                 | Returns       |
| ----------------- | --------------------------------------- | ------------- |
| `state`           | In which LR state the conflict occurred | `int`         |
| `symbol`          | On which input symbol (column)          | `str`         |
| `existing_action` | The action already in the cell          | `ParseAction` |
| `new_action`      | The new conflicting action              | `ParseAction` |
| `__repr__()`      | Text description of the conflict        | `str`         |
> **Role**: Lets you report or debug ambiguities in the grammar or construction.

_____________
## Phase5_LR1_Parser
> Is the **“runtime engine” module** – it takes the ACTION/GOTO tables from Phase 4 and actually parses an input token stream, building a parse tree or throwing a parse error.

It **depends on**:
- Phase 1: `Grammar`, `Production`, `ParseTreeNode`
- Phase 4: `action_table`, `goto_table`, `ParseAction`
- Its own error type: `ParseError`

```
Grammar      → knows productions (for reduces)
ParseTreeNode→ builds parse tree nodes during reduces
LR1Table     → tells the parser what to shift/reduce/accept
LR1Parser    → runs the stack machine over tokens
ParseError   → describes errors when no valid action exists
```

### LR1Parser.py
> **`LR1Parser` executes the LR(1) parsing algorithm using the precomputed tables, producing a parse tree or raising a parse error.**
> 
> **Purpose**: Implements the classic bottom‑up LR(1) stack machine: maintains a state stack and a parse‑tree stack, reads tokens, and for each step consults ACTION/GOTO to shift or reduce.

#### Function Table
|Method / Member|Purpose|Relation to previous phases|Returns|
|---|---|---|---|
|`__init__(grammar, action, goto)`|Stores `Grammar`, ACTION table, GOTO table, and prepares internal stacks.|Needs Phase 1 `Grammar`, Phase 4 tables.|`LR1Parser`|
|`parse(tokens)`|Main entry: runs the LR(1) loop over input tokens, returns parse tree root on success or raises `ParseError`.|Uses `ParseAction` kinds; uses `ParseTreeNode` on reduce.|`ParseTreeNode`|
|`_current_state()`|Reads top of state stack.|Internal helper.|`int`|
|`_next_action(lookahead)`|Looks up `ACTION[state][lookahead]`.|Uses Phase 4 ACTION table.|`ParseAction`|
|`_shift(action, lookahead)`|Pushes new state from `action.state` and creates terminal tree node.|Uses GOTO indirectly; uses `ParseTreeNode`.|`None`|
|`_reduce(action)`|Pops|rhs|symbols/states, creates a `ParseTreeNode` for the LHS, and pushes GOTO on LHS.|
|`_accept()`|Called when `ParseAction` is accept; returns root node.|Uses final tree stack state.|`ParseTreeNode`|
|`_error(message, position, ...)`|Raises `ParseError` with context (state, symbol, maybe expected set).|Uses `ParseError` class.|`No return (exception)`|
>**Role**: This is the final step that “runs” the parser you built. All the previous phases exist just to feed this machine.

## ParseError.py
> **`ParseError` is a custom exception representing a parsing failure.**

#### Function Table
| Field / Method | Purpose                                                  | Returns    |
| -------------- | -------------------------------------------------------- | ---------- |
| `message`      | Human‑readable error message                             | `str`      |
| `position`     | Where in the token stream the error occurred (if stored) | e.g. `int` |
| `state`        | Parser state when error occurred (optional)              | `int`      |
| `__str__()`    | Pretty-prints the error                                  | `str`      
> **Role**: Makes errors understandable when no valid ACTION entry exists (cell is empty or error).

______________

## Main

## LR1ParserBuilder.py – Overall Role
> **`LR1ParserBuilder` is the main orchestrator that wires all 5 phases together and returns a ready‑to‑use `LR1Parser` from a list of productions and a start symbol.**

It **depends on**:
- Phase 1: `Production`, `Grammar`
- Phase 2: `FirstFollowComputer`
- Phase 3: `LR1ItemSetBuilder`
- Phase 4: `LR1TableBuilder`
- Phase 5: `LR1Parser`
#### Function Table
| Method / Function                     | Purpose                                                               | Uses which phases?                | Returns               |
| ------------------------------------- | --------------------------------------------------------------------- | --------------------------------- | --------------------- |
| `__init__(productions, start_symbol)` | Stores raw productions + start symbol.                                | Phase 1 data (`Production` list). | `LR1ParserBuilder`    |
| `_build_grammar()`                    | Creates `Grammar` (auto adds S' → S).                                 | Phase 1 `Grammar`.                | `Grammar`             |
| `_build_first_follow(grammar)`        | Builds `FirstFollowComputer` for the grammar.                         | Phase 2.                          | `FirstFollowComputer` |
| `_build_item_sets(grammar, ff)`       | Builds LR(1) item sets and goto graph via `LR1ItemSetBuilder`.        | Phase 3.                          | `LR1ItemSetBuilder`   |
| `_build_tables(grammar, item_sets)`   | Uses `LR1TableBuilder` to create ACTION/GOTO tables.                  | Phase 4.                          | `(action, goto)`      |
| `build_parser()`                      | Calls all steps in order, then constructs and returns an `LR1Parser`. | Combines Phases 1–5.              | `LR1Parser`           |
|                                       |                                                                       |                                   |                       |
> **Role**: This is what you would call from a “main program” to get a parser in one line.
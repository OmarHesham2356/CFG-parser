

## Phase 1 – Core grammar structures

### `Production.py`

Represents a single grammar rule \(A → α\).

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Production:
    lhs: str              # Left-hand side nonterminal, e.g. "E"
    rhs: List[str]        # Right-hand side symbols, [] means epsilon
    prod_id: int | None = None

    def is_epsilon(self) -> bool:
        return len(self.rhs) == 0

    def __str__(self) -> str:
        rhs_str = " ".join(self.rhs) if self.rhs else "ε"
        return f"{self.lhs} → {rhs_str}"
```

Used everywhere to identify reductions and build derivations.[1]

***

### `LR1Item.py`

Represents one LR(1) item \([A → α -  β, a]\).

```python
from dataclasses import dataclass
from typing import Optional
from .Production import Production

@dataclass(frozen=True)
class LR1Item:
    prod: Production      # Underlying production A → αβ
    dot: int              # Dot position in rhs: 0..len(rhs)
    lookahead: str        # Lookahead terminal or END_OF_INPUT

    def is_complete(self) -> bool:
        return self.dot >= len(self.prod.rhs)

    def symbol_after_dot(self) -> Optional[str]:
        if self.is_complete():
            return None
        return self.prod.rhs[self.dot]

    def __str__(self) -> str:
        rhs = list(self.prod.rhs)
        rhs.insert(self.dot, "•")
        rhs_str = " ".join(rhs) if rhs else "•"
        return f"[{self.prod.lhs} → {rhs}, {self.lookahead}]"
```

Phase 3 groups these into LR(1) states.[2]

***

### `Grammar.py`

Holds all productions plus the augmented start rule.

```python
from typing import List, Dict, Set
from .Production import Production

END_OF_INPUT = "$"

class Grammar:
    def __init__(self, productions: List[Production], start_symbol: str):
        self.productions = productions
        self.start_symbol = start_symbol

        # Collect nonterminals and terminals
        self.nonterminals: Set[str] = {p.lhs for p in productions}
        rhs_symbols = {sym for p in productions for sym in p.rhs}
        self.terminals: Set[str] = rhs_symbols - self.nonterminals

        # Augmented start S' → S
        self.augmented_start = f"{self.start_symbol}'"
        self.augmented_productions: List[Production] = [
            Production(self.augmented_start, [self.start_symbol], prod_id=0),
            *productions,
        ]

    def is_nonterminal(self, sym: str) -> bool:
        return sym in self.nonterminals or sym == self.augmented_start

    def is_terminal(self, sym: str) -> bool:
        return sym in self.terminals

    def get_productions_for(self, lhs: str) -> List[Production]:
        return [p for p in self.productions if p.lhs == lhs]
```

This is the single source of truth for the grammar across all phases.

***

### `ParseTreeNode.py`

Represents nodes in the resulting parse tree.

```python
from dataclasses import dataclass, field
from typing import List, Optional
from .Production import Production

@dataclass
class ParseTreeNode:
    symbol: str
    children: List["ParseTreeNode"] = field(default_factory=list)
    production: Optional[Production] = None  # for nonterminals

    def add_child(self, child: "ParseTreeNode") -> None:
        self.children.append(child)

    def pretty_print(self, indent: int = 0) -> None:
        print("  " * indent + self.symbol)
        for child in self.children:
            child.pretty_print(indent + 1)
```

Phase 5 builds these nodes during reductions.[3]

***

### `phase1/__init__.py`

Public API for phase 1.

```python
from .Grammar import Grammar, END_OF_INPUT
from .Production import Production
from .LR1Item import LR1Item
from .ParseTreeNode import ParseTreeNode

__all__ = ["Grammar", "END_OF_INPUT", "Production", "LR1Item", "ParseTreeNode"]
```

***

## Phase 2 – FIRST and FOLLOW

### `FirstFollowComputer.py`

Computes \(FIRST\) and \(FOLLOW\) sets for the grammar.

```python
from typing import Dict, Set, List
from phase1 import Grammar, END_OF_INPUT

class FirstFollowComputer:
    def __init__(self, grammar: Grammar, auto_compute: bool = True):
        self.grammar = grammar
        self.first: Dict[str, Set[str]] = {}
        self.follow: Dict[str, Set[str]] = {}
        if auto_compute:
            self.compute_first()
            self.compute_follow()

    def compute_first(self) -> None:
        # Fixed-point FIRST computation over all productions
        ...

    def compute_follow(self) -> None:
        # Fixed-point FOLLOW computation using FIRST results
        ...

    def first_of_symbol(self, sym: str) -> Set[str]:
        return self.first.get(sym, set())

    def first_of_sequence(self, seq: List[str]) -> Set[str]:
        # FIRST over sequences (handles epsilon via FIRST and nullability)
        ...

    def follow_of(self, nonterminal: str) -> Set[str]:
        return self.follow.get(nonterminal, set())
```

Phase 3 uses `first_of_sequence` to compute LR(1) lookaheads.[4]

***

### `phase2/__init__.py`

```python
from .FirstFollowComputer import FirstFollowComputer

__all__ = ["FirstFollowComputer"]
```

***

## Phase 3 – LR(1) item sets

### `LR1ItemSetBuilder.py`

Builds the canonical collection of LR(1) item sets and the goto graph.

```python
from typing import List, Dict, Set, Tuple
from phase1 import Grammar, LR1Item, END_OF_INPUT
from phase2 import FirstFollowComputer

class LR1ItemSetBuilder:
    def __init__(self, grammar: Grammar, ff: FirstFollowComputer):
        self.grammar = grammar
        self.ff = ff
        self.item_sets: List[Set[LR1Item]] = []
        self.goto_table: Dict[Tuple[int, str], int] = {}

    def closure(self, items: Set[LR1Item]) -> Set[LR1Item]:
        changed = True
        closure_set = set(items)
        while changed:
            changed = False
            for item in list(closure_set):
                B = item.symbol_after_dot()
                if B is None or not self.grammar.is_nonterminal(B):
                    continue
                beta = item.prod.rhs[item.dot + 1 :]
                beta_lookahead = beta + [item.lookahead]
                first = self.ff.first_of_sequence(beta_lookahead)
                for prod in self.grammar.get_productions_for(B):
                    for a in first:
                        new_item = LR1Item(prod, 0, a)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            changed = True
        return closure_set

    def goto(self, items: Set[LR1Item], symbol: str) -> Set[LR1Item]:
        moved = {
            LR1Item(item.prod, item.dot + 1, item.lookahead)
            for item in items
            if item.symbol_after_dot() == symbol
        }
        return self.closure(moved) if moved else set()

    def build(self) -> tuple[list[Set[LR1Item]], Dict[Tuple[int, str], int]]:
        # I0 = closure({ [S' → • S, $] })
        start_prod = self.grammar.augmented_productions[0]
        start_item = LR1Item(start_prod, 0, END_OF_INPUT)
        I0 = frozenset(self.closure({start_item}))

        item_sets: List[frozenset[LR1Item]] = [I0]
        self.item_sets = [set(I0)]
        queue = [0]

        while queue:
            i = queue.pop(0)
            I = item_sets[i]
            symbols = {it.symbol_after_dot() for it in I if it.symbol_after_dot() is not None}
            for X in symbols:
                J = frozenset(self.goto(set(I), X))
                if not J:
                    continue
                if J not in item_sets:
                    item_sets.append(J)
                    self.item_sets.append(set(J))
                    j = len(item_sets) - 1
                    queue.append(j)
                else:
                    j = item_sets.index(J)
                self.goto_table[(i, X)] = j

        return self.item_sets, self.goto_table
```

This is the automaton Phase 4 turns into tables.

***

### `phase3/__init__.py`

```python
from .LR1ItemSetBuilder import LR1ItemSetBuilder

__all__ = ["LR1ItemSetBuilder"]
```

***

## Phase 4 – ACTION / GOTO tables

### `ParseAction.py`

Single entry in the ACTION table.

```python
from dataclasses import dataclass
from typing import Optional
from phase1 import Production

@dataclass
class ParseAction:
    action_type: str                   # 'shift', 'reduce', 'accept', 'error'
    state: Optional[int] = None        # for 'shift'
    production: Optional[Production] = None  # for 'reduce'

    def __repr__(self) -> str:
        if self.action_type == "shift":
            return f"s{self.state}"
        elif self.action_type == "reduce":
            return f"r{self.production.prod_id}"
        elif self.action_type == "accept":
            return "acc"
        else:
            return "err"
```

Used by the parser to decide what to do on `(state, token)`.[5]

***

### `ConflictInfo.py`

Describes a parsing table conflict.

```python
from dataclasses import dataclass
from .ParseAction import ParseAction

@dataclass
class ConflictInfo:
    state: int
    symbol: str
    conflict_type: str          # 'shift-reduce' or 'reduce-reduce', etc.
    action1: ParseAction
    action2: ParseAction
    description: str = ""

    def __repr__(self) -> str:
        return (f"Conflict in state {self.state} on '{self.symbol}': "
                f"{self.conflict_type} ({self.action1} vs {self.action2})")
```

`LR1TableBuilder` collects these instead of silently overwriting entries.[6]

***

### `LR1TableBuilder.py`

Builds ACTION and GOTO from item sets.

```python
from typing import Dict, List, Tuple
from phase1 import Grammar, LR1Item, END_OF_INPUT
from .ParseAction import ParseAction
from .ConflictInfo import ConflictInfo

class LR1TableBuilder:
    def __init__(self, grammar: Grammar, item_sets: List, goto_table: Dict):
        self.grammar = grammar
        self.item_sets = item_sets
        self.goto_table = goto_table

        self.action_table: Dict[Tuple[int, str], ParseAction] = {}
        self.goto_filled: Dict[Tuple[int, str], int] = {}
        self.conflicts: List[ConflictInfo] = []

    def build(self):
        for state_id, items in enumerate(self.item_sets):
            self._process_state(state_id, items)
        self.goto_filled = self.goto_table.copy()
        return self.action_table, self.goto_filled

    def _process_state(self, state_id: int, items):
        for item in items:
            symbol_after_dot = item.symbol_after_dot()
            if symbol_after_dot is None:
                self._handle_reduce_item(state_id, item)
            elif self.grammar.is_terminal(symbol_after_dot):
                self._handle_shift_item(state_id, item, symbol_after_dot)
```

`_handle_shift_item` and `_handle_reduce_item` fill entries and push `ConflictInfo` when an entry already exists.[7]

Simple usage:

```python
builder = LR1TableBuilder(grammar, item_sets, goto_table)
action_table, goto_table = builder.build()
builder.print_tables()
builder.print_conflicts()
```

***

### `phase4/__init__.py`

```python
from .ParseAction import ParseAction
from .ConflictInfo import ConflictInfo
from .LR1TableBuilder import LR1TableBuilder

__all__ = ["ParseAction", "ConflictInfo", "LR1TableBuilder"]
```

***

## Phase 5 – LR(1) parser engine

### `ParseError.py`

Exception for parse failures.

```python
from dataclasses import dataclass

@dataclass
class ParseError(Exception):
    state: int
    token: str
    message: str

    def __str__(self) -> str:
        return f"Parse error in state {self.state} on token '{self.token}': {self.message}"
```

Thrown when `ACTION[state, token]` is missing or incompatible.[8]

***

### `LR1Parser.py`

Runs the table‑driven shift/reduce algorithm and builds a parse tree.

```python
from typing import List, Tuple
from phase1 import Grammar, ParseTreeNode, END_OF_INPUT
from phase4 import ParseAction
from .ParseError import ParseError

class LR1Parser:
    def __init__(self, grammar: Grammar, action_table, goto_table, verbose: bool = False):
        self.grammar = grammar
        self.action_table = action_table
        self.goto_table = goto_table
        self.verbose = verbose

    def parse(self, tokens: List[str]) -> ParseTreeNode:
        tokens = tokens + [END_OF_INPUT]
        state_stack = [0]
        node_stack: List[ParseTreeNode] = []
        pos = 0

        while True:
            state = state_stack[-1]
            token = tokens[pos]
            action = self.action_table.get((state, token))

            if self.verbose:
                print(f"Step: state={state}, token='{token}'")
                print("  Stack:", state_stack)

            if action is None or action.action_type == "error":
                raise ParseError(state, token, "Unexpected token")

            if action.action_type == "shift":
                node_stack.append(ParseTreeNode(token))
                state_stack.append(action.state)
                pos += 1

            elif action.action_type == "reduce":
                prod = action.production
                k = len(prod.rhs)
                children = node_stack[-k:] if k > 0 else []
                del node_stack[-k:]
                del state_stack[-k:]

                new_node = ParseTreeNode(prod.lhs, children, prod)
                node_stack.append(new_node)

                goto_state = self.goto_table[(state_stack[-1], prod.lhs)]
                state_stack.append(goto_state)

            elif action.action_type == "accept":
                return node_stack[0]
```

***

### `phase5/__init__.py`

```python
from .LR1Parser import LR1Parser
from .ParseError import ParseError

__all__ = ["LR1Parser", "ParseError"]
```

***

## How it all fits together (example snippet)

You can add a short “pipeline” example to your README:

```python
from phase1 import Grammar, Production
from phase2 import FirstFollowComputer
from phase3 import LR1ItemSetBuilder
from phase4 import LR1TableBuilder
from phase5 import LR1Parser

# 1. Define grammar
prods = [
    Production("E", ["E", "+", "T"], 1),
    Production("E", ["T"], 2),
    Production("T", ["id"], 3),
]
g = Grammar(prods, "E")

# 2. FIRST / FOLLOW
ff = FirstFollowComputer(g)

# 3. LR(1) item sets
item_builder = LR1ItemSetBuilder(g, ff)
item_sets, goto_graph = item_builder.build()

# 4. ACTION / GOTO tables
table_builder = LR1TableBuilder(g, item_sets, goto_graph)
action, goto = table_builder.build()

# 5. Parse
parser = LR1Parser(g, action, goto, verbose=True)
tree = parser.parse(["id"])
tree.pretty_print()
```


[5](https://en.wikipedia.org/wiki/LR_parser)
[6](https://serokell.io/blog/how-to-implement-lr1-parser)
[7](https://en.wikipedia.org/wiki/Canonical_LR_parser)
[8](https://web.eecs.umich.edu/~weimerw/2009-4610/lectures/weimer-4610-09.pdf)

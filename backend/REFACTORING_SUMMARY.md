# CFG-Parser Code Refactoring Summary

This document outlines the refactored project structure where each class is now in its own file, organized within phase-specific folders.

## New Directory Structure

```
backend/
├── phase1_grammar/
│   ├── __init__.py
│   ├── Production.py
│   ├── LR1Item.py
│   ├── Grammar.py
│   └── ParseTreeNode.py
│
├── phase2_first_follow/
│   ├── __init__.py
│   └── FirstFollowComputer.py
│
├── phase3_lr1_items/
│   ├── __init__.py
│   └── LR1ItemSetBuilder.py
│
├── phase4_lr1_table/
│   ├── __init__.py
│   ├── ParseAction.py
│   ├── ConflictInfo.py
│   └── LR1TableBuilder.py
│
├── phase5_lr1_parser/
│   ├── __init__.py
│   ├── ParseError.py
│   └── LR1Parser.py
│
├── main/
│   ├── __init__.py
│   └── LR1ParserBuilder.py
│
└── (old files: main.py, phase*.py are now in folders)
```

## Phase 1: Grammar (phase1_grammar/)

### Classes and Files:
- **Production.py** - Grammar production rule (LHS -> RHS)
- **LR1Item.py** - LR(1) item [A → α • β, lookahead]
- **Grammar.py** - Context-Free Grammar representation
- **ParseTreeNode.py** - Node in a parse tree

### Constants:
- EPSILON = "ε"
- END_OF_INPUT = "$"

## Phase 2: First/Follow Sets (phase2_first_follow/)

### Classes and Files:
- **FirstFollowComputer.py** - Computes FIRST and FOLLOW sets

## Phase 3: Item Sets (phase3_lr1_items/)

### Classes and Files:
- **LR1ItemSetBuilder.py** - Builds LR(1) item sets and state machine

## Phase 4: Parsing Tables (phase4_lr1_table/)

### Classes and Files:
- **ParseAction.py** - A parsing action in the ACTION table
- **ConflictInfo.py** - Information about parsing conflicts
- **LR1TableBuilder.py** - Builds ACTION and GOTO tables

## Phase 5: Parser Engine (phase5_lr1_parser/)

### Classes and Files:
- **ParseError.py** - Custom exception for parsing errors
- **LR1Parser.py** - LR(1) shift-reduce parser engine

## Main Module (main/)

### Classes and Files:
- **LR1ParserBuilder.py** - Convenience class to build complete parser
  - Helper functions:
    - get_grammar_from_user()
    - get_start_symbol_from_user()
    - get_test_cases_from_user()
    - get_verbose_choice()

## Import Changes

The module structure now supports clean imports. Each package's `__init__.py` file exports the public classes:

```python
# Example: Importing from phase1_grammar
from phase1_grammar import Production, Grammar, LR1Item, ParseTreeNode, EPSILON, END_OF_INPUT

# Example: Importing from phase2_first_follow
from phase2_first_follow import FirstFollowComputer

# Example: Importing from phase4_lr1_table
from phase4_lr1_table import ParseAction, ConflictInfo, LR1TableBuilder
```

## Benefits of Refactoring

1. **Better Organization** - Each class is isolated in its own file
2. **Easier Maintenance** - Changes to a class are localized to its file
3. **Improved Readability** - Smaller files are easier to understand
4. **Cleaner Dependencies** - Import statements are more explicit
5. **Better Testing** - Individual classes can be tested in isolation
6. **Scalability** - Easy to add new classes or features within each phase

## Running the Program

The main entry point remains the same:

```bash
python main/LR1ParserBuilder.py
```

Or if you need to run with the package structure:

```bash
python -m main.LR1ParserBuilder
```

## Notes

- Old phase files (main.py, phase1_grammar.py, etc.) can be safely deleted
- All imports within the codebase should be updated to use the new package structure
- The `__init__.py` files handle re-exporting public classes for convenience imports

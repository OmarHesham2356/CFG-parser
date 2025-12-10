# ============================================================================
# Phase 1: Core Data Structures for LR(1) Parser
# ============================================================================

from typing import List, Set, Tuple, Optional

# Epsilon constant for clearer code
EPSILON = "ε"
END_OF_INPUT = "$"

class Production:
    """
    Grammar production rule: LHS -> RHS
    
    Example:
        Production("E", ["E", "+", "T"], prod_id=1)
        Production("E", [], prod_id=2)  # epsilon production
    """
    
    def __init__(self, lhs: str, rhs: List[str], prod_id: Optional[int] = None):
        """
        Args:
            lhs: Left-hand side (nonterminal)
            rhs: Right-hand side (list of symbols, empty for epsilon)
            prod_id: Unique production identifier
        """
        if not isinstance(lhs, str) or not lhs:
            raise ValueError("LHS must be a non-empty string")
        if not isinstance(rhs, list):
            raise ValueError("RHS must be a list of symbols")
        
        self.lhs = lhs
        self.rhs = rhs
        self.prod_id = prod_id
    
    def is_epsilon(self) -> bool:
        """Check if this is an epsilon production"""
        return len(self.rhs) == 0
    
    def __repr__(self) -> str:
        """String representation: A -> a b c | ε"""
        rhs_str = ' '.join(self.rhs) if self.rhs else EPSILON
        return f"{self.lhs} → {rhs_str}"
    
    def __eq__(self, other) -> bool:
        """Production equality (ignoring prod_id)"""
        if not isinstance(other, Production):
            return False
        return self.lhs == other.lhs and self.rhs == other.rhs
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        return hash((self.lhs, tuple(self.rhs)))
    
    def __lt__(self, other) -> bool:
        """For sorting productions"""
        if self.lhs != other.lhs:
            return self.lhs < other.lhs
        return self.prod_id < other.prod_id if self.prod_id and other.prod_id else False


class LR1Item:
    """
    LR(1) item: [A → α • β, lookahead]
    
    Represents parsing state:
    - The dot (•) position in the production
    - The lookahead symbol (terminal or $)
    
    Example:
        [E → E + • T, +]  means we've parsed "E +" and expect something that can be T
    """
    
    def __init__(self, prod: Production, dot: int, lookahead: str):
        """
        Args:
            prod: The production rule
            dot: Position of dot in RHS (0 to len(RHS))
            lookahead: Terminal symbol or $ (must be single symbol)
        """
        if not isinstance(prod, Production):
            raise ValueError("prod must be a Production object")
        if not (0 <= dot <= len(prod.rhs)):
            raise ValueError(f"Dot position {dot} out of range [0, {len(prod.rhs)}]")
        if not isinstance(lookahead, str) or not lookahead:
            raise ValueError("Lookahead must be a non-empty string")
        
        self.prod = prod
        self.dot = dot
        self.lookahead = lookahead
    
    def is_complete(self) -> bool:
        """Check if dot is at end of RHS (item is ready to reduce)"""
        return self.dot >= len(self.prod.rhs)
    
    def symbol_after_dot(self) -> Optional[str]:
        """Get symbol immediately after the dot (None if at end)"""
        if self.dot < len(self.prod.rhs):
            return self.prod.rhs[self.dot]
        return None
    
    def symbol_after_dot_pos(self, offset: int = 1) -> Optional[str]:
        """Get symbol at offset positions after the dot"""
        pos = self.dot + offset
        if pos < len(self.prod.rhs):
            return self.prod.rhs[pos]
        return None
    
    def __repr__(self) -> str:
        """String representation: [A → α • β, a]"""
        rhs = list(self.prod.rhs)
        rhs.insert(self.dot, '•')
        rhs_str = ' '.join(rhs) if rhs else EPSILON
        return f"[{self.prod.lhs} → {rhs_str}, {self.lookahead}]"
    
    def __eq__(self, other) -> bool:
        """Item equality"""
        if not isinstance(other, LR1Item):
            return False
        return (self.prod == other.prod and 
                self.dot == other.dot and 
                self.lookahead == other.lookahead)
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        return hash((self.prod, self.dot, self.lookahead))
    
    def __lt__(self, other) -> bool:
        """For sorting items in output"""
        if self.prod.lhs != other.prod.lhs:
            return self.prod.lhs < other.prod.lhs
        if self.dot != other.dot:
            return self.dot < other.dot
        return self.lookahead < other.lookahead


class Grammar:
    """
    Context-Free Grammar (CFG) representation
    
    Includes:
    - Original productions
    - Augmented production: S' → S (for LR(1) parsing)
    - Terminal and nonterminal symbol sets
    - Validation of grammar consistency
    """
    
    def __init__(self, productions: List[Production], start_symbol: str):
        """
        Args:
            productions: List of Production objects
            start_symbol: The start nonterminal (e.g., "E")
            
        Raises:
            ValueError: If grammar is invalid
        """
        if not isinstance(productions, list) or not productions:
            raise ValueError("Must have at least one production")
        if not isinstance(start_symbol, str) or not start_symbol:
            raise ValueError("Start symbol must be non-empty string")
        
        self.productions = productions
        self.start_symbol = start_symbol
        
        # Extract terminals and nonterminals
        self.terminals: Set[str] = set()
        self.nonterminals: Set[str] = set()
        self._extract_symbols()
        
        # Augmented grammar: S' → S
        self.augmented_start = "S'"
        augmented_prod = Production(self.augmented_start, [start_symbol], prod_id=0)
        self.augmented_productions = [augmented_prod] + productions
        
        # IMPORTANT: Add augmented start to nonterminals (FIXED BUG!)
        self.nonterminals.add(self.augmented_start)
        
        # Validate grammar
        self._validate()
    
    def _extract_symbols(self):
        """Extract terminals and nonterminals from productions"""
        # Nonterminals: left-hand sides of productions
        for prod in self.productions:
            self.nonterminals.add(prod.lhs)
        
        # Terminals: symbols in RHS that aren't nonterminals
        for prod in self.productions:
            for symbol in prod.rhs:
                if symbol not in self.nonterminals:
                    self.terminals.add(symbol)
        
        # Add END_OF_INPUT as a terminal
        self.terminals.add(END_OF_INPUT)
    
    def _validate(self):
        """Validate grammar consistency"""
        # Check that all referenced symbols are defined
        for prod in self.productions:
            for symbol in prod.rhs:
                if symbol not in self.terminals and symbol not in self.nonterminals:
                    raise ValueError(
                        f"Undefined symbol '{symbol}' in production {prod}"
                    )
        
        # Check that start symbol is a nonterminal
        if self.start_symbol not in self.nonterminals:
            raise ValueError(
                f"Start symbol '{self.start_symbol}' must be a nonterminal"
            )
    
    def is_terminal(self, symbol: str) -> bool:
        """Check if symbol is a terminal"""
        return symbol in self.terminals
    
    def is_nonterminal(self, symbol: str) -> bool:
        """Check if symbol is a nonterminal"""
        return symbol in self.nonterminals
    
    def is_augmented_start(self, symbol: str) -> bool:
        """Check if symbol is the augmented start symbol S'"""
        return symbol == self.augmented_start
    
    def get_productions_for(self, nonterminal: str) -> List[Production]:
        """Get all productions with given LHS"""
        return [p for p in self.productions if p.lhs == nonterminal]
    
    def __repr__(self) -> str:
        """String representation of grammar"""
        result = "Grammar:\n"
        for i, prod in enumerate(self.productions):
            result += f"  {i}: {prod}\n"
        return result
    
    def __str__(self) -> str:
        return self.__repr__()


class ParseTreeNode:
    """
    Node in a parse tree
    
    Example tree for "id + id":
        E
        ├─ E
        │  └─ T
        │     └─ F
        │        └─ id
        ├─ +
        └─ T
           └─ F
              └─ id
    """
    
    def __init__(self, symbol: str, children: Optional[List['ParseTreeNode']] = None, 
                 production: Optional[Production] = None):
        """
        Args:
            symbol: Terminal or nonterminal symbol
            children: Child nodes (None for leaf terminals)
            production: The production used to expand this node (None for terminals)
        """
        self.symbol = symbol
        self.children = children if children is not None else []
        self.production = production  # Which production was used to create this node
    
    def is_leaf(self) -> bool:
        """Check if this is a terminal (leaf) node"""
        return len(self.children) == 0
    
    def is_terminal(self) -> bool:
        """Check if this is a terminal node"""
        return self.production is None
    
    def height(self) -> int:
        """Get height of subtree"""
        if self.is_leaf():
            return 1
        return 1 + max((c.height() for c in self.children), default=0)
    
    def pretty_print(self, indent: int = 0):
        """Pretty print the parse tree"""
        prefix = "  " * indent
        print(prefix + str(self.symbol))
        for child in self.children:
            child.pretty_print(indent + 1)
    
    def __repr__(self) -> str:
        """Compact representation"""
        if self.is_leaf():
            return str(self.symbol)
        children_str = ' '.join(str(c) for c in self.children)
        return f"({self.symbol} {children_str})"
    
    def __str__(self) -> str:
        return self.__repr__()


# # ============================================================================
# # Example usage and validation
# # ============================================================================

# if __name__ == "__main__":
#     print("Testing Grammar Data Structures")
#     print("=" * 60)
    
#     # Create example grammar: E → E + T | T
#     #                        T → T * F | F
#     #                        F → ( E ) | id
    
#     productions = [
#         Production("E", ["E", "+", "T"], prod_id=1),
#         Production("E", ["T"], prod_id=2),
#         Production("T", ["T", "*", "F"], prod_id=3),
#         Production("T", ["F"], prod_id=4),
#         Production("F", ["(", "E", ")"], prod_id=5),
#         Production("F", ["id"], prod_id=6),
#     ]
    
#     grammar = Grammar(productions, "E")
#     print(grammar)
    
#     print(f"Terminals: {sorted(grammar.terminals)}")
#     print(f"Nonterminals: {sorted(grammar.nonterminals)}")
#     print(f"Augmented start: {grammar.augmented_start}")
#     print(f"Augmented productions: {len(grammar.augmented_productions)} total")
    
#     # Test LR1Item
#     print("\nTesting LR1Item")
#     print("-" * 60)
#     prod = productions[0]  # E → E + T
#     item = LR1Item(prod, 1, "+")
#     print(f"Item: {item}")
#     print(f"Is complete: {item.is_complete()}")
#     print(f"Symbol after dot: {item.symbol_after_dot()}")
    
#     # Test ParseTreeNode
#     print("\nTesting ParseTreeNode")
#     print("-" * 60)
#     # Build a small tree
#     leaf1 = ParseTreeNode("id")
#     leaf2 = ParseTreeNode("id")
#     f_node = ParseTreeNode("F", [leaf1], productions[5])
#     t_node = ParseTreeNode("T", [f_node], productions[3])
    
#     print("Parse tree for: id")
#     t_node.pretty_print()

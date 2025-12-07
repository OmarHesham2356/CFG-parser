# Data Structures for Grammar and Parsing

class Production:
    """Represents a grammar production rule: LHS -> RHS"""
    def __init__(self, lhs, rhs, prod_id=None):
        self.lhs = lhs              # Left-hand side (nonterminal)
        self.rhs = rhs              # Right-hand side (list of symbols)
        self.prod_id = prod_id      # Production index
    
    def __repr__(self):
        rhs_str = ' '.join(self.rhs) if self.rhs else 'ε'
        return f"{self.lhs} → {rhs_str}"
    
    def __eq__(self, other):
        return self.lhs == other.lhs and self.rhs == other.rhs
    
    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))


class LR1Item:
    """LR(1) item: [Production, dot_position, lookahead]"""
    def __init__(self, prod, dot, lookahead):
        self.prod = prod            # Production object
        self.dot = dot              # Position of dot in RHS (0 to len(RHS))
        self.lookahead = lookahead  # Specific lookahead terminal
    
    def __repr__(self):
        rhs = list(self.prod.rhs)
        rhs.insert(self.dot, '•')
        return f"[{self.prod.lhs} → {' '.join(rhs)}, {self.lookahead}]"
    
    def __eq__(self, other):
        return (self.prod == other.prod and 
                self.dot == other.dot and 
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        return hash((self.prod, self.dot, self.lookahead))
    
    def is_complete(self):
        """Check if dot is at end of RHS"""
        return self.dot >= len(self.prod.rhs)
    
    def symbol_after_dot(self):
        """Get symbol after dot (None if at end)"""
        if self.dot < len(self.prod.rhs):
            return self.prod.rhs[self.dot]
        return None


class Grammar:
    """Context-Free Grammar representation"""
    def __init__(self, productions, start_symbol):
        self.productions = productions  # List of Production objects
        self.start_symbol = start_symbol
        
        # Extract terminals and nonterminals
        self.terminals = set()
        self.nonterminals = set()
        self._extract_symbols()
        
        # Augment grammar: S' -> S
        self.augmented_start = "S'"
        augmented_prod = Production(self.augmented_start, [start_symbol], 0)
        self.augmented_productions = [augmented_prod] + productions
    
    def _extract_symbols(self):
        """Extract terminals and nonterminals from productions"""
        for prod in self.productions:
            self.nonterminals.add(prod.lhs)
            for sym in prod.rhs:
                if sym not in self.nonterminals:
                    self.terminals.add(sym)
    
    def is_terminal(self, symbol):
        return symbol in self.terminals
    
    def is_nonterminal(self, symbol):
        return symbol in self.nonterminals
    
    def __repr__(self):
        result = "Grammar:\n"
        for i, prod in enumerate(self.productions):
            result += f"  {i}: {prod}\n"
        return result


class ParseTree:
    """Node in a parse tree"""
    def __init__(self, symbol, children=None):
        self.symbol = symbol       # Terminal or nonterminal
        self.children = children if children else []
    
    def is_leaf(self):
        return len(self.children) == 0
    
    def pretty_print(self, indent=0):
        """Print tree nicely"""
        print("  " * indent + str(self.symbol))
        for child in self.children:
            child.pretty_print(indent + 1)
    
    def __repr__(self):
        if self.is_leaf():
            return str(self.symbol)
        return f"({self.symbol} {' '.join(str(c) for c in self.children)})"

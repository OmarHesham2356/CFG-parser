from typing import List, Set
from .Production import Production, EPSILON

END_OF_INPUT = "$"


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

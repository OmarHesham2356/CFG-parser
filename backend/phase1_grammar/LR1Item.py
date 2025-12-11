from typing import Optional
from .Production import Production, EPSILON


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

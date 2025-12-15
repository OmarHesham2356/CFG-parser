from typing import List, Optional

# Epsilon constant for clearer code
EPSILON = "ε"


class Production:
    """
    Example:
        Production("E", ["E", "+", "T"], prod_id=1)
        Production("E", [], prod_id=2)  # epsilon production
    """
    # lhs: nonterminal name as a string, e.g. "E".
    # rhs: list of symbols (strings), e.g. ["E", "+", "T"]; an empty list represents ε.
    # prod_id: optional numeric identifier (used in tables/debug).
    def __init__(self, lhs: str, rhs: List[str], prod_id: Optional[int] = None):
        if not isinstance(lhs, str) or not lhs:
            raise ValueError("LHS must be a non-empty string")
        if not isinstance(rhs, list):
            raise ValueError("RHS must be a list of symbols")
        
        self.lhs = lhs
        self.rhs = rhs
        self.prod_id = prod_id


    # returns True if rhs is empty (ε‑production).
    def is_epsilon(self) -> bool:
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

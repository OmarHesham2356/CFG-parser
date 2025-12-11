from dataclasses import dataclass
from .ParseAction import ParseAction


@dataclass
class ConflictInfo:
    """Information about a parsing conflict."""
    
    state: int
    symbol: str
    conflict_type: str  # 'shift-reduce' or 'reduce-reduce'
    action1: ParseAction
    action2: ParseAction
    description: str = ""
    
    def __repr__(self) -> str:
        return (f"Conflict in state {self.state} on '{self.symbol}': "
                f"{self.conflict_type} ({self.action1} vs {self.action2})")

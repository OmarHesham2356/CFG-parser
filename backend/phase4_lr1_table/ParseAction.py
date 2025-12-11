from typing import Optional
from dataclasses import dataclass
from phase1_grammar import Production


@dataclass
class ParseAction:
    """A parsing action in the ACTION table."""
    
    action_type: str  # 'shift', 'reduce', 'accept', 'error'
    state: Optional[int] = None  # For shift: next state
    production: Optional[Production] = None  # For reduce: which production
    
    def __repr__(self) -> str:
        if self.action_type == 'shift':
            return f"s{self.state}"
        elif self.action_type == 'reduce':
            return f"r{self.production.prod_id}"
        elif self.action_type == 'accept':
            return 'acc'
        else:
            return 'err'

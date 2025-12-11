from typing import List, Optional


class ParseError(Exception):
    """Custom exception for parsing errors."""
    
    def __init__(self, message: str, state: Optional[int] = None, 
                 token: Optional[str] = None, expected: Optional[List[str]] = None):
        self.message = message
        self.state = state
        self.token = token
        self.expected = expected or []
        
        full_msg = message
        if state is not None:
            full_msg += f" (in state {state})"
        if token is not None:
            full_msg += f" (on token '{token}')"
        if expected:
            full_msg += f" (expected: {', '.join(sorted(expected))})"
        
        super().__init__(full_msg)

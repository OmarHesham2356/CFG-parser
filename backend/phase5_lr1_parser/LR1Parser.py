from typing import List, Tuple, Dict, Optional
from phase1_grammar import Production, Grammar, ParseTreeNode, END_OF_INPUT, EPSILON
from phase4_lr1_table import ParseAction
from .ParseError import ParseError


class LR1Parser:
    """
    LR(1) shift-reduce parser.
    
    The main loop:
    1. Peek at top state on stack and current input token
    2. Look up action in ACTION table
    3. SHIFT: push token and new state, advance input
    4. REDUCE: pop RHS, push LHS, look up GOTO state
    5. ACCEPT: success
    6. ERROR: syntax error
    """
    
    def __init__(self, grammar: Grammar, action_table: Dict, goto_table: Dict,
                 verbose: bool = False):
        """
        Args:
            grammar: The augmented grammar
            action_table: ACTION table (state, terminal) -> ParseAction
            goto_table: GOTO table (state, nonterminal) -> state
            verbose: Print execution trace if True
        """
        self.grammar = grammar
        self.action_table = action_table
        self.goto_table = goto_table
        self.verbose = verbose
    
    def parse(self, tokens: List[str]) -> Tuple[Optional[ParseTreeNode], List[str], Optional[str]]:
        """
        Parse input tokens.
        
        Args:
            tokens: List of terminal symbols to parse
            
        Returns:
            (parse_tree, derivation, error)
            - parse_tree: Root of parse tree if successful, None otherwise
            - derivation: List of derivation steps (strings)
            - error: Error message if parsing failed, None if successful
        """
        # Validate input
        error = self._validate_input(tokens)
        if error:
            return None, [], error
        
        # Add end-of-input marker
        tokens = list(tokens) + [END_OF_INPUT]
        
        # Initialize
        state_stack = [0]  # Start in state 0
        symbol_stack: List[str] = []  # Track symbols
        tree_stack: List[ParseTreeNode] = []  # Parse tree nodes
        token_index = 0
        derivation: List[str] = []
        
        if self.verbose:
            print("\nStarting parse...")
            print(f"Input: {' '.join(tokens)}")
        
        # Main parse loop
        while True:
            current_state = state_stack[-1]
            current_token = tokens[token_index]
            
            if self.verbose:
                print(f"\nStep: state={current_state}, token='{current_token}'")
                print(f"  Stack: {state_stack}, {symbol_stack}")
            
            # Look up action
            key = (current_state, current_token)
            action = self.action_table.get(key)
            
            if action is None:
                # No valid action: syntax error
                expected = self._find_expected_tokens(current_state)
                return None, derivation, ParseError(
                    f"Unexpected token '{current_token}'",
                    state=current_state,
                    token=current_token,
                    expected=expected
                ).message
            
            # Execute action
            if action.action_type == 'shift':
                # SHIFT: push token and new state
                error = self._do_shift(
                    action, tokens[token_index], token_index,
                    state_stack, symbol_stack, tree_stack
                )
                if error:
                    return None, derivation, error
                
                token_index += 1
                
                if self.verbose:
                    print(f"  → shift {action.state}")
            
            elif action.action_type == 'reduce':
                # REDUCE: apply production
                error = self._do_reduce(
                    action, state_stack, symbol_stack, tree_stack, derivation
                )
                if error:
                    return None, derivation, error
                
                # After reduce, look up GOTO
                new_state = state_stack[-1]  # Top state after popping
                lhs = action.production.lhs
                goto_key = (new_state, lhs)
                
                if goto_key not in self.goto_table:
                    return None, derivation, f"GOTO[{new_state}, {lhs}] not found"
                
                goto_state = self.goto_table[goto_key]
                state_stack.append(goto_state)
                symbol_stack.append(lhs)
                
                if self.verbose:
                    print(f"  → reduce {action.production}")
                    print(f"  → GOTO({new_state}, {lhs}) = {goto_state}")
            
            elif action.action_type == 'accept':
                # ACCEPT: success!
                if len(tree_stack) != 1:
                    return None, derivation, \
                        f"Tree stack should have 1 tree, got {len(tree_stack)}"
                
                root = tree_stack[0]
                
                if self.verbose:
                    print(f"  → accept")
                    print(f"\nParsing successful!")
                
                return root, derivation, None
            
            else:
                # Unknown action type
                return None, derivation, f"Unknown action type: {action.action_type}"
    
    def _validate_input(self, tokens: List[str]) -> Optional[str]:
        """Validate input tokens before parsing."""
        
        if not isinstance(tokens, list):
            return "Input must be a list of tokens"
        
        if not tokens:
            return "Input cannot be empty"
        
        for i, token in enumerate(tokens):
            if not isinstance(token, str):
                return f"Token {i} is not a string: {repr(token)}"
            
            if not token:
                return f"Token {i} is an empty string"
            
            if token == END_OF_INPUT:
                return f"Token {i} cannot be END_OF_INPUT '{END_OF_INPUT}'"
        
        return None
    
    def _do_shift(self, action: ParseAction, token: str, token_index: int,
                  state_stack: List[int], symbol_stack: List[str],
                  tree_stack: List[ParseTreeNode]) -> Optional[str]:
        """Execute a SHIFT action."""
        
        # Push symbol
        symbol_stack.append(token)
        
        # Push next state
        state_stack.append(action.state)
        
        # Push leaf node for terminal
        leaf = ParseTreeNode(token)
        tree_stack.append(leaf)
        
        return None
    
    def _do_reduce(self, action: ParseAction, state_stack: List[int],
                   symbol_stack: List[str], tree_stack: List[ParseTreeNode],
                   derivation: List[str]) -> Optional[str]:
        """Execute a REDUCE action."""
        
        production = action.production
        rhs_len = len(production.rhs)
        
        # Validation: stack must have enough states and symbols
        if len(state_stack) < 1:
            return f"State stack underflow: only {len(state_stack)} states"
        
        if len(symbol_stack) < rhs_len:
            return f"Symbol stack underflow: need {rhs_len} symbols, have {len(symbol_stack)}"
        
        if len(tree_stack) < rhs_len:
            return f"Tree stack underflow: need {rhs_len} trees, have {len(tree_stack)}"
        
        # Pop RHS symbols and their states
        # Stack structure: [state0, symbol1, state1, symbol2, state2, ...]
        # When reducing, pop 2*rhs_len entries
        for _ in range(rhs_len):
            state_stack.pop()  # Pop state after symbol
            if symbol_stack:
                symbol_stack.pop()  # Pop symbol
        
        # Pop children from tree stack
        children = []
        for _ in range(rhs_len):
            if tree_stack:
                children.insert(0, tree_stack.pop())
        
        # Build new parse tree node for this nonterminal
        node = ParseTreeNode(production.lhs, children, production)
        tree_stack.append(node)
        
        # Track derivation
        rhs_str = ' '.join(production.rhs) if production.rhs else EPSILON
        derivation.append(f"{production.lhs} → {rhs_str}")
        
        return None
    
    def _find_expected_tokens(self, state: int) -> List[str]:
        """Find which tokens are valid in this state."""
        
        expected = []
        for (s, token), action in self.action_table.items():
            if s == state and action.action_type in ['shift', 'reduce', 'accept']:
                expected.append(token)
        
        return sorted(set(expected))

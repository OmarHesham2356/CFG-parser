# LR(1) Parser Engine

from grammar import ParseTree

class LR1Parser:
    """Shift-Reduce LR(1) Parser"""
    
    def __init__(self, grammar, action_table, goto_table):
        self.grammar = grammar
        self.action_table = action_table
        self.goto_table = goto_table
    
    def parse(self, tokens):
        """
        Parse a sequence of tokens.
        Returns: (parse_tree, derivation, error_message)
        """
        # Add end-of-input marker
        tokens = list(tokens) + ['$']
        
        stack = [0]              # State stack
        pos = 0
        tree_stack = []          # Parse tree construction
        derivation = []          # Record of reduce steps
        
        while True:
            state = stack[-1]
            token = tokens[pos]
            
            # Get action from table
            action = self.action_table[state].get(token)
            
            if action is None:
                error = f"Syntax error: state {state}, token '{token}'"
                return None, derivation, error
            
            action_type = action[0]
            
            if action_type == 'shift':
                # SHIFT: push token and new state
                next_state = action[1]
                stack.append(token)
                stack.append(next_state)
                tree_stack.append(ParseTree(token))  # Leaf node
                pos += 1
            
            elif action_type == 'reduce':
                # REDUCE: apply production
                prod_id = action[1]
                prod = self.grammar.augmented_productions[prod_id]
                
                # Record derivation
                derivation.append(f"Reduce by: {prod}")
                
                # Pop 2 * |RHS| items from state stack (symbols and states)
                for _ in range(len(prod.rhs)):
                    if stack:
                        stack.pop()  # pop symbol
                    if stack:
                        stack.pop()  # pop state
                
                # Pop children from tree stack and build subtree
                children = []
                for _ in range(len(prod.rhs)):
                    if tree_stack:
                        children.insert(0, tree_stack.pop())
                
                # Create parent node
                parent = ParseTree(prod.lhs, children)
                tree_stack.append(parent)
                
                # Get current state and use GOTO
                top_state = stack[-1] if stack else 0
                goto_state = self.goto_table[top_state].get(prod.lhs)
                
                if goto_state is None:
                    error = f"GOTO error: state {top_state}, symbol {prod.lhs}"
                    return None, derivation, error
                
                stack.append(prod.lhs)
                stack.append(goto_state)
            
            elif action_type == 'accept':
                # ACCEPT: parse succeeded
                if tree_stack:
                    parse_tree = tree_stack[0]
                    return parse_tree, derivation, None
                else:
                    return None, derivation, "Accept but no parse tree"
            
            else:
                return None, derivation, f"Unknown action: {action}"
    
    def get_derivation_string(self, derivation):
        """Convert derivation steps to readable string"""
        result = []
        for i, step in enumerate(derivation, 1):
            result.append(f"  {i}. {step}")
        return "\n".join(result)

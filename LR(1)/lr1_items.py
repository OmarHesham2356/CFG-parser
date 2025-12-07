# LR(1) Item Sets and State Machine Construction

from grammar import LR1Item

class LR1ItemSetBuilder:
    """Build LR(1) item sets (states) for a grammar"""
    
    def __init__(self, grammar, first_computer):
        self.grammar = grammar
        self.first_computer = first_computer
        self.item_sets = []      # All LR(1) item sets
        self.goto_table = {}     # goto_table[(state_id, symbol)] = next_state_id
        self.state_map = {}      # Map item_set to state_id for deduplication
    
    def closure(self, kernel_items):
        """
        Compute closure of a set of LR(1) items.
        kernel_items: set of LR1Item objects
        """
        closed = set(kernel_items)
        added = True
        
        while added:
            added = False
            
            for item in list(closed):
                # Get symbol after dot
                next_sym = item.symbol_after_dot()
                
                # If it's a nonterminal, add productions for it
                if next_sym and self.grammar.is_nonterminal(next_sym):
                    # Compute lookahead for new items
                    rest = item.prod.rhs[item.dot + 1:]
                    if rest:
                        # FIRST(rest + lookahead)
                        lookaheads = self.first_computer.first_of_sequence(
                            rest + [item.lookahead]
                        )
                    else:
                        # Just the lookahead
                        lookaheads = {item.lookahead}
                    
                    # Add all productions for next_sym with computed lookaheads
                    for prod in self.grammar.productions:
                        if prod.lhs == next_sym:
                            for lookahead in lookaheads:
                                if lookahead != 'ε':  # Don't use ε as lookahead
                                    new_item = LR1Item(prod, 0, lookahead)
                                    if new_item not in closed:
                                        closed.add(new_item)
                                        added = True
        
        return frozenset(closed)
    
    def goto(self, item_set, symbol):
        """
        Compute GOTO(item_set, symbol).
        Returns closure of items with dot moved past symbol.
        """
        # Find items where dot is before 'symbol'
        kernel = set()
        for item in item_set:
            if item.symbol_after_dot() == symbol:
                # Create new item with dot moved past symbol
                new_item = LR1Item(item.prod, item.dot + 1, item.lookahead)
                kernel.add(new_item)
        
        if not kernel:
            return frozenset()
        
        # Return closure of kernel
        return self.closure(kernel)
    
    def build(self):
        """Build all LR(1) item sets"""
        # Initial item: [S' -> . S, $]
        # S' is augmented start, S is original start
        for prod in self.grammar.augmented_productions:
            if prod.lhs == self.grammar.augmented_start:
                initial_item = LR1Item(prod, 0, '$')
                break
        
        I0 = self.closure({initial_item})
        
        self.item_sets.append(I0)
        self.state_map[I0] = 0
        
        worklist = [I0]
        processed = set()
        
        while worklist:
            current_set = worklist.pop(0)
            
            if current_set in processed:
                continue
            processed.add(current_set)
            
            state_id = self.state_map[current_set]
            
            # Find all symbols that have successors
            symbols_after_dot = set()
            for item in current_set:
                next_sym = item.symbol_after_dot()
                if next_sym:
                    symbols_after_dot.add(next_sym)
            
            # For each symbol, compute GOTO
            for symbol in symbols_after_dot:
                next_set = self.goto(current_set, symbol)
                
                if next_set:
                    if next_set not in self.state_map:
                        next_state_id = len(self.item_sets)
                        self.item_sets.append(next_set)
                        self.state_map[next_set] = next_state_id
                        worklist.append(next_set)
                    else:
                        next_state_id = self.state_map[next_set]
                    
                    # Record GOTO transition
                    self.goto_table[(state_id, symbol)] = next_state_id
        
        return self.item_sets, self.goto_table
    
    def print_item_sets(self):
        """Print all item sets"""
        for state_id, item_set in enumerate(self.item_sets):
            print(f"\nI{state_id}:")
            for item in sorted(item_set, key=lambda x: (str(x.prod.lhs), x.prod.prod_id, x.dot, x.lookahead)):
                print(f"  {item}")

# LR(1) Parsing Table Construction

class LR1TableBuilder:
    """Build ACTION and GOTO parsing tables from LR(1) item sets"""
    
    def __init__(self, grammar, item_sets, goto_table):
        self.grammar = grammar
        self.item_sets = item_sets
        self.goto_table = goto_table
        self.action_table = []    # ACTION[state][symbol] = action
        self.goto_table_filled = []  # GOTO[state][nonterminal] = next_state
    
    def build(self):
        """Build ACTION and GOTO tables"""
        num_states = len(self.item_sets)
        
        # Initialize tables
        for _ in range(num_states):
            self.action_table.append({})
            self.goto_table_filled.append({})
        
        # Fill tables
        for state_id, item_set in enumerate(self.item_sets):
            for item in item_set:
                next_sym = item.symbol_after_dot()
                
                # SHIFT action: [A → α • a β, x]
                if next_sym and self.grammar.is_terminal(next_sym):
                    next_state = self.goto_table.get((state_id, next_sym))
                    if next_state is not None:
                        # Check for shift-reduce conflicts
                        if next_sym in self.action_table[state_id]:
                            existing = self.action_table[state_id][next_sym]
                            if existing[0] != 'shift':
                                print(f"WARNING: Shift-reduce conflict in state {state_id}")
                        
                        self.action_table[state_id][next_sym] = ('shift', next_state)
                
                # REDUCE action: [A → α •, x] (but NOT augmented production)
                elif item.is_complete() and item.prod.lhs != self.grammar.augmented_start:
                    # Find production index
                    prod_id = None
                    for i, prod in enumerate(self.grammar.augmented_productions):
                        if prod == item.prod:
                            prod_id = i
                            break
                    
                    # Check for reduce-reduce conflicts
                    if item.lookahead in self.action_table[state_id]:
                        existing = self.action_table[state_id][item.lookahead]
                        if existing[0] == 'reduce':
                            print(f"WARNING: Reduce-reduce conflict in state {state_id}, lookahead {item.lookahead}")
                    
                    self.action_table[state_id][item.lookahead] = ('reduce', prod_id)
                
                # ACCEPT action: [S' → S •, $]
                elif (item.is_complete() and 
                      item.prod.lhs == self.grammar.augmented_start and 
                      item.lookahead == '$'):
                    self.action_table[state_id]['$'] = ('accept',)
        
        # Fill GOTO table for nonterminals
        for (state_id, symbol), next_state in self.goto_table.items():
            if self.grammar.is_nonterminal(symbol):
                self.goto_table_filled[state_id][symbol] = next_state
        
        return self.action_table, self.goto_table_filled
    
    def print_tables(self):
        """Print ACTION and GOTO tables"""
        terminals = sorted(self.grammar.terminals) + ['$']
        nonterminals = sorted(self.grammar.nonterminals)
        
        print("\n" + "="*80)
        print("LR(1) PARSING TABLE")
        print("="*80)
        
        # Print header
        print(f"{'State':<8}", end='')
        for term in terminals:
            print(f"{term:<12}", end='')
        for nt in nonterminals:
            print(f"{nt:<12}", end='')
        print()
        print("-" * 80)
        
        # Print rows
        for state_id in range(len(self.action_table)):
            print(f"I{state_id:<7}", end='')
            
            # ACTION entries
            for term in terminals:
                if term in self.action_table[state_id]:
                    action = self.action_table[state_id][term]
                    if action[0] == 'shift':
                        print(f"s{action[1]:<10}", end='')
                    elif action[0] == 'reduce':
                        print(f"r{action[1]:<10}", end='')
                    elif action[0] == 'accept':
                        print(f"accept     ", end='')
                    else:
                        print(f"{'':12}", end='')
                else:
                    print(f"{'':12}", end='')
            
            # GOTO entries
            for nt in nonterminals:
                if nt in self.goto_table_filled[state_id]:
                    print(f"{self.goto_table_filled[state_id][nt]:<12}", end='')
                else:
                    print(f"{'':12}", end='')
            
            print()

# FIRST and FOLLOW Set Computation

class FirstFollowComputer:
    """Compute FIRST and FOLLOW sets for a grammar"""
    
    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = {}
        self.follow_sets = {}
    
    def compute_first_sets(self):
        """Compute FIRST set for all symbols"""
        # Initialize
        for symbol in self.grammar.terminals:
            self.first_sets[symbol] = {symbol}
        
        for symbol in self.grammar.nonterminals:
            self.first_sets[symbol] = set()
        
        # Iterate until no changes
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                old_size = len(self.first_sets[prod.lhs])
                
                # Add FIRST of first symbol in RHS
                if not prod.rhs:  # epsilon production
                    self.first_sets[prod.lhs].add('ε')
                else:
                    for symbol in prod.rhs:
                        # Add FIRST(symbol) - {ε}
                        for term in self.first_sets.get(symbol, set()):
                            if term != 'ε':
                                self.first_sets[prod.lhs].add(term)
                        
                        # If ε not in FIRST(symbol), stop
                        if 'ε' not in self.first_sets.get(symbol, set()):
                            break
                    else:
                        # All symbols can derive ε
                        self.first_sets[prod.lhs].add('ε')
                
                if len(self.first_sets[prod.lhs]) > old_size:
                    changed = True
        
        return self.first_sets
    
    def first_of_sequence(self, symbols):
        """Compute FIRST of a sequence of symbols"""
        result = set()
        
        for symbol in symbols:
            first_sym = self.first_sets.get(symbol, {symbol})
            for term in first_sym:
                if term != 'ε':
                    result.add(term)
            
            if 'ε' not in first_sym:
                return result
        
        # All can derive ε
        result.add('ε')
        return result
    
    def compute_follow_sets(self):
        """Compute FOLLOW set for all nonterminals"""
        # Initialize
        for nt in self.grammar.nonterminals:
            self.follow_sets[nt] = set()
        
        # FOLLOW(start) includes $
        self.follow_sets[self.grammar.start_symbol].add('$')
        
        # Iterate until no changes
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                # For each symbol in RHS
                for i, symbol in enumerate(prod.rhs):
                    if not self.grammar.is_nonterminal(symbol):
                        continue
                    
                    old_size = len(self.follow_sets[symbol])
                    
                    # FOLLOW(symbol) += FIRST(rest) - {ε}
                    rest = prod.rhs[i+1:]
                    if rest:
                        first_rest = self.first_of_sequence(rest)
                        for term in first_rest:
                            if term != 'ε':
                                self.follow_sets[symbol].add(term)
                        
                        # If ε in FIRST(rest), add FOLLOW(LHS)
                        if 'ε' in first_rest:
                            self.follow_sets[symbol].update(
                                self.follow_sets[prod.lhs]
                            )
                    else:
                        # No symbols after, add FOLLOW(LHS)
                        self.follow_sets[symbol].update(
                            self.follow_sets[prod.lhs]
                        )
                    
                    if len(self.follow_sets[symbol]) > old_size:
                        changed = True
        
        return self.follow_sets
    
    def print_sets(self):
        """Print FIRST and FOLLOW sets"""
        print("\n--- FIRST Sets ---")
        for symbol in sorted(self.first_sets.keys()):
            print(f"FIRST({symbol}) = {self.first_sets[symbol]}")
        
        print("\n--- FOLLOW Sets ---")
        for symbol in sorted(self.follow_sets.keys()):
            print(f"FOLLOW({symbol}) = {self.follow_sets[symbol]}")

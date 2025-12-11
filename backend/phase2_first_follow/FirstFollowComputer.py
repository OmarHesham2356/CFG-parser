from typing import List, Set, Dict
from phase1_grammar import Production, Grammar, EPSILON, END_OF_INPUT


class FirstFollowComputer:
    """
    Computes FIRST and FOLLOW sets for a context-free grammar.
    
    FIRST(X):
    - For terminal 'a': FIRST(a) = {a}
    - For nonterminal A: terminals that can start strings from A
    - For sequence: computed left-to-right, propagating ε
    
    FOLLOW(A):
    - Terminals that can appear immediately after A in some sentential form
    - Always includes $ for the start symbol
    
    These sets are essential for LR(1) parsing to compute lookaheads.
    """
    
    def __init__(self, grammar: Grammar, auto_compute: bool = True):
        """
        Args:
            grammar: The augmented grammar
            auto_compute: If True, compute sets immediately on construction
        """
        self.grammar = grammar
        
        # Store FIRST sets for all symbols
        self.first_sets: Dict[str, Set[str]] = {}
        
        # Store FOLLOW sets for all nonterminals
        self.follow_sets: Dict[str, Set[str]] = {}
        
        # Initialize sets (empty initially)
        for symbol in grammar.terminals | grammar.nonterminals:
            self.first_sets[symbol] = set()
        
        for nonterminal in grammar.nonterminals:
            self.follow_sets[nonterminal] = set()
        
        # Auto-compute if requested
        if auto_compute:
            self.compute_first_sets(verbose=False)
            self.compute_follow_sets(verbose=False)
    
    def compute_first_sets(self, verbose: bool = False):
        """
        Compute FIRST sets for all symbols using fixed-point iteration.
        
        Rules:
        1. FIRST(terminal) = {terminal}
        2. If A → ε, then ε ∈ FIRST(A)
        3. For A → X₁X₂...Xₙ, add FIRST of sequence to FIRST(A)
        """
        
        if verbose:
            print("\nComputing FIRST sets...")
            print("=" * 70)
        
        # Rule 1: Initialize FIRST for terminals
        for terminal in self.grammar.terminals:
            self.first_sets[terminal].add(terminal)
        
        if verbose:
            print(f"Initialized {len(self.grammar.terminals)} terminals")
        
        # Rule 2 & 3: Iteratively apply rules until no change (fixed point)
        iteration = 0
        changed = True
        
        while changed:
            iteration += 1
            changed = False
            
            if verbose:
                print(f"\nIteration {iteration}:")
            
            for production in self.grammar.productions:
                lhs = production.lhs
                rhs = production.rhs
                
                if verbose:
                    prod_str = f"{lhs} → {' '.join(rhs) if rhs else EPSILON}"
                
                if not rhs:
                    # A → ε: add ε to FIRST(A)
                    if EPSILON not in self.first_sets[lhs]:
                        self.first_sets[lhs].add(EPSILON)
                        changed = True
                        if verbose:
                            print(f"  {prod_str}: added ε to FIRST({lhs})")
                else:
                    # A → X₁X₂...Xₙ
                    # Compute FIRST of the sequence
                    sequence_first = self.first_of_sequence(rhs)
                    
                    # Add all non-ε symbols to FIRST(A)
                    before = len(self.first_sets[lhs])
                    for symbol in sequence_first:
                        if symbol != EPSILON:
                            self.first_sets[lhs].add(symbol)
                    
                    # Add ε if entire sequence can produce ε
                    if EPSILON in sequence_first:
                        self.first_sets[lhs].add(EPSILON)
                    
                    if len(self.first_sets[lhs]) > before:
                        changed = True
                        if verbose:
                            print(f"  {prod_str}: added {sequence_first} to FIRST({lhs})")
        
        if verbose:
            print(f"\nFIRST computation converged after {iteration} iterations")
    
    def first_of_symbol(self, symbol: str) -> Set[str]:
        """
        Get FIRST set for a single symbol.
        
        Args:
            symbol: Terminal or nonterminal
            
        Returns:
            FIRST(symbol)
        """
        if symbol not in self.first_sets:
            # If symbol not in sets, return empty
            return set()
        return set(self.first_sets[symbol])
    
    def first_of_sequence(self, symbols: List[str]) -> Set[str]:
        """
        Compute FIRST for a sequence of symbols.
        
        FIRST(X₁X₂...Xₙ):
        - Start with FIRST(X₁) - {ε}
        - If ε ∈ FIRST(X₁), add FIRST(X₂) - {ε}
        - Continue until we find a symbol without ε or reach end
        - If all can produce ε, add ε to result
        
        Args:
            symbols: List of terminals/nonterminals
            
        Returns:
            FIRST(symbol sequence)
        """
        if not symbols:
            return {EPSILON}
        
        result: Set[str] = set()
        
        for symbol in symbols:
            # Get FIRST of current symbol
            first_sym = self.first_of_symbol(symbol)
            
            # Add all non-ε symbols
            result.update(s for s in first_sym if s != EPSILON)
            
            # If this symbol cannot produce ε, stop
            if EPSILON not in first_sym:
                return result
        
        # If we get here, all symbols can produce ε
        result.add(EPSILON)
        return result
    
    def compute_follow_sets(self, verbose: bool = False):
        """
        Compute FOLLOW sets for all nonterminals using fixed-point iteration.
        
        Rules:
        1. FOLLOW(start) contains $
        2. For production A → αBβ:
           - Add FIRST(β) - {ε} to FOLLOW(B)
           - If ε ∈ FIRST(β), add FOLLOW(A) to FOLLOW(B)
        """
        
        if verbose:
            print("\nComputing FOLLOW sets...")
            print("=" * 70)
        
        # Rule 1: Add $ to FOLLOW(start symbol)
        self.follow_sets[self.grammar.start_symbol].add(END_OF_INPUT)
        
        if verbose:
            print(f"Initialized FOLLOW({self.grammar.start_symbol}) with $")
        
        # Rule 2: Iteratively apply rules until no change (fixed point)
        iteration = 0
        changed = True
        
        while changed:
            iteration += 1
            changed = False
            
            if verbose:
                print(f"\nIteration {iteration}:")
            
            # For each production A → α B β
            for production in self.grammar.productions:
                lhs = production.lhs
                rhs = production.rhs
                
                # For each symbol in the RHS
                for i, symbol in enumerate(rhs):
                    # We only care about nonterminals
                    if symbol not in self.grammar.nonterminals:
                        continue
                    
                    # β = symbols after B
                    beta = rhs[i + 1:]
                    
                    if verbose:
                        prod_str = f"{lhs} → {' '.join(rhs) if rhs else EPSILON}"
                    
                    if beta:
                        # Case 1: A → αBβ where β is nonempty
                        # Add FIRST(β) - {ε} to FOLLOW(B)
                        first_beta = self.first_of_sequence(beta)
                        
                        before = len(self.follow_sets[symbol])
                        for t in first_beta:
                            if t != EPSILON:
                                self.follow_sets[symbol].add(t)
                        
                        if len(self.follow_sets[symbol]) > before:
                            changed = True
                            if verbose:
                                added = [t for t in first_beta if t != EPSILON]
                                print(f"  {prod_str}: added {added} to FOLLOW({symbol})")
                        
                        # Case 1b: If ε ∈ FIRST(β), add FOLLOW(A) to FOLLOW(B)
                        if EPSILON in first_beta:
                            before = len(self.follow_sets[symbol])
                            self.follow_sets[symbol].update(self.follow_sets[lhs])
                            if len(self.follow_sets[symbol]) > before:
                                changed = True
                                if verbose:
                                    print(f"  {prod_str}: β can be ε, added FOLLOW({lhs}) to FOLLOW({symbol})")
                    else:
                        # Case 2: A → αB (B is at end)
                        # Add FOLLOW(A) to FOLLOW(B)
                        before = len(self.follow_sets[symbol])
                        self.follow_sets[symbol].update(self.follow_sets[lhs])
                        
                        if len(self.follow_sets[symbol]) > before:
                            changed = True
                            if verbose:
                                prod_str = f"{lhs} → {' '.join(rhs) if rhs else EPSILON}"
                                print(f"  {prod_str}: B at end, added FOLLOW({lhs}) to FOLLOW({symbol})")
        
        if verbose:
            print(f"\nFOLLOW computation converged after {iteration} iterations")
    
    def first_of(self, symbol: str) -> Set[str]:
        """Public method to get FIRST set."""
        return self.first_of_symbol(symbol)
    
    def follow_of(self, nonterminal: str) -> Set[str]:
        """
        Get FOLLOW set for a nonterminal.
        
        Args:
            nonterminal: A nonterminal symbol
            
        Returns:
            FOLLOW(nonterminal)
        """
        if nonterminal not in self.follow_sets:
            return set()
        return set(self.follow_sets[nonterminal])
    
    def print_sets(self):
        """Print all FIRST and FOLLOW sets in readable format."""
        
        print("\nFIRST and FOLLOW Sets")
        print("=" * 70)
        
        print("\nFIRST Sets:")
        print("-" * 70)
        for symbol in sorted(self.first_sets.keys()):
            first_set = self.first_sets[symbol]
            if first_set:
                symbols_str = ', '.join(sorted(first_set))
                print(f"  FIRST({symbol:8s}) = {{ {symbols_str} }}")
        
        print("\nFOLLOW Sets:")
        print("-" * 70)
        for nonterminal in sorted(self.follow_sets.keys()):
            follow_set = self.follow_sets[nonterminal]
            if follow_set:
                symbols_str = ', '.join(sorted(follow_set))
                print(f"  FOLLOW({nonterminal:8s}) = {{ {symbols_str} }}")
            else:
                print(f"  FOLLOW({nonterminal:8s}) = {{ }}")

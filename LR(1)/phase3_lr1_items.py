# ============================================================================
# Phase 3: LR(1) Item Sets and State Machine Construction
# ============================================================================
# Improvements:
# 1. Efficient item set generation using closure and GOTO
# 2. Frozenset-based deduplication for states
# 3. Complete DFA construction for all reachable states
# 4. Verbose output showing state transitions
# ============================================================================

from typing import List, Set, Tuple, FrozenSet, Dict, Optional
from phase1_grammar import Production, LR1Item, Grammar, EPSILON, END_OF_INPUT
from phase2_first_follow import FirstFollowComputer


class LR1ItemSetBuilder:
    """
    Builds the LR(1) item sets (states) and state machine (DFA).
    
    The key idea:
    - Each state is a set of LR(1) items
    - closure() expands items to all reachable items
    - goto() computes the next state given a symbol
    - build() constructs the complete DFA
    """
    
    def __init__(self, grammar: Grammar, ff_computer: 'FirstFollowComputer'):
        """
        Args:
            grammar: The augmented grammar
            ff_computer: Precomputed FIRST/FOLLOW sets
        """
        self.grammar = grammar
        self.ff = ff_computer
        
        # Output
        self.item_sets: List[FrozenSet[LR1Item]] = []
        self.goto_table: Dict[Tuple[int, str], int] = {}
        
        # Working storage
        self._item_set_to_state: Dict[FrozenSet[LR1Item], int] = {}
        self._processed: Set[FrozenSet[LR1Item]] = set()
        self._worklist: List[FrozenSet[LR1Item]] = []
    
    def closure(self, items: Set[LR1Item]) -> Set[LR1Item]:
        """
        Compute closure of a set of items.
        
        For each item [A → α • B β, a]:
        - If B is a nonterminal, add [B → • γ, b] for each production B → γ
        - b ∈ FIRST(βa)
        
        Args:
            items: Initial set of LR(1) items
            
        Returns:
            Closed set of items (fixed point)
        """
        closure_set = set(items)
        changed = True
        
        while changed:
            changed = False
            for item in list(closure_set):
                # Get symbol after dot
                symbol_after_dot = item.symbol_after_dot()
                
                if symbol_after_dot is None:
                    # Dot at end, no expansion
                    continue
                
                if not self.grammar.is_nonterminal(symbol_after_dot):
                    # Next symbol is terminal, can't expand
                    continue
                
                # Compute lookahead for new items
                # For item [A → α • B β, a], lookahead is FIRST(βa)
                rest_of_rhs = item.prod.rhs[item.dot + 1:]  # β
                beta_lookahead = self.ff.first_of_sequence(rest_of_rhs + [item.lookahead])
                
                # Add items for all productions of symbol_after_dot
                for prod in self.grammar.get_productions_for(symbol_after_dot):
                    for la in beta_lookahead:
                        new_item = LR1Item(prod, 0, la)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            changed = True
        
        return closure_set
    
    def goto(self, items: Set[LR1Item], symbol: str) -> Set[LR1Item]:
        """
        Compute GOTO(items, symbol).
        
        For each item [A → α • X β, a] where X = symbol,
        move the dot: [A → αX • β, a]
        Then compute closure.
        
        Args:
            items: Set of LR(1) items
            symbol: Grammar symbol (terminal or nonterminal)
            
        Returns:
            New item set after moving dot over symbol
        """
        # Move dot over symbol for all items that have symbol after dot
        goto_set = set()
        
        for item in items:
            if item.symbol_after_dot() == symbol:
                # Create new item with dot moved forward
                new_item = LR1Item(item.prod, item.dot + 1, item.lookahead)
                goto_set.add(new_item)
        
        # If no items were moved, result is empty
        if not goto_set:
            return set()
        
        # Compute closure and return
        return self.closure(goto_set)
    
    def build(self) -> Tuple[List[FrozenSet[LR1Item]], Dict[Tuple[int, str], int]]:
        """
        Build the complete LR(1) state machine.
        
        Returns:
            (item_sets, goto_table)
            - item_sets: List of states (each is a frozenset of items)
            - goto_table: Dict[(state_id, symbol)] -> next_state_id
        """
        # Create initial item: [S' → • S, $]
        start_prod = self.grammar.augmented_productions[0]
        initial_item = LR1Item(start_prod, 0, END_OF_INPUT)
        initial_set = frozenset(self.closure({initial_item}))
        
        # Initialize worklist
        self.item_sets = [initial_set]
        self._item_set_to_state[initial_set] = 0
        self._worklist = [initial_set]
        self._processed = set()
        
        # Worklist algorithm
        while self._worklist:
            current_set = self._worklist.pop(0)
            
            if current_set in self._processed:
                continue
            
            self._processed.add(current_set)
            current_state = self._item_set_to_state[current_set]
            
            # Find all unique symbols after dot
            symbols = set()
            for item in current_set:
                symbol = item.symbol_after_dot()
                if symbol is not None:
                    symbols.add(symbol)
            
            # For each symbol, compute GOTO
            for symbol in symbols:
                goto_set = self.goto(current_set, symbol)
                
                if not goto_set:
                    continue
                
                goto_frozen = frozenset(goto_set)
                
                # Check if we've seen this state before
                if goto_frozen not in self._item_set_to_state:
                    # New state
                    state_id = len(self.item_sets)
                    self.item_sets.append(goto_frozen)
                    self._item_set_to_state[goto_frozen] = state_id
                    self._worklist.append(goto_frozen)
                else:
                    state_id = self._item_set_to_state[goto_frozen]
                
                # Record GOTO entry
                self.goto_table[(current_state, symbol)] = state_id
        
        return self.item_sets, self.goto_table
    
    def print_item_sets(self):
        """Print all item sets and their contents."""
        print("\nLR(1) Item Sets:")
        print("=" * 70)
        
        for state_id, items in enumerate(self.item_sets):
            print(f"\nState {state_id}:")
            print("-" * 70)
            for item in sorted(items):
                print(f"  {item}")
    
    def print_goto_transitions(self):
        """Print GOTO table entries (state transitions)."""
        print("\nGOTO Transitions:")
        print("=" * 70)
        
        for (state_id, symbol), next_state in sorted(self.goto_table.items()):
            print(f"  GOTO({state_id}, {symbol:6s}) = {next_state}")


# ============================================================================
# Example usage and validation
# ============================================================================

# if __name__ == "__main__":
#     from phase2_first_follow import FirstFollowComputer
    
#     print("Testing LR(1) Item Set Construction")
#     print("=" * 70)
    
#     # Create simple grammar: E → E + T | T, T → id
#     productions = [
#         Production("E", ["E", "+", "T"], prod_id=1),
#         Production("E", ["T"], prod_id=2),
#         Production("T", ["id"], prod_id=3),
#     ]
    
#     grammar = Grammar(productions, "E")
#     print(grammar)
    
#     # Compute FIRST/FOLLOW
#     ff = FirstFollowComputer(grammar)
#     ff.compute_first_sets()
#     ff.compute_follow_sets()
    
#     # Build item sets
#     builder = LR1ItemSetBuilder(grammar, ff)
#     item_sets, goto_table = builder.build()
    
#     print(f"\nTotal states: {len(item_sets)}")
#     print(f"Total GOTO entries: {len(goto_table)}")
    
#     builder.print_item_sets()
#     builder.print_goto_transitions()
    
#     print("\n" + "=" * 70)
#     print("Item set construction complete!")

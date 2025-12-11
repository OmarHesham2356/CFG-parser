from typing import Dict, List, Tuple
from phase1_grammar import Production, LR1Item, Grammar, END_OF_INPUT
from .ParseAction import ParseAction
from .ConflictInfo import ConflictInfo


class LR1TableBuilder:
    """
    Builds ACTION and GOTO tables from LR(1) item sets.
    
    The key idea:
    - For each state and symbol, look at the items
    - Items with dot before terminal → shift entry
    - Items with dot at end → reduce entry (based on lookahead)
    - Augmented start item at end → accept entry
    """
    
    def __init__(self, grammar: Grammar, item_sets: List, goto_table: Dict):
        """
        Args:
            grammar: The augmented grammar
            item_sets: List of item sets (from phase 3)
            goto_table: GOTO table (from phase 3)
        """
        self.grammar = grammar
        self.item_sets = item_sets
        self.goto_table = goto_table
        
        # Output tables
        self.action_table: Dict[Tuple[int, str], ParseAction] = {}
        self.goto_filled: Dict[Tuple[int, str], int] = {}
        
        # Conflict tracking
        self.conflicts: List[ConflictInfo] = []
    
    def build(self) -> Tuple[Dict, Dict]:
        """
        Build ACTION and GOTO tables.
        
        Returns:
            (action_table, goto_filled)
        """
        # Process each state
        for state_id, items in enumerate(self.item_sets):
            self._process_state(state_id, items)
        
        # Copy GOTO table (already computed in phase 3)
        self.goto_filled = self.goto_table.copy()
        
        return self.action_table, self.goto_filled
    
    def _process_state(self, state_id: int, items):
        """Process all items in a state to generate ACTION entries."""
        
        for item in items:
            symbol_after_dot = item.symbol_after_dot()
            
            if symbol_after_dot is None:
                # Dot at end: REDUCE or ACCEPT
                self._handle_reduce_item(state_id, item)
            elif self.grammar.is_terminal(symbol_after_dot):
                # Symbol after dot is terminal: SHIFT
                self._handle_shift_item(state_id, item, symbol_after_dot)
    
    def _handle_shift_item(self, state_id: int, item: LR1Item, terminal: str):
        """Handle item with terminal after dot (SHIFT action)."""
        
        # Look up next state via GOTO
        next_state = self.goto_table.get((state_id, terminal))
        
        if next_state is None:
            # This shouldn't happen in a well-formed LR(1) construction
            return
        
        action = ParseAction('shift', state=next_state)
        
        # Check for conflict
        key = (state_id, terminal)
        if key in self.action_table:
            existing = self.action_table[key]
            if existing.action_type != 'shift' or existing.state != next_state:
                # Conflict!
                conflict = ConflictInfo(
                    state=state_id,
                    symbol=terminal,
                    conflict_type='shift-reduce' if existing.action_type == 'reduce' else 'shift-shift',
                    action1=existing,
                    action2=action,
                    description=f"Both shift to {next_state} and {existing}"
                )
                self.conflicts.append(conflict)
        else:
            self.action_table[key] = action
    
    def _handle_reduce_item(self, state_id: int, item: LR1Item):
        """Handle item with dot at end (REDUCE or ACCEPT action)."""
        
        prod = item.prod
        lookahead = item.lookahead
        
        # Check if this is the augmented start item
        if prod == self.grammar.augmented_productions[0]:
            # [S' → S •, $]
            if lookahead == END_OF_INPUT:
                action = ParseAction('accept')
                key = (state_id, lookahead)
                
                if key in self.action_table:
                    existing = self.action_table[key]
                    if existing.action_type != 'accept':
                        conflict = ConflictInfo(
                            state=state_id,
                            symbol=lookahead,
                            conflict_type='accept-other',
                            action1=existing,
                            action2=action
                        )
                        self.conflicts.append(conflict)
                else:
                    self.action_table[key] = action
        else:
            # Regular reduce
            action = ParseAction('reduce', production=prod)
            key = (state_id, lookahead)
            
            if key in self.action_table:
                existing = self.action_table[key]
                
                if existing.action_type == 'shift':
                    # Shift-reduce conflict
                    conflict = ConflictInfo(
                        state=state_id,
                        symbol=lookahead,
                        conflict_type='shift-reduce',
                        action1=existing,
                        action2=action,
                        description=f"Shift to {existing.state} vs Reduce by {prod}"
                    )
                    self.conflicts.append(conflict)
                elif existing.action_type == 'reduce':
                    # Reduce-reduce conflict
                    conflict = ConflictInfo(
                        state=state_id,
                        symbol=lookahead,
                        conflict_type='reduce-reduce',
                        action1=existing,
                        action2=action,
                        description=f"Reduce by {existing.production} vs {prod}"
                    )
                    self.conflicts.append(conflict)
            else:
                self.action_table[key] = action
    
    def print_tables(self):
        """Print ACTION and GOTO tables in readable format."""
        
        print("\nPARSING TABLES")
        print("=" * 80)
        
        # Collect all symbols
        all_terminals = set()
        all_nonterminals = set()
        
        for (state, symbol) in self.action_table.keys():
            if self.grammar.is_terminal(symbol) or symbol == END_OF_INPUT:
                all_terminals.add(symbol)
        
        for (state, symbol) in self.goto_filled.items():
            if self.grammar.is_nonterminal(symbol):
                all_nonterminals.add(symbol)
        
        terminals = sorted(all_terminals)
        nonterminals = sorted(all_nonterminals)
        
        # Print ACTION table
        print("\nACTION Table (shift/reduce/accept/error):")
        print("-" * 80)
        print(f"{'State':>6s}  ", end="")
        for term in terminals:
            print(f"{term:>8s}", end="  ")
        print()
        
        for state_id in range(len(self.item_sets)):
            print(f"{state_id:>6d}  ", end="")
            for term in terminals:
                key = (state_id, term)
                if key in self.action_table:
                    print(f"{str(self.action_table[key]):>8s}", end="  ")
                else:
                    print(f"{'—':>8s}", end="  ")
            print()
        
        # Print GOTO table
        if nonterminals:
            print("\nGOTO Table (next state):")
            print("-" * 80)
            print(f"{'State':>6s}  ", end="")
            for nonterm in nonterminals:
                print(f"{nonterm:>8s}", end="  ")
            print()
            
            for state_id in range(len(self.item_sets)):
                print(f"{state_id:>6d}  ", end="")
                for nonterm in nonterminals:
                    key = (state_id, nonterm)
                    if key in self.goto_filled:
                        print(f"{self.goto_filled[key]:>8d}", end="  ")
                    else:
                        print(f"{'—':>8s}", end="  ")
                print()
    
    def print_conflicts(self):
        """Print any detected conflicts."""
        
        if not self.conflicts:
            print("\n✓ No conflicts detected (grammar is LR(1))")
            return
        
        print(f"\n⚠ {len(self.conflicts)} conflict(s) detected:")
        print("=" * 80)
        
        for i, conflict in enumerate(self.conflicts, 1):
            print(f"\n{i}. {conflict}")
            if conflict.description:
                print(f"   {conflict.description}")

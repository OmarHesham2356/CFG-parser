from phase1_grammar import Production, Grammar
from phase2_first_follow import FirstFollowComputer
from phase3_lr1_items import LR1ItemSetBuilder
from phase4_lr1_table import LR1TableBuilder
from phase5_lr1_parser import LR1Parser


class LR1ParserBuilder:
    
    def __init__(self, productions, start_symbol, verbose=False):
        """
        Args:
            productions: List of Production objects
            start_symbol: Start nonterminal
            verbose: Print debug information if True
        """
        self.productions = productions
        self.start_symbol = start_symbol
        self.verbose = verbose
        
        self.grammar = None
        self.ff_computer = None
        self.item_builder = None
        self.table_builder = None
        self.parser = None
    
    def build(self):
        # Phase 1: Grammar
        self.grammar = Grammar(self.productions, self.start_symbol)
        
        # Phase 2: FIRST/FOLLOW
        self.ff_computer = FirstFollowComputer(self.grammar, auto_compute=True)
        
        # Phase 3: Item sets
        self.item_builder = LR1ItemSetBuilder(self.grammar, self.ff_computer)
        item_sets, goto_table = self.item_builder.build()
        
        # Phase 4: Tables
        self.table_builder = LR1TableBuilder(self.grammar, item_sets, goto_table)
        action_table, goto_filled = self.table_builder.build()
        
        # Phase 5: Parser
        self.parser = LR1Parser(self.grammar, action_table, goto_filled, self.verbose)
        
        if self.verbose:
            print(f"\nParser built successfully!")
            print(f"  States: {len(item_sets)}")
            print(f"  ACTION entries: {len(action_table)}")
            print(f"  GOTO entries: {len(goto_filled)}")
            if self.table_builder.conflicts:
                print(f"  ! Conflicts: {len(self.table_builder.conflicts)}")
            else:
                print(f"  OK: No conflicts")
        
        return self.parser

# ============================================================================
# LR(1) Parser - Main Entry Point
# ============================================================================
# User input based grammar parsing
# ============================================================================

from phase1_grammar import Production, Grammar
from phase2_first_follow import FirstFollowComputer
from phase3_lr1_items import LR1ItemSetBuilder
from phase4_lr1_table import LR1TableBuilder
from phase5_lr1_parser import LR1Parser


class LR1ParserBuilder:
    """
    Convenience class to build a complete LR(1) parser from a grammar.
    
    Usage:
        builder = LR1ParserBuilder(productions, "StartSymbol", verbose=True)
        parser = builder.build()
        tree, derivation, error = parser.parse(tokens)
    """
    
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
        
        # Components (built on demand)
        self.grammar = None
        self.ff_computer = None
        self.item_builder = None
        self.table_builder = None
        self.parser = None
    
    def build(self):
        """Build the complete parser."""
        
        # Phase 1: Grammar
        self.grammar = Grammar(self.productions, self.start_symbol)
        
        # Phase 2: FIRST/FOLLOW (with auto_compute=True)
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


def get_grammar_from_user():
    """
    Get grammar productions from user input.
    
    Format: Each line should be "LHS -> RHS" where RHS symbols are space-separated
    Example: 
        E -> E + T | T
        T -> T * F | F
        F -> ( E ) | id
    
    Enter an empty line to finish.
    """
    print("\n" + "=" * 80)
    print("GRAMMAR INPUT")
    print("=" * 80)
    print("\nEnter grammar productions (format: LHS -> RHS | RHS | ...)")
    print("Separate multiple productions with | symbol")
    print("Enter empty line when done.\n")
    
    productions = []
    prod_id = 1
    
    while True:
        line = input(f"Production {prod_id}: ").strip()
        
        if not line:
            if not productions:
                print("Error: Grammar cannot be empty!")
                continue
            break
        
        # Parse line: "LHS -> RHS1 | RHS2 | RHS3"
        if "->" not in line:
            print("Error: Use '->' to separate LHS and RHS")
            continue
        
        lhs, rhs_part = line.split("->", 1)
        lhs = lhs.strip()
        
        if not lhs:
            print("Error: LHS cannot be empty")
            continue
        
        # Split by | for alternatives
        alternatives = rhs_part.split("|")
        
        for alt in alternatives:
            alt = alt.strip()
            
            # Handle epsilon (ε or empty)
            if alt.lower() == "epsilon" or alt == "ε" or alt == "":
                rhs_symbols = []
            else:
                # Split RHS into symbols (space-separated)
                rhs_symbols = alt.split()
            
            productions.append(Production(lhs, rhs_symbols, prod_id=prod_id))
            prod_id += 1
    
    return productions


def get_start_symbol_from_user(productions):
    """Get the start symbol from user."""
    print("\nAvailable nonterminals:", ", ".join(set(p.lhs for p in productions)))
    
    while True:
        start = input("Enter start symbol: ").strip()
        if start and any(p.lhs == start for p in productions):
            return start
        print("Error: Invalid start symbol")


def get_test_cases_from_user():
    """Get test cases from user."""
    print("\n" + "=" * 80)
    print("TEST INPUT")
    print("=" * 80)
    print("\nEnter test inputs (space-separated tokens)")
    print("Enter empty line when done.\n")
    
    test_cases = []
    
    while True:
        line = input("Test input: ").strip()
        
        if not line:
            break
        
        tokens = line.split()
        test_cases.append(tokens)
    
    return test_cases


def _tree_to_lines(node, indent=0):
    """Convert parse tree to list of indented lines."""
    lines = []
    prefix = "  " * indent
    lines.append(f"{prefix}{node.symbol}")
    for child in node.children:
        lines.extend(_tree_to_lines(child, indent + 1))
    return lines

def get_verbose_choice():
    """Ask user if they want verbose output."""
    while True:
        choice = input("Enable verbose output? (y/n): ").strip().lower()
        if choice in ('y', 'n'):
            if choice == 'y':
                return True
            return False
        else:
            print("Error: Please enter 'y' or 'n'.")

# ============================================================================
# Main: Run all examples
# ============================================================================

# ============================================================================
# Main: User-driven parser
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LR(1) PARSER - USER INPUT")
    print("=" * 80)
    
    try:
        # Get grammar from user
        productions = get_grammar_from_user()
        
        # Get start symbol
        start_symbol = get_start_symbol_from_user(productions)
        
        # Build parser
        print("\nBuilding parser...")
        verbose = get_verbose_choice()
        builder = LR1ParserBuilder(productions, start_symbol, verbose)
        parser = builder.build()
        
        # Get test cases from user
        test_cases = get_test_cases_from_user()
        
        if test_cases:
            # Test the parser
            print("\n" + "=" * 80)
            print("PARSING RESULTS")
            print("=" * 80)
            
            for tokens in test_cases:
                input_str = ' '.join(tokens) if tokens else "(empty)"
                tree, derivation, error = parser.parse(tokens)
                
                is_accepted = error is None
                status = "✓" if is_accepted else "✗"
                
                print(f"\n{status} Input: {input_str}")
                
                if error:
                    print(f"  Error: {error}")
                else:
                    print(f"  Accepted!")
                    if tree:
                        print(f"  Parse tree:")
                        lines = _tree_to_lines(tree)
                        for line in lines:
                            print(f"    {line}")
        else:
            print("\nNo test cases entered. Parser built successfully!")
        
        print("\n" + "=" * 80)
        print("Complete!")
        print("=" * 80)
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

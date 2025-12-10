# ============================================================================
# LR(1) Parser - Main Entry Point with Examples
# ============================================================================
# This file demonstrates complete working parsers for 3 different grammars
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
                print(f"  ⚠ Conflicts: {len(self.table_builder.conflicts)}")
            else:
                print(f"  ✓ No conflicts")
        
        return self.parser


def example_expression_grammar():
    """
    Expression grammar with operator precedence.
    
    E → E + T | T
    T → T * F | F
    F → ( E ) | id
    """
    
    productions = [
        Production("E", ["E", "+", "T"], prod_id=1),
        Production("E", ["T"], prod_id=2),
        Production("T", ["T", "*", "F"], prod_id=3),
        Production("T", ["F"], prod_id=4),
        Production("F", ["(", "E", ")"], prod_id=5),
        Production("F", ["id"], prod_id=6),
    ]
    
    return productions


def example_simple_grammar():
    """
    Simple grammar with epsilon production.
    
    S → A b
    A → a | ε
    """
    
    productions = [
        Production("S", ["A", "b"], prod_id=1),
        Production("A", ["a"], prod_id=2),
        Production("A", [], prod_id=3),  # epsilon
    ]
    
    return productions


def example_bracket_grammar():
    """
    Balanced bracket grammar.
    
    S → ( S ) | ε
    """
    
    productions = [
        Production("S", ["(", "S", ")"], prod_id=1),
        Production("S", [], prod_id=2),  # epsilon
    ]
    
    return productions


def run_example(name, productions, start, test_cases, verbose=False):
    """
    Run a complete example: build parser and test it.
    
    Args:
        name: Example name
        productions: List of Production objects
        start: Start symbol
        test_cases: List of (input_tokens, should_accept) tuples
        verbose: Print debug info
    """
    
    print("\n" + "=" * 80)
    print(f"Example: {name}")
    print("=" * 80)
    
    # Print grammar
    grammar = Grammar(productions, start)
    print("\nGrammar:")
    print(grammar)
    
    # Build parser
    builder = LR1ParserBuilder(productions, start, verbose=False)
    parser = builder.build()
    
    if verbose and builder.table_builder:
        print("\n--- Parsing Tables ---")
        builder.table_builder.print_tables()
        builder.table_builder.print_conflicts()
    
    # Test cases
    print("\nTest Cases:")
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for tokens, should_accept in test_cases:
        input_str = ' '.join(tokens) if tokens else "(empty)"
        tree, derivation, error = parser.parse(tokens if tokens else [])
        
        is_accepted = error is None
        status = "✓" if is_accepted == should_accept else "✗"
        
        print(f"\n{status} Input: {input_str}")
        print(f"  Expected: {'accept' if should_accept else 'reject'}")
        print(f"  Got: {'accept' if is_accepted else 'reject'}")
        
        if error:
            print(f"  Error: {error}")
        
        if is_accepted:
            print(f"  Parse tree:")
            # Print tree with indentation
            lines = _tree_to_lines(tree)
            for line in lines:
                print(f"    {line}")
        
        if is_accepted == should_accept:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    return passed, failed


def _tree_to_lines(node, indent=0):
    """Convert parse tree to list of indented lines."""
    lines = []
    prefix = "  " * indent
    lines.append(f"{prefix}{node.symbol}")
    for child in node.children:
        lines.extend(_tree_to_lines(child, indent + 1))
    return lines


# ============================================================================
# Main: Run all examples
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("LR(1) PARSER - COMPLETE EXAMPLES")
    print("=" * 80)
    
    total_passed = 0
    total_failed = 0
    
    # Example 1: Expression grammar
    prods_1 = example_expression_grammar()
    test_cases_1 = [
        (["id"], True),
        (["id", "+", "id"], True),
        (["id", "+", "id", "+", "id"], True),
        (["id", "*", "id"], True),
        (["id", "+", "id", "*", "id"], True),
        (["(", "id", ")"], True),
        (["(", "id", "+", "id", ")"], True),
        (["id", "+"], False),
        (["(", "id"], False),
    ]
    
    p, f = run_example("Expression Grammar (E → E + T | T, etc.)",
                       prods_1, "E", test_cases_1, verbose=False)
    total_passed += p
    total_failed += f
    
    # Example 2: Simple grammar with epsilon
    prods_2 = example_simple_grammar()
    test_cases_2 = [
        (["a", "b"], True),
        (["b"], True),
        (["a"], False),
        (["b", "b"], False),
    ]
    
    p, f = run_example("Simple Grammar (S → A b, A → a | ε)",
                       prods_2, "S", test_cases_2, verbose=False)
    total_passed += p
    total_failed += f
    
    # Example 3: Bracket grammar with epsilon
    prods_3 = example_bracket_grammar()
    test_cases_3 = [
        ([], True),
        (["(", ")"], True),
        (["(", "(", ")", ")"], True),
        (["(", "(", ")", ")", ")"], False),
        (["("], False),
    ]
    
    p, f = run_example("Bracket Grammar (S → ( S ) | ε)",
                       prods_3, "S", test_cases_3, verbose=False)
    total_passed += p
    total_failed += f
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total passed: {total_passed}")
    print(f"Total failed: {total_failed}")
    if total_passed + total_failed > 0:
        print(f"Success rate: {100*total_passed/(total_passed+total_failed):.1f}%")
    
    if total_failed == 0:
        print("\n✓ All tests passed!")
    else:
        print(f"\n⚠ {total_failed} test(s) failed - Check parser construction")
    
    print("\n" + "=" * 80)
    print("Complete!")

#!/usr/bin/env python3
"""     
Main example: Build and run an LR(1) parser

Example grammar:
E → E + T | T
T → T * F | F
F → ( E ) | id
"""

from grammar import Grammar, Production
from first_follow import FirstFollowComputer
from lr1_items import LR1ItemSetBuilder
from lr1_table import LR1TableBuilder
from lr1_parser import LR1Parser

def main():
    print("="*80)
    print("LR(1) PARSER EXAMPLE")
    print("="*80)
    
    # Define grammar
    # Grammar: E → E + T | T
    #          T → T * F | F
    #          F → ( E ) | id
    
    productions = [
        Production("E", ["E", "+", "T"], 1),
        Production("E", ["T"], 2),
        Production("T", ["T", "*", "F"], 3),
        Production("T", ["F"], 4),
        Production("F", ["(", "E", ")"], 5),
        Production("F", ["id"], 6),
    ]
    
    grammar = Grammar(productions, "E")
    
    print("\n1. Original Grammar:")
    print(grammar)
    
    # Compute FIRST and FOLLOW sets
    print("\n2. Computing FIRST and FOLLOW sets...")
    ff_computer = FirstFollowComputer(grammar)
    ff_computer.compute_first_sets()
    ff_computer.compute_follow_sets()
    ff_computer.print_sets()
    
    # Build LR(1) item sets
    print("\n3. Building LR(1) item sets...")
    item_builder = LR1ItemSetBuilder(grammar, ff_computer)
    item_sets, goto_table = item_builder.build()
    
    print(f"\nTotal states: {len(item_sets)}")
    item_builder.print_item_sets()
    
    # Build parsing tables
    print("\n4. Building parsing tables...")
    table_builder = LR1TableBuilder(grammar, item_sets, goto_table)
    action_table, goto_table_filled = table_builder.build()
    table_builder.print_tables()
    
    # Create parser
    parser = LR1Parser(grammar, action_table, goto_table_filled)
    
    # Test parse examples
    test_strings = [
        ["id"],                          # id
        ["id", "+", "id"],               # id + id
        ["id", "*", "id"],               # id * id
        ["id", "+", "id", "*", "id"],    # id + id * id
        ["(", "id", ")"],                # (id)
        ["(", "id", "+", "id", ")"],     # (id + id)
    ]
    
    print("\n" + "="*80)
    print("PARSING TESTS")
    print("="*80)
    
    for test_input in test_strings:
        print(f"\nInput: {' '.join(test_input)}")
        print("-" * 40)
        
        parse_tree, derivation, error = parser.parse(test_input)
        
        if error:
            print(f"ERROR: {error}")
        else:
            print("Parse tree:")
            parse_tree.pretty_print(indent=1)
            
            print("\nDerivation steps:")
            print(parser.get_derivation_string(derivation))
            
            print("\nFinal parse tree (compact):")
            print(parse_tree)

if __name__ == "__main__":
    main()

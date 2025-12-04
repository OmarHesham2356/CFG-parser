from backend.grammar_parser import GrammarParser, Tokenizer
from backend.cfg_parser import CFGParser

if __name__ == "__main__":
    gp = GrammarParser()

    n = int(input("Enter number of grammar rules: "))
    for _ in range(n):
        rule = input("Rule: ")
        gp.parse_rule(rule)

    grammar = gp.get_grammar()
    start_symbol = list(grammar.keys())[0]  # first rule is start

    # Extract terminals (symbols not on the left side)
    non_terminals = set(grammar.keys())
    terminals = set()
    for productions in grammar.values():
        for prod in productions:
            for symbol in prod:
                if symbol not in non_terminals and symbol != "ε":
                    terminals.add(symbol)

    tokenizer = Tokenizer(terminals)

    string = input("Enter string to parse: ")
    tokens = tokenizer.tokenize(string)

    parser = CFGParser(grammar, start_symbol)
    parser.tokens = tokens  # Set tokens for parser

    accepted, tree = parser.parse(tokens)  # Use parse_tokens if available

    if accepted:
        print("\nString Accepted!")
        print(tree.to_dict())
    else:
        print("\nString Rejected!")


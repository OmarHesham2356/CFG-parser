from backend.grammar_parser import GrammarParser, Tokenizer
from backend.cfg_parser import CFGParser


def build_grammar_from_input() -> tuple[dict, str, Tokenizer]:
    """
    Ask the user for grammar rules and return:
    - grammar: dict(nonterminal -> list of productions)
    - start_symbol: first nonterminal entered
    - tokenizer: Tokenizer built from inferred terminals
    """
    gp = GrammarParser()

    n = int(input("Enter number of grammar rules: "))
    for _ in range(n):
        rule = input("Rule: ")
        gp.parse_rule(rule)

    grammar = gp.get_grammar()
    start_symbol = list(grammar.keys())[0]  # first rule is start

    # infer terminals
    non_terminals = set(grammar.keys())
    terminals = set()
    for productions in grammar.values():
        for prod in productions:
            for symbol in prod:
                if symbol not in non_terminals and symbol != "ε":
                    terminals.add(symbol)

    tokenizer = Tokenizer(terminals)
    return grammar, start_symbol, tokenizer


def run_cli():
    """
    Interactive CLI:
    - read grammar
    - then repeatedly read strings and parse them
    """
    grammar, start_symbol, tokenizer = build_grammar_from_input()

    while True:
        string = input("Enter string to parse (or type 'exit' to quit): ")
        if string.lower() == "exit":
            break

        try:
            tokens = tokenizer.tokenize(string)
        except ValueError as e:
            print(f"Tokenization error: {e}")
            continue

        parser = CFGParser(grammar, start_symbol)
        accepted, tree = parser.parse(tokens)

        if accepted:
            print("\nString Accepted!")
            print(tree.to_dict())
        else:
            print("\nString Rejected!")

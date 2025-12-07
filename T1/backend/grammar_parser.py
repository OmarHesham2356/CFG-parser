class GrammarParser:
    def __init__(self):
        self.grammar = {}

    def parse_rule(self, rule: str):
        # Ignore empty lines
        rule = rule.strip()
        if not rule:
            return

        # Split into left and right parts
        if '->' not in rule:
            raise ValueError(f"Invalid rule: {rule}")
        left, right = rule.split('->', 1)
        left = left.strip()
        right = right.strip()

        # Split right part into productions
        productions = [prod.strip() for prod in right.split('|')]
        for prod in productions:
            symbols = prod.split()  # Split production into symbols
            self.grammar.setdefault(left, []).append(symbols)

    def get_grammar(self):
        return self.grammar

class Tokenizer:
    def __init__(self, terminals):
        self.terminals = set(terminals)

    def tokenize(self, input_string: str):
        tokens = []
        i = 0
        while i < len(input_string):
            match = None
            for term in sorted(self.terminals, key=len, reverse=True):
                if input_string.startswith(term, i):
                    match = term
                    break
            if match:
                tokens.append(match)
                i += len(match)
            else:
                if input_string[i].isspace():
                    i += 1  # Skip whitespace
                else:
                    raise ValueError(f"Unexpected character: {input_string[i]}")
        return tokens


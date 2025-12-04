class GrammarParser:
    """
    Reads and stores user-defined CFG rules.
    """

    def __init__(self):
        self.grammar = {}  # { NonTerminal: [ [symbols], [symbols] ] }

    def parse_rule(self, rule: str):
        """
        Parses a rule string like: S -> ( S ) S | ε
        """
        rule = rule.strip()

        if "->" not in rule:
            raise ValueError("Invalid rule format! Must contain '->'.")

        left, right = rule.split("->")
        left = left.strip()

        # Split RHS alternatives
        alternatives = right.split("|")

        productions = []
        for alt in alternatives:
            symbols = alt.strip().split()
            productions.append(symbols)

        # Add to grammar
        if left not in self.grammar:
            self.grammar[left] = []

        self.grammar[left].extend(productions)

    def get_grammar(self):
        return self.grammar




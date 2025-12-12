from .parse_tree import ParseTreeNode

class CFGParser:
    """
    Top-down recursive descent parser with backtracking.
    """

    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.input_string = ""
        self.derivations = []
        self.tokens = []


    def parse(self, tokens):
        """Parse a string and return (accepted, parse_tree)."""

        self.tokens = tokens
        self.derivations = []

        success, node, next_index = self._parse_symbol(self.start_symbol, 0)
         # Accept only if all tokens are consumed
        if success and next_index == len(self.tokens):
            return True, node
        return False, None

    def _parse_symbol(self, symbol, index):
        """
        Attempts to parse a symbol starting at string[index].
        Returns: (success, ParseTreeNode, new_index)
        """

        node = ParseTreeNode(symbol)

        # Terminal
        if symbol not in self.grammar:
            if index < len(self.tokens) and self.tokens[index] == symbol:
                return True, node, index + 1
            return False, None, index

        # Non-terminal
        for production in self.grammar[symbol]:

            temp_index = index
            temp_node = ParseTreeNode(symbol)
            success = True

            for sym in production:
                if sym == "ε":
                    continue

                ok, child_node, temp_index = self._parse_symbol(sym, temp_index)
                if not ok:
                    success = False
                    break
                temp_node.add_child(child_node)

            if success:
                return True, temp_node, temp_index

        return False, None, index


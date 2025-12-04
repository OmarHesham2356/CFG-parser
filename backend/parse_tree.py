class ParseTreeNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def to_dict(self):
        """Export as JSON-like dictionary for visualization."""
        return {
            "symbol": self.symbol,
            "children": [c.to_dict() for c in self.children]
        }


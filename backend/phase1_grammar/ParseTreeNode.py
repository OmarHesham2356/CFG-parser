from typing import List, Optional
from .Production import Production, EPSILON


class ParseTreeNode:
    def __init__(self, symbol: str, children: Optional[List['ParseTreeNode']] = None, 
                production: Optional[Production] = None):
        """
        Args:
            symbol: Terminal or nonterminal symbol
            children: Child nodes (None for leaf terminals)
            production: The production used to expand this node (None for terminals)
        """
        self.symbol = symbol
        self.children = children if children is not None else []
        self.production = production  # Which production was used to create this node
    
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def is_terminal(self) -> bool:
        return self.production is None
    
    def height(self) -> int:
        if self.is_leaf():
            return 1
        return 1 + max((c.height() for c in self.children), default=0)
    
    def pretty_print(self, prefix: str = "", is_last: bool = True, is_root: bool = True):
        """
        Pretty print the parse tree using ASCII box-drawing characters.
        """
        # Define the visual connector for this node
        if is_root:
            connector = ""
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            # Prepare the prefix for children of THIS node
            # If this node is the last child, its children don't need a vertical bar
            new_prefix = prefix + ("    " if is_last else "│   ")

        # Print the current node
        print(f"{prefix}{connector}{self.symbol}")
        
        # Recursively print children
        count = len(self.children)
        for i, child in enumerate(self.children):
            # Check if this child is the last one in the list
            is_last_child = (i == count - 1)
            # Pass the calculated prefix down
            child.pretty_print(new_prefix, is_last_child, is_root=False)   
    
    def get_tree_str(self, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
        # Determine connector and prefix
        if is_root:
            connector = ""
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")

        # Build the current line
        result = f"{prefix}{connector}{self.symbol}\n"

        # Recursively build children
        count = len(self.children)
        for i, child in enumerate(self.children):
            is_last_child = (i == count - 1)
            result += child.get_tree_str(new_prefix, is_last_child, is_root=False)
            
        return result

    def pretty_print(self):
        print(self.get_tree_str())
        
    def __repr__(self) -> str:
        """Compact representation"""
        
        if self.is_leaf():
            return str(self.symbol)
        children_str = ' '.join(str(c) for c in self.children)
        return f"({self.symbol} {children_str})"
    
    def __str__(self) -> str:
        return self.__repr__()

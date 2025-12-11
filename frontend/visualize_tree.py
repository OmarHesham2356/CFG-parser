import sys
import os
import graphviz

# Add backend to path so we can import phase1_grammar
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..', 'backend'))

from phase1_grammar import ParseTreeNode

def generate_tree_graph(node: ParseTreeNode) -> graphviz.Digraph:
    """
    Converts a ParseTreeNode into a Graphviz Digraph.
    """
    # 1. Initialize the graph
    dot = graphviz.Digraph(comment='Parse Tree')
    dot.attr(rankdir='TB')  # Top to Bottom layout
    
    # Counter for unique node IDs
    counter = 0
    
    # Internal recursive function
    def add_nodes(current_node, parent_id=None):
        nonlocal counter
        node_id = str(counter)
        counter += 1
        
        # Style the node
        if current_node.is_terminal():
            dot.node(node_id, current_node.symbol, shape='box', style='filled', fillcolor='lightgrey')
        else:
            dot.node(node_id, current_node.symbol, shape='ellipse')
        
        # Connect to parent
        if parent_id is not None:
            dot.edge(parent_id, node_id)
        
        # Recursively handle children
        for child in current_node.children:
            add_nodes(child, node_id)
            
    # 2. Build the graph (only if tree exists)
    if node:
        add_nodes(node)
        
    # 3. CRITICAL: Return the graph object
    return dot

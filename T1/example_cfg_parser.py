
# cfg_parser.py
from typing import List, Dict, Tuple, Optional
import itertools
import uuid


class ParseNode:
    """
    Node in the parse tree.
    symbol: grammar symbol (terminal or nonterminal)
    children: list of ParseNode
    production: the production (list of symbols) used to expand this nonterminal (None for terminals)
    """
    def __init__(self, symbol: str, children: Optional[List["ParseNode"]] = None, production: Optional[List[str]] = None):
        self.symbol = symbol
        self.children = children or []
        self.production = production  # None if terminal or leaf; otherwise the RHS used (list of symbols)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def __repr__(self):
        return f"ParseNode({self.symbol!r}, children={len(self.children)}, prod={self.production})"


class Parser:
    """
    Top-down backtracking parser for a context-free grammar.
    Grammar representation:
        grammar: Dict[str, List[List[str]]]
            maps nonterminal -> list of productions
            each production is a list of symbols (terminals are single-char strings or multi-char tokens)
            epsilon production is represented by an empty list [].
    start_symbol: str (e.g., 'S')
    """

    def __init__(self, grammar: Dict[str, List[List[str]]], start_symbol: str = "S"):
        self.grammar = grammar
        self.start_symbol = start_symbol
        # Quick helper to tell if symbol is nonterminal:
        self.nonterminals = set(grammar.keys())

    def parse(self, text: str) -> Tuple[bool, Optional[ParseNode]]:
        """
        Try to parse the whole text. Returns (accepted, parse_tree_root_or_None).
        """
        results = self._parse_nonterminal(self.start_symbol, text, 0)
        # results: list of tuples (node, next_pos)
        for node, pos in results:
            if pos == len(text):
                return True, node
        return False, None

    def _parse_nonterminal(self, nt: str, text: str, pos: int) -> List[Tuple[ParseNode, int]]:
        """
        Try to parse nonterminal 'nt' starting at text[pos].
        Returns list of (node, new_pos) for each successful expansion.
        """
        results: List[Tuple[ParseNode, int]] = []
        if nt not in self.grammar:
            return results

        productions = self.grammar[nt]
        # Try productions in order
        for prod in productions:
            # prod is list of symbols (terminals or nonterminals). epsilon -> prod == []
            if len(prod) == 0:
                # epsilon production
                node = ParseNode(nt, children=[], production=prod)
                results.append((node, pos))
                continue

            # We'll build a list of lists: for each symbol in prod, possible (node, pos) matches.
            # Start with a single empty match at current pos.
            partial_matches: List[Tuple[List[ParseNode], int]] = [ ([], pos) ]
            failed = False

            for symbol in prod:
                new_partial: List[Tuple[List[ParseNode], int]] = []
                for children_so_far, cur_pos in partial_matches:
                    if symbol in self.nonterminals:
                        # expand nonterminal
                        expansions = self._parse_nonterminal(symbol, text, cur_pos)
                        for child_node, new_pos in expansions:
                            new_children = children_so_far + [child_node]
                            new_partial.append((new_children, new_pos))
                    else:
                        # terminal symbol: we treat symbol as a string (can be multi-char)
                        term = symbol
                        term_len = len(term)
                        if text[cur_pos:cur_pos+term_len] == term:
                            leaf = ParseNode(term)  # terminal leaf
                            new_children = children_so_far + [leaf]
                            new_partial.append((new_children, cur_pos + term_len))
                        # else no match for this path
                # update partial_matches for next symbol
                partial_matches = new_partial
                if not partial_matches:
                    failed = True
                    break

            if failed:
                continue

            # For each successful full-match build the parent node
            for children, final_pos in partial_matches:
                node = ParseNode(nt, children=children, production=prod)
                results.append((node, final_pos))

        return results


def leftmost_derivation_steps(root: ParseNode) -> List[str]:
    """
    Reconstruct leftmost derivation steps using the parse tree.
    We produce a sequence of sentential forms, starting from start symbol,
    expanding the leftmost nonterminal at each step following the tree's productions.
    """
    # Represent sentential form as list of symbols (terminals and nonterminals)
    sentential = [root.symbol]

    # We need a mapping from node objects to their productions/children.
    # Walk tree in leftmost order and expand nodes as encountered.
    steps = ["".join(sentential)]  # initial sentential form

    # We'll perform repeated expansions: find leftmost nonterminal in sentential,
    # find the corresponding node in the tree in left-to-right order, and replace it.
    # To find nodes in left-to-right order we traverse tree and yield nodes in that order.
    def traverse_left_to_right(node: ParseNode):
        yield node
        for child in node.children:
            if child.symbol in root_productions_nonterminals:
                # child may be nonterminal; continue traversal
                yield from traverse_left_to_right(child)
            else:
                # terminal leaf yields itself only
                yield child

    # Quick set of nonterminals from root's grammar presence
    # but we don't have grammar here: detect nonterminals as nodes with production != None
    def is_nonterminal_symbol(sym: str, node: ParseNode) -> bool:
        return node.production is not None

    # We'll map node ids to positions as we traverse.
    # Instead, iterative expansion algorithm:
    def expand_once(sentential_symbols: List[str], node: ParseNode) -> Tuple[List[str], Optional[ParseNode]]:
        """
        Expand the leftmost nonterminal symbol in sentential_symbols using the next node from tree traversal.
        Returns (new_sentential, the node that was expanded) or (sentential, None) if no nonterminal.
        """
        # Find index of leftmost nonterminal in sentential_symbols by comparing with tree structure
        # We'll perform a simultaneous walk over the parse tree and the sentential form.
        # Use a stack: tuples (node, pos_in_sentential)
        # pos_in_sentential indicates where this node's symbol begins in sentential_symbols
        stack = [(node, 0)]
        # We will build a list of nodes in left-to-right corresponding to sentential_symbols.
        node_list = []

        def collect(node: ParseNode):
            node_list.append(node)
            for child in node.children:
                collect(child)

        collect(node)
        # Build a linear sequence of symbols from the tree (terminals and nonterminals as nodes)
        tree_symbols = []
        for n in node_list:
            tree_symbols.append(n)

        # Now find leftmost node in tree_symbols whose production is not None -> a nonterminal
        for n in tree_symbols:
            if n.production is not None:
                # Expand this node: replace its symbol occurrence in sentential_symbols with its production's symbols
                # Find the first occurrence of n.symbol in sentential_symbols (leftmost)
                for idx, sym in enumerate(sentential_symbols):
                    if sym == n.symbol:
                        # build replacement list: if production is empty -> epsilon -> remove symbol
                        replacement = list(n.production)  # may be []
                        new_sent = sentential_symbols[:idx] + replacement + sentential_symbols[idx+1:]
                        return new_sent, n
                # if not found, continue
        return sentential_symbols, None

    # Build initial sentential as list (terminals/nonterminals are single-character strings in our design)
    sent = [root.symbol]
    steps = ["".join(sent)]
    while True:
        new_sent, expanded_node = expand_once(sent, root)
        if expanded_node is None:
            break
        steps.append("".join(new_sent) if new_sent else "ε")
        sent = new_sent

    return steps


class Visualizer:
    """
    Produces a Graphviz DOT representation of the parse tree (no dependency on graphviz Python lib).
    You can render the produced `.dot` file using Graphviz command line: dot -Tpng tree.dot -o tree.png
    """

    def __init__(self):
        self.node_id_counter = itertools.count()

    def _new_id(self):
        return f"n{uuid.uuid4().hex[:8]}"

    def to_dot(self, root: ParseNode, graph_name: str = "ParseTree") -> str:
        lines = [f'digraph "{graph_name}" {{', "  node [shape=plain];"]
        # assign ids
        id_map = {}

        def dfs(node: ParseNode):
            nid = self._new_id()
            id_map[id(node)] = nid
            label = node.symbol
            # if node is nonterminal and has production, show production as a small note
            if node.production is not None:
                # display production in the label for clarity
                rhs = "".join(node.production) if node.production else "ε"
                label = f"{node.symbol} → {rhs}"
            # escape quotes
            label = label.replace('"', '\\"')
            lines.append(f'  {nid} [label="{label}"];')
            for child in node.children:
                child_id = dfs(child)
                lines.append(f'  {nid} -> {child_id};')
            return nid

        dfs(root)
        lines.append("}")
        return "\n".join(lines)

    def write_dot(self, root: ParseNode, filename: str):
        dot = self.to_dot(root)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(dot)


# Example: balanced parentheses grammar (non-left-recursive)
def example_balanced_parentheses_grammar() -> Dict[str, List[List[str]]]:
    # S -> '(' S ')' S | ε
    return {
        "S": [
            ["(", "S", ")", "S"],
            []  # epsilon
        ]
    }


# CLI-like helper
def run_example(text: str):
    grammar = example_balanced_parentheses_grammar()
    parser = Parser(grammar, start_symbol="S")
    accepted, tree = parser.parse(text)
    if accepted:
        print(f"Input '{text}' => ACCEPTED")
        # print parse tree as indented
        def print_tree(node: ParseNode, depth=0):
            indent = "  " * depth
            if node.production is None:
                print(f"{indent}{node.symbol}")  # terminal
            else:
                rhs = "".join(node.production) if node.production else "ε"
                print(f"{indent}{node.symbol} -> {rhs}")
                for c in node.children:
                    print_tree(c, depth+1)
        print_tree(tree)
        # derivation
        deriv = leftmost_derivation_steps(tree)
        print("\nLeftmost derivation steps:")
        for step in deriv:
            print("  " + step)
        # write dot file
        vis = Visualizer()
        dotfile = "parse_tree.dot"
        vis.write_dot(tree, dotfile)
        print(f"\nDOT file written to: {dotfile} (render with: dot -Tpng {dotfile} -o tree.png)")
    else:
        print(f"Input '{text}' => REJECTED")


if __name__ == "__main__":
    # quick manual tests
    tests = ["", "()", "()()", "(())", "(()())", "(()", "())(", "(()))("]
    for t in tests:
        run_example(t)
        print("-" * 40)

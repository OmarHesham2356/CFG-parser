import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, '..', 'backend')
sys.path.append(backend_path)

import streamlit as st
import pandas as pd
from phase1_grammar import Production
from main import LR1ParserBuilder
from visualize_tree import generate_tree_graph 

st.set_page_config(page_title="LR(1) Parser Generator", layout="wide")
st.title("LR(1) Parser Generator")
st.markdown("### Interactive Parser for Context-Free Grammars")

# --- Sidebar: Grammar Input ---
with st.sidebar:
    st.header("1. Define Grammar")
    st.info("Format: LHS -> RHS | ... (one rule per line)")
    
    # Default grammar (Dangling Else)
    default_grammar = """E -> E + F | F
F -> F * G | G
G -> ( E ) | id
    """
    
    grammar_input = st.text_area("Enter Productions:", value=default_grammar, height=200)
    
    start_symbol = st.text_input("Start Symbol:", value="E")
    
    build_btn = st.button("Build Parser")

# --- Main Logic ---
if build_btn or 'parser' in st.session_state:
    try:
        # Parse the grammar input
        productions = []
        prod_id = 1
        
        # Process lines
        lines = [line.strip() for line in grammar_input.split('\n') if line.strip()]
        
        for line in lines:
            if "->" not in line:
                st.error(f"Invalid format: {line}")
                st.stop()
                
            lhs, rhs_part = line.split("->", 1)
            lhs = lhs.strip()
            alternatives = rhs_part.split("|")
            
            for alt in alternatives:
                alt = alt.strip()
                symbols = [] if alt in ["epsilon", "ε", ""] else alt.split()
                productions.append(Production(lhs, symbols, prod_id))
                prod_id += 1
        
        # Build the Parser
        builder = LR1ParserBuilder(productions, start_symbol, verbose=False)
        parser = builder.build()
        st.session_state['parser'] = parser
        st.session_state['table_builder'] = builder.table_builder
        
        st.success("Parser built successfully!")
        
        # --- Display Parser Info ---
        tab1, tab2, tab3 = st.tabs(["Parsing", "Action/Goto Tables", "Item Sets"])
        
        with tab1:
            st.subheader("Test Input")
            test_input = st.text_input("Enter tokens (space separated):", value="id + id * id")
            
            if test_input:
                tokens = test_input.split()
                try:
                    tree, derivation, error = parser.parse(tokens)
                    
                    if error:
                        st.error(f"Parse Error: {error}")
                        st.markdown("**Partial Derivation:**")
                        st.code("\n".join(derivation))
                    else:
                        st.success("Accepted!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Derivation Steps:**")
                            # Format derivation as a numbered list
                            deriv_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(derivation)])
                            st.text_area("Derivation", deriv_text, height=400)
                            
                        with col2:
                            st.markdown("**Parse Tree:**")
                            
                            # 1. ASCII Tree (Keep it as text option)
                            with st.expander("View as ASCII Text"):
                                st.code(tree.get_tree_str())
                            
                            # 2. Graphviz Tree (Visual)
                            try:
                                dot = generate_tree_graph(tree)
                                st.graphviz_chart(dot)
                            except Exception as e:
                                st.error(f"Graphviz Error: {e}")
                                st.info("Make sure Graphviz is installed on your system (sudo pacman -S graphviz)")                           
                
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")

        with tab2:
            st.subheader("Parsing Table")
            
            # Convert Action Table to DataFrame for display
            action_table = builder.table_builder.action_table
            goto_table = builder.table_builder.goto_filled
            
            # Get all states and symbols
            states = sorted(list(set(k[0] for k in action_table.keys()) | set(k[0] for k in goto_table.keys())))
            terminals = sorted(list(set(k[1] for k in action_table.keys())))
            nonterminals = sorted(list(set(k[1] for k in goto_table.keys())))
            
            # Build Data structure for DataFrame
            data = []
            for s in states:
                row = {'State': s}
                for t in terminals:
                    act = action_table.get((s, t))
                    row[t] = str(act) if act else ""
                for n in nonterminals:
                    goto = goto_table.get((s, n))
                    row[n] = str(goto) if goto is not None else ""
                data.append(row)
            
            df = pd.DataFrame(data).set_index("State")
            st.dataframe(df)
            
            # Show conflicts if any
            if builder.table_builder.conflicts:
                st.warning(f"Conflicts Detected: {len(builder.table_builder.conflicts)}")
                for conf in builder.table_builder.conflicts:
                    st.write(f"- State {conf.state} on '{conf.symbol}': {conf.conflict_type}")

        with tab3:
            st.subheader("LR(1) Item Sets")
            item_sets = builder.item_builder.item_sets
            for i, items in enumerate(item_sets):
                with st.expander(f"State {i}"):
                    for item in sorted(items):
                        st.text(str(item))

    except Exception as e:
        st.error(f"Builder Error: {e}")
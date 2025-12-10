# CFG Parser

````markdown
# LR(1) Parser Generator 🌳

A robust, interactive **Canonical LR(1) Parser Generator** built with Python and Streamlit. This tool accepts Context-Free Grammars (CFGs), computes First/Follow sets, builds LR(1) item sets, generates parsing tables with conflict detection, and visualizes the resulting parse tree.

## ✨ Features

* **Canonical LR(1) Algorithm:** Implements the full LR(1) state machine (not just SLR or LALR).
* **Conflict Detection:** Automatically identifies and reports **Shift-Reduce** and **Reduce-Reduce** conflicts.
* **Interactive Web Interface:** Built with **Streamlit** for easy grammar input and testing.
* **Visual Parse Trees:** Generates high-quality parse tree diagrams using **Graphviz**.
* **Step-by-Step Derivation:** Shows the exact derivation sequence used to parse the input.
* **Modular Architecture:** Clean separation between the parsing backend and the visualization frontend.
* **CLI Support:** Includes a terminal-based interface for quick testing.

## 📂 Project Structure

```text
CFG-parser/
├── backend/                  # Core Parsing Logic
│   ├── phase1_grammar.py     # Grammar & Production structures
│   ├── phase2_first_follow.py# FIRST & FOLLOW set computation
│   ├── phase3_lr1_items.py   # Canonical Collection of LR(1) Items (Closure/Goto)
│   ├── phase4_lr1_table.py   # ACTION and GOTO Table generation
│   ├── phase5_lr1_parser.py  # The Parser Engine
│   └── main.py               # CLI Entry point & Builder class
├── frontend/                 # User Interface
│   ├── app.py                # Streamlit Web Application
│   └── visualize_tree.py     # Graphviz Visualization Logic
└── requirements.txt          # Python dependencies
````

## 🚀 Installation

### 1\. Clone the Repository

```bash
git clone [https://github.com/OmarHesham2356/CFG-parser.git](https://github.com/OmarHesham2356/CFG-parser.git)
cd CFG-parser
git checkout "LR(1)"  # Ensure you are on the correct branch
```

### 2\. Install System Dependencies (Graphviz)

This project requires the Graphviz system library to render parse trees.

* **Arch Linux / Manjaro / CachyOS:**

    ```bash
    sudo pacman -S graphviz
    ```

* **Ubuntu / Debian:**

    ```bash
    sudo apt-get install graphviz
    ```

* **macOS:**

    ```bash
    brew install graphviz
    ```

* **Windows:** Download the installer from the [Graphviz website](https://graphviz.org/download/) and add it to your PATH.

### 3\. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 🖥️ Usage

### Web Application (Recommended)

Run the interactive web interface:

```bash
streamlit run frontend/app.py
```

This will open the tool in your browser (usually at `http://localhost:8501`).

1. **Define Grammar:** Enter your productions in the sidebar (e.g., `S -> A`).
2. **Build Parser:** Click the button to generate the parsing tables.
3. **Test Input:** Go to the "Parsing" tab, enter a token string, and see the result.
4. **Visualize:** View the Parse Tree and Derivation steps.

### Command Line Interface (CLI)

You can also run the parser directly in your terminal:

```bash
python3 backend/main.py
```

## 📝 Example Grammars

### 1\. Dangling Else (Ambiguity Test)

This grammar tests conflict detection. The parser defaults to SHIFT (standard convention).

```text
S -> i C t S | i C t S e S | a
C -> b
```

*Test Input:* `i b t i b t a e a`

### 2\. Simple Arithmetic

```text
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

*Test Input:* `id + id * id`

## 🛠️ Phases Explained

1. **Grammar Parsing:** Validates inputs and augments the grammar (`S' -> S`).
2. **First & Follow:** Computes lookahead sets using a fixed-point iteration algorithm.
3. **Item Sets:** Builds the Canonical Collection of LR(1) items using `Closure` and `Goto` operations.
4. **Table Construction:** Populates the ACTION and GOTO tables. Detects conflicts here.
5. **Parsing:** The engine processes input tokens using a stack-based shift-reduce approach.

## 📄 License

[MIT License](https://www.google.com/search?q=LICENSE)

```
```

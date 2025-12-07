# CFG Parser

---

A parser that checks the balance of parenthesis.

## Parser

- Input: String of balanced or unbalanced parenthesis.
- Output: Parse tree or error message.

### Parser Grammar

$$
S \to (S) | SS | \epsilon
$$

### Parser Output Example

For the string `(())`:

```python
parse_tree = {
  "S": {
    "(": None,
    "S": {
      "(": None,
      "S": None,
      ")": None
    },
    ")": None
  }
}
```

## Visualization

- Input: Parser output (parse tree).
- Output: Output parse tree graph.

### Example Visualization

For the string `(())`:

# Commenting & Docstrings

**Python:**
- **Format:** Google style ([reference](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings))
- **Enforcement:** Ruff with `pydocstyle` rule
- **Config:**
```toml
[lint]
extend-select = ["D"]

[lint.pydocstyle]
convention = "google"
```
- **Required for:** All public functions, classes, and modules

**JavaScript/TypeScript:**
- **Format:** JSDoc with TypeScript annotations
- **Enforcement:** ESLint with `eslint-plugin-jsdoc`
- **Config:**
```js
{
  plugins: ["jsdoc"],
  rules: {
    "jsdoc/require-description": "error",
    "jsdoc/require-param": "error",
    "jsdoc/require-returns": "error"
  }
}
```
- **Required for:** All exported functions, classes, and types

**When to document:**
- Every public function/method (including test helpers)
- Classes with non-trivial state
- Complex business logic
- API route handlers (brief summary + params)

**When to skip:**
- Private helpers under 5 lines
- Simple type aliases
- Test assertions (test names serve as documentation)

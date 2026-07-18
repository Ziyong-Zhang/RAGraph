> Context: The Streamlit app is crashing with a white screen on Chapter 5. The Chrome DevTools console reveals the root cause: `Uncaught SyntaxError: Unexpected identifier 's'`. This is caused by an unescaped apostrophe (`'`) in the character alias "German Lady's Maid" breaking the JavaScript string injection in the HTML template.

> STRICT RULES:
> 1. ALL code, comments, docstrings, and commit messages MUST be strictly in English.
> 2. Focus on `frontend/app.py`.

Please execute the following fixes to ensure robust JavaScript string escaping:

### Task 1: Fix JSON Injection Syntax (app.py)
In `frontend/app.py`, locate the HTML string where the Cytoscape.js component is initialized.
- Ensure you are converting the Python dict to a JSON string safely: `safe_json = json.dumps(graph_data)`
- **CRITICAL FIX:** Inside the JavaScript `<script>` block, inject the JSON string **DIRECTLY** as an object literal. DO NOT wrap it in single or double quotes, and DO NOT use `JSON.parse`.
  
  **WRONG:** `const data = JSON.parse('{safe_json}');`
  **WRONG:** `const data = JSON.parse('{json.dumps(graph_data)}');`
  
  **CORRECT:** 
  
```javascript
  const graphData = {safe_json}; // Injected directly as a JS object
  

```

*(Note: Replace `{safe_json}` with your actual f-string interpolation variable).*

### Task 2: Clean up Cytoscape Stylesheet Warnings

The Chrome console is also throwing warnings: `The style property 'shadow-blur: 8' is invalid`.
In the Cytoscape initialization options inside `frontend/app.py`, locate the `style` array.

* Remove all invalid CSS-like shadow properties inside Cytoscape element styles (e.g., remove `shadow-blur`, `shadow-color`, `shadow-offset-x`, `shadow-offset-y`). Cytoscape does not use standard CSS box-shadow syntax.

Run the Streamlit app. The apostrophe in "Lady's Maid" should no longer crash the JavaScript engine, and the graph should render perfectly.

> Context: We need to refine the Entity Resolution (ER) and LLM Extraction prompts. The LLM is incorrectly extracting relational nouns (like "母親") as aliases, and failing to extract proper formal titles (like "奎雷夫人" / Mrs. Crale) as aliases. This causes the Python deterministic ER to fail because there is no string intersection between "卡蘿琳．奎雷" and "奎雷夫人".

> STRICT RULES:
> 1. ALL code, comments, docstrings, and commit messages MUST be strictly in English. No Chinese characters in the code.
> 2. Maintain strict separation of concerns.

Please execute the following updates:

### Task 1: Prompt Hardening for Aliases (extractor.py)
In `backend/core/extractor.py`, drastically tighten the System Prompt regarding Aliases:
- Add a strict definition: "An 'Alias' MUST ONLY be a proper noun, an alternative formal name, a nickname, or a Title + Surname combination (e.g., 'Mrs. Crale', 'Poirot', 'Captain Hastings')."
- Add a strict negative constraint: "NEVER extract relational roles, pronouns, or generic identifiers as aliases. Words like '母親' (mother), '妻子' (wife), '哥哥' (brother), '那個男人' (that man) are strictly FORBIDDEN in the aliases list. Put relationship information in the `description`."
- Add a specific instruction for married characters: "If a female character is referred to by her husband's surname with a title (e.g., '奎雷夫人' / Mrs. Crale), you MUST explicitly include '奎雷夫人' in her aliases list."

### Task 2: String Normalization in Deterministic ER (graph_builder.py or entity_resolver.py)
In the Python function `resolve_and_merge_entities`:
- Create a helper function `normalize_name(name: str) -> str` inside the module.
- This function should:
  1. Convert to lowercase.
  2. Strip leading/trailing whitespaces.
  3. Remove all spaces within the string.
  4. Remove various Chinese separator dots frequently used in translated names: `name.replace("．", "").replace("·", "").replace("•", "")`.
- Update the matching logic (Name-to-Name, Name-to-Alias, Alias-to-Alias) to ALWAYS use the output of `normalize_name(string)` before comparing. This ensures "卡蘿琳．奎雷", "卡蘿琳·奎雷", and "卡蘿琳奎雷" evaluate as exact matches.

### Task 3: Testing
- Write a Pytest in `tests/test_er.py` to verify the normalization:
  - Node 1: Name "卡蘿琳．奎雷", Aliases ["奎雷夫人"]
  - Node 2: Name "奎雷夫人", Aliases []
  - Node 3: Name "卡蘿琳·奎雷" (different dot), Aliases []
  - Assert they all merge into a single node successfully.
- Run `uv run pytest tests/ -v`.
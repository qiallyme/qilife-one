# fileflow/rules.py

def get_naming_prompt():
    return """
Use this format:
[entity]_[type or document kind]_[reference or number]_[main date]_[optional date or tag]

Guidelines:
1. DO NOT start with the date.
2. Entity or subject (e.g., IRS, Chase, Amazon) comes first.
3. Type should describe what the file is (invoice, statement, log, report, etc.)
4. Use underscores between words.
5. Avoid generic words like 'file', 'document', 'scan'.
6. Keep it 5–7 tokens max when possible.
7. Respond with only the filename, no extension, no explanation.
"""

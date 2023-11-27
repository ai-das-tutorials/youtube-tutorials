# Add Semantic Search to Large Codebase

Check out the full tutorial on [Youtube](https://www.youtube.com/watch?v=QaUMkZQ5TrA&t=46s)

## Prerequisites

- Python 3.9 or higher
- "pipenv" as package manager
- am empty file called "main.py" and folder "./temp" in the project root

```
pip install pipenv
pipenv install tree_sitter openai chromadb
```

## Project Setup
Clone and build tree-sitter-python under ./temp

```
cd temp
git clone https://github.com/tree-sitter/tree-sitter-python.git
```

## Run Script

Clone your code base under ./temp to enable semantic search on it.

```
python main.py
```


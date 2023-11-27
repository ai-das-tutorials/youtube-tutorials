import os, glob

def get_all_file_paths(folder: str, extension: str = "py"):
    """
    Function to recursively iterate over a folder and look for files with a specific extension
    """
    search_pattern = os.path.join(folder, "**", f"*.{extension}")
    for file_path in glob.iglob(search_pattern, recursive=True):
        yield file_path


from tree_sitter import Language, Parser

def get_tree_sitter_parser() -> Parser:
    """
    Function to initialize tree-sitter parser as described in
    https://github.com/tree-sitter/py-tree-sitter
    """
    # clone python language grammar under "temp"
    # https://github.com/tree-sitter/tree-sitter-python
    grammarPath = "temp/tree-sitter-python"

    # execute build
    buildPath = "temp/my-python-tree-sitter-build.so"
    Language.build_library(buildPath, [grammarPath])

    # initialize parser
    parser = Parser()
    parser.set_language(Language(buildPath, "python"))
    return parser


def get_all_function_definitions(file_path: str):
    """
    Iteratively find each function in the given file and
    yield function names and corresponding function text.
    """
    # Step 1: read and parse file content
    tree_parser = get_tree_sitter_parser()
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    parsed_file = tree_parser.parse(bytes(content, "utf-8"))
    
    # Step 2: at the root-level, look for all function definitions 
    main_node = parsed_file.root_node
    func_nodes = [
        _ for _ in main_node.named_children if _.type == "function_definition"
    ]

    # Step 3: iterate over each function definition to get its name and code
    for fn in func_nodes:
        for nc in fn.named_children:
            if nc.type == "identifier":
                #     👇 function name        👇 function code
                yield nc.text.decode("utf-8"), fn.text.decode("utf-8")


import openai
openai.api_key = "your-key"  # note: bad practice ⚠️⚠️⚠️

def explain_func_text_ai(func_text: str):
    """
    Function to get explanation for python code using AI (GPT-3.5)
    """
    prompt = f"""
        You are an expert python programmer, 
        please explain the following code: 
        {func_text}"""

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
    

import chromadb

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="codebase_functions")

def index_to_chroma_db(func_name: str, func_text: str, file_path:str):
    """
    Function to create vector embedding for a given function text
    and store it in chroma-db along with its metadata.
    """
    function_explanation = explain_func_text_ai(func_text)
    
    collection.add(
        documents=[function_explanation],
        metadatas=[{
            "func_name": func_name, 
            "func_text": func_text, 
            "file_path": file_path,
        }],
        ids=[str(hash(f"{file_path}{func_name}"))], # could use a better id generator
    )


if __name__ == "__main__":
    # Clone your project under "temp" dir
    # if you dont have a python project in mind - clone "pyGameMath" from github for learning purpose

    project_path = "temp\pyGameMath"

    for file_path in get_all_file_paths(project_path):
        iter_func_defs = get_all_function_definitions(file_path)

        for func_name, func_text in iter_func_defs:
            index_to_chroma_db(func_name, func_text, file_path)
         

    # search on code base using natural language 
    results = collection.query(
        query_texts=["Your query here ..."],
        n_results=5,
    )

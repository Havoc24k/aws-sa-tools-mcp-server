import os
from . import mcp


@mcp.tool(
    name="list-local-folder",
    description="""
    List all folders in the path

    Returns:
        dict: A list containing the names of all folders in the path folder.
    """
)
def list_local_folder(path: str) -> list:
    # Get a list of all folders in the ~/projects folder
    return os.listdir(os.path.expanduser(path))


@mcp.tool(
    name="read-local-folder",
    description="""
    Read all code files in the path and return the content as aa response an LLM can understand.

    Returns:
        str: A string containing the content of all code files in the path folder.
    """
)
def read_local_folder(path: str) -> str:
    code_extensions = ('.mjs', '.tf')
    # Read all files recursively in the path
    content = ""
    for root, _, files in os.walk(os.path.expanduser(path)):
        for file in files:
            # Read the content of the file only if it is a code file
            # Ignore node_modules, .git, .terraform, and .idea folders
            if 'node_modules' in root or '.git' in root or '.terraform' in root or '.idea' in root:
                continue
            if file.endswith(code_extensions):
                with open(os.path.join(root, file), 'r') as f:
                    content += f"\n\n# {file}\n\n"
                    content += f.read() + "\n"
                    content += "\n\n"

    return content

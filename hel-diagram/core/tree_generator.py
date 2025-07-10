import os

def generate_tree(path, prefix=""):
    entries = sorted(os.listdir(path))
    result = ""
    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "├── " if index < len(entries) - 1 else "└── "

        if os.path.isdir(full_path):
            icon = "📁 "
        else:
            icon = "📄 "

        result += prefix + connector + icon + entry + "\n"

        if os.path.isdir(full_path):
            new_prefix = prefix + ("│   " if index < len(entries) - 1 else "    ")
            result += generate_tree(full_path, new_prefix)
    return result

def generate_tree_diagram(folder_path):
    root = os.path.basename(folder_path.rstrip("/\\"))
    diagram = "📁 " + root + "/\n"
    diagram += generate_tree(folder_path)
    return diagram

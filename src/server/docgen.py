import os
import shutil
import subprocess
import sys
import stat
from git import Repo
import markdown

def on_rm_error(func, path, exc_info):
    """Error handler for shutil.rmtree to handle read-only files on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def is_python_repo(repo_path: str) -> bool:
    """Return True if the repo contains any .py files."""
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.py'):
                return True
    return False

def is_js_repo(repo_path: str) -> bool:
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.js') or file.endswith('.ts'):
                return True
    return False

def detect_language(repo_path: str) -> str:
    if is_python_repo(repo_path):
        return 'python'
    if is_js_repo(repo_path):
        return 'javascript'
    return 'unknown'

def build_file_tree(root_path: str, rel_path: str = ""):
    tree = []
    full_path = os.path.join(root_path, rel_path)
    for entry in sorted(os.listdir(full_path)):
        entry_path = os.path.join(full_path, entry)
        entry_rel = os.path.join(rel_path, entry)
        if os.path.isdir(entry_path):
            tree.append({
                'type': 'dir',
                'name': entry,
                'path': entry_rel.replace('\\', '/'),
                'children': build_file_tree(root_path, entry_rel)
            })
        else:
            tree.append({
                'type': 'file',
                'name': entry,
                'path': entry_rel.replace('\\', '/')
            })
    return tree

def render_readme_html(repo_path: str) -> str:
    readme_path = None
    for name in ["README.md", "readme.md", "Readme.md"]:
        candidate = os.path.join(repo_path, name)
        if os.path.exists(candidate):
            readme_path = candidate
            break
    if readme_path:
        with open(readme_path, encoding='utf-8') as f:
            return markdown.markdown(f.read())
    return ""

def clone_repo(repo_url: str, dest_dir: str) -> str:
    """
    Clone the given GitHub repo URL into dest_dir. Returns the path to the cloned repo.
    """
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, onerror=on_rm_error)
    Repo.clone_from(repo_url, dest_dir)
    return dest_dir

def generate_sphinx_docs(repo_path: str, docs_output_dir: str) -> bool:
    """
    Generate Sphinx HTML docs for the given repo_path. Output to docs_output_dir.
    Returns True if successful, False otherwise.
    """
    if not is_python_repo(repo_path):
        print("Not a Python repo. Skipping Sphinx doc generation.")
        return False
    docs_dir = os.path.join(repo_path, 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        # Quickstart Sphinx (non-interactive)
        try:
            subprocess.run([
                sys.executable, '-m', 'sphinx.cmd.quickstart', '--quiet', '--project', 'Project', '--author', 'Author',
                '--sep', '--ext-autodoc', '--makefile', '--no-batchfile', docs_dir
            ], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print("Sphinx quickstart failed!")
            print("Return code:", e.returncode)
            print("Output:\n", e.output)
            print("Error:\n", e.stderr)
            return False
    # Add autodoc config if not present
    conf_py = os.path.join(docs_dir, 'conf.py')
    if os.path.exists(conf_py):
        with open(conf_py, 'a', encoding='utf-8') as f:
            f.write("\nextensions.append('sphinx.ext.autodoc')\n")
            f.write("extensions.append('sphinx_autodoc_typehints')\n")
            f.write("import os, sys\nsys.path.insert(0, os.path.abspath('..'))\n")
    # Generate autodoc .rst if not present
    index_rst = os.path.join(docs_dir, 'index.rst')
    if os.path.exists(index_rst):
        with open(index_rst, 'a', encoding='utf-8') as f:
            f.write("\n.. automodule:: main\n    :members:\n")
    # Build HTML docs
    try:
        subprocess.run([
            sys.executable, '-m', 'sphinx', '-b', 'html', docs_dir, docs_output_dir
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Sphinx build failed!")
        print("Return code:", e.returncode)
        print("Output:\n", e.output)
        print("Error:\n", e.stderr)
        return False 
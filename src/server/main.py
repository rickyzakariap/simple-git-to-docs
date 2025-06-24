# If you see import errors, run: pip install -r requirements.txt
import os
import socket
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .docgen import clone_repo, generate_sphinx_docs, build_file_tree, detect_language, render_readme_html

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request, error: str = ""):
    return templates.TemplateResponse("index.jinja", {"request": request, "error": error})

@app.post("/generate", response_class=HTMLResponse)
def generate_docs(request: Request, input_text: str = Form(...)):
    repo_url = input_text.strip()
    if not repo_url.startswith("https://github.com/"):
        return templates.TemplateResponse("index.jinja", {"request": request, "error": "Invalid GitHub URL."})
    repo_name = repo_url.rstrip('/').split('/')[-1]
    clone_path = os.path.join(BASE_DIR, "_repos", repo_name)
    docs_output_dir = os.path.join(BASE_DIR, "static", "docs", repo_name)
    try:
        clone_repo(repo_url, clone_path)
        file_tree = build_file_tree(clone_path)
        language = detect_language(clone_path)
        readme_html = render_readme_html(clone_path)
        doc_link = None
        doc_success = False
        if language == 'python':
            doc_success = generate_sphinx_docs(clone_path, docs_output_dir)
            if doc_success:
                doc_link = f"/static/docs/{repo_name}/index.html"
                # Get local IP for sharing
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return templates.TemplateResponse("doc_url_result.jinja", {
                    "request": request,
                    "repo_url": repo_url,
                    "doc_link": doc_link,
                    "local_ip": local_ip
                })
        # TODO: Add JS/JSDoc support here in the future
        return templates.TemplateResponse("result.jinja", {
            "request": request,
            "repo_url": repo_url,
            "file_tree": file_tree,
            "readme_html": readme_html,
            "doc_link": doc_link,
            "language": language
        })
    except Exception as e:
        return templates.TemplateResponse("index.jinja", {"request": request, "error": f"Error: {e}"})

@app.get("/docs/{repo_name}", response_class=HTMLResponse)
def docs_stub(request: Request, repo_name: str):
    return templates.TemplateResponse("docs_stub.jinja", {"request": request, "repo_name": repo_name})

@app.get("/file", response_class=PlainTextResponse)
def get_file(request: Request, repo: str = Query(...), path: str = Query(...)):
    # Only allow files inside the specified repo
    repo_root = os.path.join(BASE_DIR, "_repos", repo)
    abs_path = os.path.abspath(os.path.join(repo_root, path))
    if not abs_path.startswith(repo_root) or not os.path.isfile(abs_path):
        print(f"File not found or access denied: repo={repo}, path={path}, abs_path={abs_path}")
        return PlainTextResponse(f"File not found or access denied.\nrepo={repo}\npath={path}\nabs_path={abs_path}", status_code=404)
    with open(abs_path, encoding='utf-8', errors='replace') as f:
        return PlainTextResponse(f.read())

# Run the FastAPI app using Python's `-m` flag
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server.main:app", host="0.0.0.0", port=8000, reload=True)
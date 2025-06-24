# 🚀 Git to Docs (Local Edition)

Turn any GitHub repository into beautiful, browsable documentation—served right from your own computer! No cloud, no S3, just fast local docs for any repo.

---

## ✨ Features
- 🖥️ Clean, modern, and responsive UI (Tailwind CSS)
- 📥 Enter any GitHub repo URL to generate docs
- 🐍 Python repos: auto-generate Sphinx docs
- 🌐 All repos: browse files, view README, explore code
- 📋 Copy/share docs URL for your local network
- 🔒 100% local—no cloud or internet upload required

---

## 🛠️ Setup & Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/git-to-doc.git
   cd git-to-doc
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install python-multipart
   ```
3. **Run the server:**
   ```sh
   python -m uvicorn src.server.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Open in your browser:**
   [http://localhost:8000/](http://localhost:8000/)

---

## 📡 How to Share on Your Local Network
- Find your local IP address (e.g., `192.168.1.10`).
- Access the app from any device on your WiFi:
  ```
  http://192.168.1.10:8000/
  ```
- After generating docs, share the docs URL (e.g., `http://192.168.1.10:8000/static/docs/your-repo/index.html`).
- **Note:** Your server must stay running for others to access the docs.

---

## 📸 Screenshot

> Add a screenshot of your app here (e.g. `screenshot.png`)

---

## 🙏 Credits
- Inspired by [@git-to-doc](https://github.com/filiksyos/gittodoc)
- Built with [FastAPI](https://fastapi.tiangolo.com/), [Jinja2](https://jinja.palletsprojects.com/), and [Tailwind CSS](https://tailwindcss.com/)

---

## 📄 License

MIT 
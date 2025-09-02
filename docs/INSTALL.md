# 📦 Cross-Platform Installation Guide

## 🚀 Quick Install (Copy & Paste)

### macOS / Linux
```bash
git clone https://github.com/yourusername/Project-Synapse.git && \
cd Project-Synapse && \
python3 -m venv .venv && \
source .venv/bin/activate && \
pip install -r requirements.txt && \
cp .env.template .env && \
echo "✅ Done! Add your Gemini API key to .env file"
```

### Windows (PowerShell)
```powershell
git clone https://github.com/yourusername/Project-Synapse.git; `
cd Project-Synapse; `
python -m venv .venv; `
.venv\Scripts\Activate; `
pip install -r requirements.txt; `
copy .env.template .env; `
Write-Host "✅ Done! Add your Gemini API key to .env file"
```

### Windows (Command Prompt)
```cmd
git clone https://github.com/yourusername/Project-Synapse.git && ^
cd Project-Synapse && ^
python -m venv .venv && ^
.venv\Scripts\activate.bat && ^
pip install -r requirements.txt && ^
copy .env.template .env && ^
echo Done! Add your Gemini API key to .env file
```

## 🔑 Add Your API Key

1. Get free API key: https://ai.google.dev/
2. Open `.env` file in any text editor
3. Replace `your_gemini_api_key_here` with your actual key
4. Save the file

## ✅ Test Installation

```bash
python main.py "Driver stuck in traffic"
```

## 💡 Platform-Specific Notes

| Platform | Python Command | Path Separator | Activate venv |
|----------|---------------|----------------|---------------|
| macOS    | `python3`     | `/`            | `source .venv/bin/activate` |
| Linux    | `python3`     | `/`            | `source .venv/bin/activate` |
| Windows  | `python`      | `\`            | `.venv\Scripts\activate` |

## 🆘 Common Issues

**"python not found"**: Use `python3` on Mac/Linux, `python` on Windows

**"No module named synapse"**: Make sure virtual environment is activated

**"API key not set"**: Check `.env` file exists and contains your key

**Still stuck?** See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed help.
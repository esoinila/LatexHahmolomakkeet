# RPG Character Generator

A robust tool for generating professional LaTeX character sheets and name signs from simple Markdown bios. Now featuring **AI-powered image generation**.

## 🚀 Quick Links
- [**Getting Started**](docs/GettingStarted.md) - Setup and installation instructions.
- [**Character Creation**](docs/CharacterCreation.md) - How to write character files and use AI prompts.
- [**System Architecture**](docs/Architecture.md) - Under the hood details.

## ✨ Features
- **Markdown Source**: Write character stats and lore in plain text.
- **Auto-Formatting**: Automatic conversion to high-quality PDF via LaTeX.
- **AI Integration**: Automatically generates character portraits using Google Gemini (Imagen) if a local image is missing.
- **Batch Processing**: Generates sheets for all characters in your folder at once.

## 📂 Project Structure
```text
LatexHahmolomakkeet_/
├── Characters/         # Put your character .md files here
├── images/             # Character portraits (auto-generated or manual)
├── Output/             # Generated PDFs appear here
├── System/             # Source code and templates
└── Generate.ps1        # Main script to run everything
```

## 🛠️ Usage
Simply run the script:
```powershell
.\Generate.ps1
```

---
*Created for the "Nano Banana" Tabletop System.*

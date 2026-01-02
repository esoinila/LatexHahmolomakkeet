# Getting Started

## Prerequisites
- **.NET 8.0 SDK**: Required to build and run the generator.
- **LaTeX Distribution**: `pdflatex` must be installed and in your PATH (e.g., TeX Live or MiKTeX).
- **Google API Key**: Required for automatic image generation.

## Installation & Setup

1.  **Clone the Repository**
    ```powershell
    git clone <repository-url>
    cd LatexHahmolomakkeet_
    ```

2.  **Configure API Key (User Secrets)**
    To enable AI image generation, you must set your Google Gemini API key using .NET User Secrets. This keeps your key safe and out of source control.
    ```powershell
    cd System/Generator
    dotnet user-secrets init
    dotnet user-secrets set "Gemini:ApiKey" "YOUR_API_KEY_HERE"
    ```
    *Note: Get a free API key from [Google AI Studio](https://aistudio.google.com/).*

3.  **Restore Dependencies**
    ```powershell
    dotnet restore
    ```

## Running the Generator

The easiest way to generate character sheets is using the automation script.

1.  **Open PowerShell** in the root directory.
2.  **Run the script**:
    ```powershell
    .\Generate.ps1
    ```

### What Happens?
1.  The script compiles the C# generator.
2.  It scans the `Characters/` folder for `.md` files.
3.  It checks `images/` for matching portraits.
    - If an image is missing, it attempts to generate one via Gemini API.
    - If API fails, it uses a fallback placeholder.
4.  It generates `.tex` files in `System/Temp/`.
5.  It compiles them into PDFs using `pdflatex`.
6.  Final PDFs are placed in `Output/`.

[Return to Home](../README.md)

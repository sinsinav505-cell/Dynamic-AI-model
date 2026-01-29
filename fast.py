import os
import sys
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = FastAPI()

active_bot_process = None

class ChatbotRequest(BaseModel):
    description: str

def extract_code(text, language):
    marker = f"```{language}"
    if marker in text:
        start = text.find(marker) + len(marker)
        end = text.find("```", start)
        return text[start:end].strip()
    return None

def install_required_packages(requirements_text):
    """Installs missing packages without touching existing ones."""
    if not requirements_text:
        return

    # Map import names to install names
    package_mapper = {
        "sklearn": "scikit-learn", 
        "opencv": "opencv-python",
        "PIL": "Pillow"
    }
    
    # Parse and clean names
    raw_packages = [pkg.strip().lower() for pkg in requirements_text.split('\n') if pkg.strip()]
    packages_to_install = [package_mapper.get(p, p) for p in raw_packages]

    if packages_to_install:
        print(f"📦 Verifying/Installing: {packages_to_install}")
        try:
            # We use 'pip install' without uninstalling anything.
            # Pip handles the 'already satisfied' check automatically.
            subprocess.check_call([sys.executable, "-m", "pip", "install", *packages_to_install])
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Installation failed for some packages: {e}")

@app.post("/create-and-run")
def create_and_run(req: ChatbotRequest):
    global active_bot_process

    # Kill the previous chatbot window
    if active_bot_process and active_bot_process.poll() is None:
        active_bot_process.terminate()
        active_bot_process.wait()

    prompt = (f"Create a Streamlit chatbot. Description: {req.description}. "
              "Return ONLY: ```python_bot``` and ```requirements```.")

    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    bot_code = extract_code(response.text, "python_bot")
    reqs_text = extract_code(response.text, "requirements") or ""
    
    # 1. Install what's missing (Synchronous)
    install_required_packages(reqs_text)

    # 2. Launch the new code
    if bot_code:
        file_path = "generated_bot.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(bot_code)
        
        # Windows detached process flag
        active_bot_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", file_path, "--server.port", "8502", "--server.headless", "true"],
            creationflags=0x00000008,
            close_fds=True
        )
        
        return {"status": "success", "message": "Packages ready and Bot launched!", "code": bot_code}
    
    return {"status": "error", "message": "AI failed to generate code."}
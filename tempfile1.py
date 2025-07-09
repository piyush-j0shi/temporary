import os
import logging
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, UploadFile, File, HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url = "https://integrate.api.nvidia.com/v1",
)

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def extract_text(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")
    extension = file.filename.lower().split('.')[-1]
    
    if extension == "txt":
        content = file.file.read()
        return content.decode("utf-8")
    
    elif extension == "pdf":
        return extract_text_from_pdf(file.file)
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .txt and .pdf are allowed.")

def nemotron(context: str, question: str) -> str:
    try:
        response = client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-70b-instruct",
            messages=[
                {"role": "system", "content": "You are an expert assistant. Always provide answers in markdown format."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ],
            temperature=0.5
        )
        content = response.choices[0].message.content
        
        if content is None:
            raise HTTPException(status_code=500, detail="Nothing.")
        return content

    except OpenAIError as e:
        logger.exception("NVIDIA API error")
        raise HTTPException(status_code=500, detail=f"NVIDIA API error: {str(e)}")

    except Exception:
        logger.exception("Unexpected error in nemotron()")
        raise HTTPException(status_code=500, detail="Unexpected error")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), question: str = "What is the main topic?"):
    try:
        text = extract_text(file)
    
    except Exception as e:
        logger.exception("Error during text extraction")
        raise HTTPException(status_code=400, detail=str(e))
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file.")
    
    truncated_context = text[:3000]
    try:
        answer = nemotron(truncated_context, question)
    
    except Exception:
        logger.exception("Error during nemotron call")
        raise
    return JSONResponse(content={"answer": answer})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

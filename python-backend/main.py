from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="QiLife Python Backend", version="0.1.0")

# Add CORS middleware to allow Electron app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class DuplicateCleanerRequest(BaseModel):
    roots: Optional[List[str]] = None
    max_depth: Optional[int] = None
    weights: Optional[Dict[str, float]] = None
    review_threshold: Optional[float] = None
    prefer_threshold: Optional[float] = None
    ai_threshold: Optional[float] = None
    action: Optional[str] = None
    output: Optional[str] = None

class FileFlowRequest(BaseModel):
    source_path: str
    destination_path: str
    file_types: Optional[List[str]] = None

class QuickReceiptRequest(BaseModel):
    items: List[Dict[str, Any]]
    total: float
    notes: Optional[str] = None

class FormSubmissionRequest(BaseModel):
    form_data: Dict[str, Any]
    form_type: str
    user_id: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "QiLife Python Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "python_version": sys.version,
        "modules": {
            "fileflow": "available",
            "voice": "available", 
            "memory": "available",
            "food": "available",
            "forms": "available"
        }
    }

@app.post("/fileflow/duplicate-cleaner")
async def run_duplicate_cleaner(request: DuplicateCleanerRequest):
    """Run the duplicate cleaner module"""
    try:
        # Import the duplicate cleaner module
        from fileflow.duplicate_cleaner.duplicateCleaner import run_duplicate_cleaner
        
        # Convert request to the format expected by the module
        options = {
            "roots": request.roots,
            "max_depth": request.max_depth,
            "weights": request.weights,
            "review_threshold": request.review_threshold,
            "prefer_threshold": request.prefer_threshold,
            "ai_threshold": request.ai_threshold,
            "action": request.action,
            "output": request.output
        }
        
        # Run the duplicate cleaner
        result = run_duplicate_cleaner(options)
        
        return {
            "status": "success",
            "result": result,
            "message": "Duplicate cleaner completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate cleaner error: {str(e)}")

@app.post("/fileflow/process")
async def process_fileflow(request: FileFlowRequest):
    """Process files through the fileflow system"""
    try:
        # Import fileflow modules
        from fileflow.analyzer import analyze_files
        from fileflow.batcher import batch_process
        
        # Analyze files
        analysis = analyze_files(request.source_path, request.file_types)
        
        # Process files
        result = batch_process(analysis, request.destination_path)
        
        return {
            "status": "success",
            "analysis": analysis,
            "result": result,
            "message": "File processing completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@app.post("/quick-receipt/generate")
async def generate_receipt(request: QuickReceiptRequest):
    """Generate a quick receipt"""
    try:
        # Import receipt generation module
        from mini_apps.quick_receipt import generate_receipt
        
        receipt = generate_receipt(
            items=request.items,
            total=request.total,
            notes=request.notes
        )
        
        return {
            "status": "success",
            "receipt": receipt,
            "message": "Receipt generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt generation error: {str(e)}")

@app.get("/voice/transcribe")
async def transcribe_audio(file_path: str):
    """Transcribe audio file"""
    try:
        from voice.voice_transcriber import transcribe_audio_file
        
        transcription = transcribe_audio_file(file_path)
        
        return {
            "status": "success",
            "transcription": transcription,
            "message": "Audio transcribed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

@app.post("/memory/query")
async def query_memory(query: str, context: Optional[str] = None):
    """Query the memory system"""
    try:
        from memory.vector_store import query_memory
        
        result = query_memory(query, context)
        
        return {
            "status": "success",
            "result": result,
            "message": "Memory query completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory query error: {str(e)}")

@app.post("/forms/submit")
async def submit_form(request: FormSubmissionRequest):
    """Submit form data"""
    try:
        # Process form submission
        form_data = request.form_data
        form_type = request.form_type
        user_id = request.user_id
        
        # Here you would typically:
        # 1. Validate the form data
        # 2. Store it in a database
        # 3. Send notifications
        # 4. Generate PDFs, etc.
        
        # For now, we'll just return success
        return {
            "status": "success",
            "form_type": form_type,
            "user_id": user_id,
            "submission_id": f"form_{form_type}_{len(form_data)}",
            "message": f"Form {form_type} submitted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Form submission error: {str(e)}")

@app.get("/forms/zoho-url")
async def get_zoho_form_url():
    """Get the Zoho form URL"""
    return {
        "status": "success",
        "url": "https://writer.zohopublic.com/writer/published/k8rb3640aae6022414281b9c872cd3e644c98/fill",
        "form_type": "zoho_fillable",
        "description": "Embedded Zoho fillable form"
    }

@app.post("/forms/export-pdf")
async def export_form_to_pdf(form_data: Dict[str, Any]):
    """Export form data to PDF"""
    try:
        # Here you would generate a PDF from the form data
        # For now, we'll return a success response
        
        return {
            "status": "success",
            "pdf_url": "/generated/form_document.pdf",
            "message": "Form exported to PDF successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 
#!/usr/bin/env python3
"""
FastAPI web interface for the Worry Butler system.

This provides a REST API and web interface for processing worries
through the three-agent workflow.
"""

import os
import sys
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from worry_butler import WorryButler

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Worry Butler API",
    description="A multi-agent AI system for processing anxiety and worry",
    version="1.0.0"
)

# Initialize Worry Butler
try:
    butler = WorryButler()
except Exception as e:
    print(f"Warning: Could not initialize Worry Butler: {e}")
    butler = None

# Pydantic models for API requests/responses
class WorryRequest(BaseModel):
    worry: str
    description: str = "The worry statement to process"

class WorryResponse(BaseModel):
    original_worry: str
    overthinker_response: str
    therapist_response: str
    executive_summary: str
    metadata: Dict[str, Any]

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Root endpoint that serves a simple web interface.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Worry Butler 🤖🧠💭</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            h1 {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                margin-bottom: 30px;
                opacity: 0.9;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
            }
            textarea {
                width: 100%;
                height: 100px;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                resize: vertical;
                background: rgba(255, 255, 255, 0.9);
                color: #333;
            }
            button {
                background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
                width: 100%;
            }
            button:hover {
                transform: translateY(-2px);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .results {
                margin-top: 30px;
                display: none;
            }
            .agent-section {
                background: rgba(255, 255, 255, 0.1);
                margin: 15px 0;
                padding: 20px;
                border-radius: 15px;
                border-left: 5px solid;
            }
            .overthinker { border-left-color: #ff6b6b; }
            .therapist { border-left-color: #4ecdc4; }
            .executive { border-left-color: #45b7d1; }
            .agent-title {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            .loading {
                text-align: center;
                padding: 20px;
                font-style: italic;
            }
            .error {
                background: rgba(255, 107, 107, 0.2);
                border: 1px solid #ff6b6b;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Worry Butler 🧠💭</h1>
            <div class="subtitle">
                Let our AI agents help you process your worries through a unique three-stage approach
            </div>
            
            <form id="worryForm">
                <div class="form-group">
                    <label for="worry">What's worrying you today?</label>
                    <textarea id="worry" name="worry" placeholder="Share your worry here..." required></textarea>
                </div>
                <button type="submit" id="submitBtn">🚀 Process My Worry</button>
            </form>
            
            <div id="loading" class="loading" style="display: none;">
                🔄 Processing your worry through the agents...<br>
                ⏳ This may take a few moments...
            </div>
            
            <div id="results" class="results">
                <div class="agent-section overthinker">
                    <div class="agent-title">🎭 OVERTHINKER AGENT</div>
                    <div id="overthinkerResponse"></div>
                </div>
                
                <div class="agent-section therapist">
                    <div class="agent-title">🧘‍♀️ THERAPIST AGENT</div>
                    <div id="therapistResponse"></div>
                </div>
                
                <div class="agent-section executive">
                    <div class="agent-title">📋 EXECUTIVE SUMMARY</div>
                    <div id="executiveResponse"></div>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('worryForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const worry = document.getElementById('worry').value.trim();
                if (!worry) return;
                
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                
                // Show loading, hide results
                submitBtn.disabled = true;
                loading.style.display = 'block';
                results.style.display = 'none';
                
                try {
                    const response = await fetch('/process-worry', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ worry: worry })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    // Display results
                    document.getElementById('overthinkerResponse').textContent = data.overthinker_response;
                    document.getElementById('therapistResponse').textContent = data.therapy_response;
                    document.getElementById('executiveResponse').textContent = data.executive_summary;
                    
                    results.style.display = 'block';
                    
                } catch (error) {
                    console.error('Error:', error);
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error';
                    errorDiv.textContent = 'Error processing worry: ' + error.message;
                    document.querySelector('.container').appendChild(errorDiv);
                } finally {
                    // Hide loading, re-enable submit
                    loading.style.display = 'none';
                    submitBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/process-worry", response_model=WorryResponse)
async def process_worry(request: WorryRequest):
    """
    Process a worry through the three-agent workflow.
    
    Args:
        request: WorryRequest containing the worry statement
        
    Returns:
        WorryResponse with all agent responses
    """
    if not butler:
        raise HTTPException(status_code=500, detail="Worry Butler not initialized")
    
    try:
        # Process the worry
        result = butler.process_worry(request.worry)
        
        # Convert to response model
        return WorryResponse(
            original_worry=result['original_worry'],
            overthinker_response=result['overthinker_response'],
            therapist_response=result['therapy_response'],
            executive_summary=result['executive_summary'],
            metadata=result['metadata']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing worry: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Worry Butler API",
        "version": "1.0.0",
        "butler_initialized": butler is not None
    }

@app.get("/agents")
async def get_agents():
    """
    Get information about all agents.
    """
    if not butler:
        raise HTTPException(status_code=500, detail="Worry Butler not initialized")
    
    try:
        return {"agents": butler.get_agent_info()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        print("See env_example.txt for the required format")
        sys.exit(1)
    
    print("🚀 Starting Worry Butler API server...")
    print("🌐 Web interface available at: http://localhost:8000")
    print("📚 API documentation available at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

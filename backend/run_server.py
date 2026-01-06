import uvicorn
import sys

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

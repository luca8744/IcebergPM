import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory is the project root
    print("Avvio di IcebergPM...")
    print("Accedi a http://localhost:8000")
    print("Admin iniziale: admin / admin123")
    
    # Disable reload in frozen mode
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # In frozen mode, we import the app object directly
        from backend.app.main import app
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False
        )
    else:
        # In development mode, we use the string for hot-reload support
        uvicorn.run(
            "backend.app.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True
        )

#!/usr/bin/env python3
"""
Script alternativo para iniciar el servidor FastAPI desde el directorio API
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    # Inicializar servidor FastAPI
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_dirs=["."],
    )
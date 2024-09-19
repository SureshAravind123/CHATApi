# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import pyodbc
import re

app = FastAPI()
        
        

@app.get("/getresponse")
    return "hi"
    
   
    

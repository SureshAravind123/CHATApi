# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import pyodbc
import re

app = FastAPI()


@app.get("/get")
async def get_response():
    # Define the prompt with dynamic user input
    return "Hello!"
    

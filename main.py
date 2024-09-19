# Import necessary modules
from fastapi import FastAPI

# Create an instance of the FastAPI app
app = FastAPI()

# Define a route for the root endpoint
@app.get("/")
async def generate_response():
    # Return the response as a JSON-compatible format (e.g., dictionary)
    return "hi"

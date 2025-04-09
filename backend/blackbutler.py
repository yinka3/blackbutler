import json
import os
from dotenv import load_dotenv
import uvicorn as uvicorn
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv('GEMINI_KEY'))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "https://black-innovators.onrender.com"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
    expose_headers=["websocket-extensions", "sec-websocket-extensions", "sec-websocket-key", "sec-websocket-accept"],
)

prompt_context = """You are an AI Assistant called Black Butler. Your goal is to provide
accurate information to users based on the black engineers they are asking about. If domain knowledge
is not sufficient, web search information based on user's prompt. If possible give
them additional links about the engineer for them to learn more about them. The responses should always try to be kept within 150
tokens.
"""

# Create a model with the system instruction
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-001",
    generation_config={
        "temperature": 0.5,
        "max_output_tokens": 1000,
        "stop_sequences": ["Have a good day", "Bye", "Thank you bye"]
    },
    safety_settings={
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE"
    }
)

# Create a chat session with the system instruction
chat = model.start_chat(history=[])
# Add system instruction as the first message
chat.send_message(prompt_context)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Black Butler API is running"}

@app.websocket("/ws/blackbutler")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            engineer = data["engineer"]
            prompt = data["prompt"]

            text_prompt = f"""The user is asking about the following engineer: {engineer}
            User's question: {prompt}

            Provide a response as Black Butler.
            """

            response = chat.send_message(text_prompt)
            
            await websocket.send_text(json.dumps({"response": response.text}))

    except WebSocketDisconnect:
        print("Client disconnected.")
        

if __name__ == "__main__":
    uvicorn.run("blackbutler:app", host="127.0.0.1", port=8000, reload=True)
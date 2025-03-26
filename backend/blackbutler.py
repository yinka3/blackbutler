from collections import defaultdict
import json
import os
from typing import Dict, Text
from dotenv import load_dotenv
import uvicorn as uvicorn
from google import genai
from google.genai import types
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

model = genai.Client(api_key=os.getenv('GEMINI_KEY'))

prompt_context = """You are an AI Assistant called Black Butler. Your goal is to provide
accurate information to users based on the black engineers they are asking about. If domain knowledge
is not sufficient, web search information based on user's prompt. If possible give
them additional links about the engineer for them to learn more about them.
"""


chat = model.chats.create(
    model="gemini-2.0-flash-001",
    config=types.GenerateContentConfig(
        system_instruction=prompt_context,
        temperature=0.2,
        max_output_tokens=100,
        stop_sequences=["Have a good day", "Bye", "Thank you bye"],
        safety_settings= [
            types.SafetySetting(
                category='HARM_CATEGORY_HATE_SPEECH',
                threshold='BLOCK_MEDIUM_AND_ABOVE'),
        ]
    )
)

# TODO: Have some starting prompt for people who are using the chat bot 
starting_prompt = []

history = defaultdict(list)
def lowercase(words):
    return ''.join(word.lower() for word in words)

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

            response = chat.send_message(message=text_prompt)
            history[engineer].append((prompt, response.text))

            await websocket.send_text(json.dumps({"response": response.text}))

    except WebSocketDisconnect:
        print("Client disconnected.")
        

if __name__ == "__main__":
    uvicorn.run("blackbutler:app", host="127.0.0.1", port=8000, reload=True)

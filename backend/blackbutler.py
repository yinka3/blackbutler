import os
from dotenv import load_dotenv
import uvicorn as uvicorn
from google import genai
from google.genai import types
from fastapi import FastAPI, Request
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
accurate information to users based on the engineers they are asking about. If domain knowledge
is not sufficient, web search information based on user's prompt. If possible give
them additional links about the engineer for them to learn more about them.
"""

def lowercase(words):
    return ''.join(word.lower() for word in words)


@app.post("/query_model")
async def query(request: Request):
    data = await request.json()
    engineer = data["engineer"]
    prompt = data["prompt"]

    text_prompt = f"""The user is asking about the following engineer: {engineer}
    User's question: {prompt}

    Provide a response as Black Butler.
    """

    response = model.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=text_prompt,
        config=types.GenerateContentConfig(
            system_instruction=prompt_context,
            tools=[
                types.Tool(google_search=types.GoogleSearch())],
            temperature=0.2,
            top_p=1.5,
            max_output_tokens=100,
            stop_sequences=["Have a good day", "Bye", "Thank you bye"],
            safety_settings= [
                types.SafetySetting(
                    category='HARM_CATEGORY_HATE_SPEECH',
                    threshold='BLOCK_MEDIUM_AND_ABOVE'),
            ]
        )
    )

    return {"response": response.text}


if __name__ == "__main__":
    uvicorn.run("blackbutler:app", host="127.0.0.1", port=8000, reload=True)

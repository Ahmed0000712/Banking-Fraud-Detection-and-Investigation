
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def explain_prediction(details):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "GPT is unavailable. Please configure your API key."

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-6.2-sol"),
        instructions="""
        You are a banking fraud investigation assistant.

        Explain the supplied ML prediction in simple language.
        Identify the suspicious indicators provided.
        Suggest practical investigation steps.

        Do not change or override the ML prediction.
        Do not claim that fraud is proven.
        Use only the supplied transaction information.
        """,
        input=json.dumps(details)
    )

    return response.output_text

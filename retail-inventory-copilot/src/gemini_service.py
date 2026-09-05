import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    client = None
else:
    client = genai.Client(api_key=API_KEY)


def ask_gemini(question, evidence):
    """
    Send the user's question and verified Python analytics
    to Gemini for explanation and recommendation.
    """

    if client is None:
        return (
            "Gemini API key is not configured. "
            "Please add your GEMINI_API_KEY to the .env file."
        )

    prompt = f"""
You are a Retail Sales and Inventory Copilot.

You help a retail store manager understand sales and inventory.

IMPORTANT RULES:

1. Use ONLY the verified evidence provided below.
2. Never invent numbers, products, suppliers, dates, or business facts.
3. Do not assume information that is not present in the evidence.
4. If the available evidence cannot answer the question, clearly say:
   "The available data is insufficient to answer this question."
5. If the question asks about information that does not exist in the
   provided data, explicitly identify the missing information.
6. Give a concise recommendation when the evidence supports one.
7. Include the actual numbers that support your answer.
8. Clearly distinguish facts from assumptions.
9. End every useful answer with an "Evidence" line identifying the
   relevant data source(s), such as:
   sales.csv, stock.csv, products.csv, or stores.csv.
10. Do not claim to have information from a source that is not provided.

Manager's question:
{question}

Verified evidence calculated by the Python analytics system:
{evidence}

Answer format:

Answer:
Give a direct answer to the manager.

Evidence:
Mention the important numbers and the relevant data source(s).

Recommended action:
Give a practical action supported by the evidence.
If no reliable action can be recommended, say so.

Now answer the manager's question.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as error:
        return f"Unable to get a Gemini response: {error}"
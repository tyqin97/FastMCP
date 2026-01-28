from fastmcp import FastMCP, Context
from fastmcp.prompts import Message
from dotenv import load_dotenv
from functools import lru_cache

import os, random, json, openai, asyncio,sqlite3, requests

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets", ".env"))

mcp = FastMCP("Main Server for MCP")
openai = openai.OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")

@mcp.tool
def roll_dice(num_dice: int = 1, num_sides: int = 6) -> list[int]:
    return [random.randint(1, num_sides) for _ in range(num_dice)]

@mcp.tool
def get_user_info(user_id: int) -> dict:
    conn = sqlite3.connect(os.getenv("SQLITE3_PATH"))
    try:
        cur = conn.cursor()
        sql = "SELECT id, name, email FROM users WHERE id = ?"
        cur.execute(sql, (user_id,))
        result = cur.fetchone()
        return { "id":result[0], "name":result[1], "email":result[2] }
    finally : conn.close()
    
@mcp.resource("vector://fastmcp-info")
def get_kb_vector_store_id() -> str:
    return os.getenv("OPENAI_VS_FASTMCP")

@mcp.resource("file://llms-full", annotations={"readOnlyHint": True})
def get_llms_file() -> str:
    with open("db/llms-full.txt", "r", encoding="utf-8") as f:
        return f.read()
    
@mcp.prompt
def fastmcp_related_prompt(question:str) -> list[Message]:
    """Only route to this function if the question is related"""
    return [
        Message(
            role="assistant",
            content=(
                "Answer the question.\n"
                "When file_search returns relevant excerpts, prefer those over general knowledge.\n"
                "If the retrieved content is insufficient, just say no idea.\n"
                "Do not hallucinate. Be clear and practical."
            ),
        ),
        Message(role="user", content=question),
    ]

def _call_openai(msg) -> str:
    respond = openai.responses.create(
        model=os.getenv("OPENAI_MODEL"),
        input=msg
    )
    return respond.output_text

# Responses API expects content to be string or array of objects, not a single object
def _content_to_str(c):
    return c.text if hasattr(c, "text") else (c if isinstance(c, str) else str(c))
    
@mcp.tool
async def ask_llm(prompt: str, ctx: Context):
    respond = await ctx.read_resource("vector://fastmcp-info")
    vs_id = respond[0].content.strip()
    
    pr = await ctx.get_prompt("fastmcp_related_prompt", {"question": prompt})
    messages = [{"role": m.role, "content": _content_to_str(m.content)} for m in pr.messages]

    if vs_id:
        tools = [{"type": "file_search", "vector_store_ids": [vs_id]}]
        resp = openai.responses.create(
            model=os.getenv("OPENAI_MODEL"),
            input=messages,
            tools=tools
        )

    return resp.output_text

@mcp.tool
def get_all_football_country() -> dict:
    url = "https://api.football-data.org/v4/areas"
    result = requests.get(url)
    result.raise_for_status()
    return result.json()

@mcp.tool
def get_football_by_id(id: str) -> dict:
    """Get a football area by ID. Pass the area id as a string (e.g. \"2072\")."""
    url = f"https://api.football-data.org/v4/areas/{id}"
    result = requests.get(url)
    result.raise_for_status()
    return result.json()

if __name__ == "__main__":
    mcp.run()
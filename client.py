from fastmcp import Client
from rich.console import Console
from rich.markdown import Markdown
import asyncio

def show(text):
    try:
        Console().print(text)
    except Exception:
        print(text)

client = Client("http://localhost:8000/mcp")

async def tool_list():
    async with client:
        list_tools = await client.list_tools()
        for tool in list_tools: show(tool.name)
        return list_tools
        
async def roll_dice(n_dice: int):
    async with client:
        results = await client.call_tool("roll_dice",{"num_dice":n_dice})
        for res in results.data : show(results.data)
        return results
    
async def get_one_user_info(user_id: int):
    async with client:
        result = await client.call_tool("get_user_info", {"user_id":user_id})
        show(result)
        return result.data
    
async def ask_question(prompt:str):
    async with client:
        result = await client.call_tool("ask_llm", {"prompt": prompt})
        show(Markdown(result.content[0].text))
    
if __name__ == "__main__":
    # asyncio.run(tool_list())
    # asyncio.run(roll_dice(6))
    # asyncio.run(get_one_user_info(1))
    asyncio.run(ask_question("I want to know how to setup FastMCP Server."))
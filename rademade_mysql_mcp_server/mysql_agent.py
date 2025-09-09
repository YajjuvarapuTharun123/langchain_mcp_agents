import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq



load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


async def main():
    client = MultiServerMCPClient(
        {
            "mysql": {
                "command": "uvx",
                "args": ["--from", "mysql-mcp-server", "mysql_mcp_server"],
                "transport": "stdio",
                "env": {
                    "MYSQL_HOST": MYSQL_HOST,
                    "MYSQL_PORT": MYSQL_PORT,
                    "MYSQL_USER": MYSQL_USER,
                    "MYSQL_PASSWORD": MYSQL_PASSWORD,
                    "MYSQL_DATABASE": MYSQL_DATABASE,
                },
            }
        }
    )

    print("Loading MCP tools...")
    tools = await client.get_tools()
    print(f"Loaded tools: {[tool.name for tool in tools]}")

    model = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
    agent = create_react_agent(model, tools)


    system_prompt = (
        "You are a SQL assistant. Only answer questions related to the table 'tharun111'. "
        "Do not reference any other tables. If the user asks about non-existing tables, "
        "inform them politely that only 'tharun111' is available."
    )


    user_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Show all data in the table"}
    ]

    response = await agent.ainvoke({"messages": user_messages})
    print("Agent Response:", response['messages'][-1].content)


    user_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "how many rows are there in the table?"}
    ]

    response_count = await agent.ainvoke({"messages": user_messages})
    print("Row Count Response:", response_count['messages'][-1].content)


if __name__ == "__main__":
    asyncio.run(main())

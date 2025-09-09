import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
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

app = FastAPI(title="SQL MCP Agent API")

class QueryRequest(BaseModel):
    query: str

agent = None

SYSTEM_PROMPT = (
    "You are a SQL assistant. Only answer questions related to the table 'tharun111'. "
    "Do not reference any other tables. If the user asks about non-existing tables, "
    "inform them politely that only 'tharun111' is available."
)

async def init_agent():
    global agent
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

    tools = await client.get_tools()
    model = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")
    agent = create_react_agent(model, tools)
    print("Agent initialized!")

# Initialize agent on server startup
@app.on_event("startup")
async def startup_event():
    await init_agent()

@app.post("/query")
async def query_agent(request: QueryRequest):
    global agent
    user_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request.query}
    ]

    response = await agent.ainvoke({"messages": user_messages})
    return {"response": response['messages'][-1].content}

@app.get("/health")
def health_check():
    return {"status": "running"}

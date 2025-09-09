# Rademade MySQL MCP Server

A FastAPI-based MCP (Multi-Server Control Protocol) agent for MySQL, built using **LangChain MCP adapters**, **LangGraph**, and **ChatGroq**. This agent provides an API to interact with a SQL database and answer queries related to a specific table.

The project has been **tested using Postman** for API requests.

---

## Features

- Connects to a MySQL database via MCP server.
- Agent only answers questions about the table `tharun111`.
- Returns polite responses if a query references other tables.
- Exposes REST API endpoints:
  - `POST /query` – Ask a query to the SQL agent.
  - `GET /health` – Check server health status.

---

## Prerequisites

- Python 3.10+
- MySQL server
- Environment variables configured in `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
GROQ_API_KEY=your_groq_api_key

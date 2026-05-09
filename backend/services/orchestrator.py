"""
AI Orchestrator — OpenAI GPT-4o function-calling agentic loop.
This is the most important file in the codebase.
Runs a multi-turn loop dispatching tool calls until GPT produces a final answer.
"""

import json
import time
import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel
from config import settings
from services.sql_tool import query_sql, QUERY_TEMPLATES
from services.rag_tool import search_documents
from services.csv_tool import analyze_csv, METRICS, DIMENSIONS
from services.chart_tool import generate_chart, ChartSpec

logger = structlog.get_logger()

# ─── Configure OpenAI Client ─────────────────────────────────────────

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# ─── System Prompt ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an internal analytics assistant for a fictional entertainment company called StreamCo.
You answer business questions using three internal tools: a SQL database, PDF document search,
and CSV analytics. You also have a chart generation tool.

Rules:
- Always cite which source(s) you used at the end of your answer using [Source: ...] notation
- Use the SQL tool for hard numbers and rankings
- Use document search for qualitative context, strategy, editorial rationale, or explanations
- Use CSV analytics for trend analysis and multi-dimensional comparisons
- Generate a chart when the data would be clearer as a visual (rankings, trends, comparisons)
- Combine multiple tools when a question requires both quantitative and qualitative answers
- Never reveal raw SQL queries, internal system IDs, or tool implementation details
- If you are uncertain, say so — do not fabricate data
- Answers must be factual and grounded in retrieved data only
- Be concise but complete. Use bullet points for lists, prose for explanations."""

# ─── OpenAI Tool (Function) Definitions ─────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_sql",
            "description": (
                "Query structured movie, viewer, and performance data from the SQL database. "
                "Use for numerical questions: revenue, views, ratings, rankings, comparisons. "
                "Select the appropriate query_name from the allowed list and pass validated params."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query_name": {
                        "type": "string",
                        "enum": list(QUERY_TEMPLATES.keys()),
                        "description": "Named query template to execute",
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameter values for the selected template (e.g. year, limit, title, genre, month)",
                    },
                },
                "required": ["query_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Retrieve relevant passages from internal PDF reports and documents. "
                "Use for qualitative questions about strategy, campaigns, editorial decisions, "
                "audience insights, or when structured data alone is insufficient."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query",
                    },
                    "doc_type": {
                        "type": "string",
                        "enum": ["quarterly_report", "campaign", "roadmap", "policy", "audience"],
                        "description": "Optional: filter to a specific document type",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_csv",
            "description": (
                "Run aggregation queries over CSV business data. "
                "Use for trend analysis, multi-dimensional grouping, and comparisons across genres, "
                "cities, or time periods."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "enum": METRICS},
                    "group_by": {"type": "string", "enum": DIMENSIONS},
                    "filters": {
                        "type": "object",
                        "description": "Optional filters: year (int), genre (str), city (str), month (str)",
                    },
                },
                "required": ["metric", "group_by"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_chart",
            "description": (
                "Generate a chart specification from data. "
                "Use when the user would benefit from a visual summary of retrieved data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {"type": "string", "enum": ["bar", "line", "scatter", "pie"]},
                    "data": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                    "x_key": {"type": "string"},
                    "y_key": {"type": "string"},
                    "title": {"type": "string"},
                },
                "required": ["chart_type", "data", "x_key", "y_key", "title"],
            },
        },
    },
]


# ─── Tool Dispatcher ─────────────────────────────────────────────────

async def _dispatch_tool(name: str, arguments: dict) -> dict:
    """Route a tool call to its implementation and return the result."""
    start = time.monotonic()
    try:
        if name == "query_sql":
            result = await query_sql(arguments.get("query_name", ""), arguments.get("params", {}))
        elif name == "search_documents":
            result = await search_documents(arguments.get("query", ""), arguments.get("doc_type"))
        elif name == "analyze_csv":
            result = await analyze_csv(
                arguments.get("metric", ""),
                arguments.get("group_by", ""),
                arguments.get("filters", {}),
            )
        elif name == "generate_chart":
            result = await generate_chart(
                arguments["chart_type"],
                arguments["data"],
                arguments["x_key"],
                arguments["y_key"],
                arguments["title"],
            )
        else:
            result = {"error": f"Unknown tool: {name}"}
    except Exception as e:
        logger.error("tool_dispatch_error", tool=name, error=str(e))
        result = {"error": str(e)}

    duration_ms = round((time.monotonic() - start) * 1000)
    logger.info("tool_call", tool_name=name, duration_ms=duration_ms,
                row_count=result.get("row_count", len(result.get("data", result.get("chunks", [])))))
    return result


# ─── Response Model ──────────────────────────────────────────────────

class OrchestratorResponse(BaseModel):
    answer: str
    tool_trace: list[dict]
    chart_spec: dict | None = None
    sources: list[str]


# ─── Agentic Loop ────────────────────────────────────────────────────

MAX_TOOL_ROUNDS = 10


async def run_conversation(
    messages: list[dict],
    filters: dict | None = None,
    user_role: str = "analyst",
) -> OrchestratorResponse:
    """
    Run the OpenAI agentic function-calling loop.
    Continues dispatching tool calls until GPT produces a final text answer.
    """
    tool_trace = []
    chart_spec = None
    sources_used = set()

    # Build message list with system prompt
    system_message = {"role": "system", "content": SYSTEM_PROMPT}
    if filters:
        system_message["content"] += f"\n\nActive user filters: {json.dumps(filters)}"

    chat_messages = [system_message] + list(messages)

    # Agentic loop
    for _round in range(MAX_TOOL_ROUNDS):
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=chat_messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        chat_messages.append(message.model_dump(exclude_none=True))

        # No tool calls — final answer
        if not message.tool_calls:
            answer = message.content or "I was unable to generate a response."
            break

        # Dispatch all tool calls in parallel
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            result = await _dispatch_tool(fn_name, fn_args)
            sources_used.add(result.get("source", fn_name))

            # Capture chart spec
            if fn_name == "generate_chart" and "error" not in result:
                chart_spec = result

            tool_trace.append({
                "tool": fn_name,
                "input": fn_args,
                "row_count": result.get("row_count", len(result.get("data", result.get("chunks", [])))),
                "source": result.get("source"),
            })

            # Append tool result to message history
            chat_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, default=str),
            })
    else:
        answer = "I reached the maximum number of tool calls. Please try a simpler question."

    return OrchestratorResponse(
        answer=answer,
        tool_trace=tool_trace,
        chart_spec=chart_spec,
        sources=list(sources_used),
    )


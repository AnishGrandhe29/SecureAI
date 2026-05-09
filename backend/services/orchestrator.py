"""
AI Orchestrator — Google Gemini function-calling agentic loop.
This is the most important file in the codebase.
Runs a multi-turn loop dispatching tool calls until Gemini produces a final answer.
"""

import json
import time
import structlog
import google.generativeai as genai
from pydantic import BaseModel
from config import settings
from services.sql_tool import query_sql, QUERY_TEMPLATES
from services.rag_tool import search_documents
from services.csv_tool import analyze_csv, METRICS, DIMENSIONS
from services.chart_tool import generate_chart, ChartSpec

logger = structlog.get_logger()

# ─── Configure Gemini Client ─────────────────────────────────────────

genai.configure(api_key=settings.GEMINI_API_KEY)

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

# ─── Gemini Function (Tool) Definitions ─────────────────────────────

TOOLS = [
    genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name="query_sql",
                description=(
                    "Query structured movie, viewer, and performance data from the SQL database. "
                    "Use for numerical questions: revenue, views, ratings, rankings, comparisons. "
                    "Select the appropriate query_name from the allowed list and pass validated params."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query_name": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=list(QUERY_TEMPLATES.keys()),
                            description="Named query template to execute",
                        ),
                        "params": genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            description="Parameter values for the selected template (e.g. year, limit, title, genre, month)",
                        ),
                    },
                    required=["query_name"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="search_documents",
                description=(
                    "Retrieve relevant passages from internal PDF reports and documents. "
                    "Use for qualitative questions about strategy, campaigns, editorial decisions, "
                    "audience insights, or when structured data alone is insufficient."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "query": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Natural language search query",
                        ),
                        "doc_type": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=["quarterly_report", "campaign", "roadmap", "policy", "audience"],
                            description="Optional: filter to a specific document type",
                        ),
                    },
                    required=["query"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="analyze_csv",
                description=(
                    "Run aggregation queries over CSV business data. "
                    "Use for trend analysis, multi-dimensional grouping, and comparisons across genres, "
                    "cities, or time periods."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "metric": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=METRICS,
                        ),
                        "group_by": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=DIMENSIONS,
                        ),
                        "filters": genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            description="Optional filters: year (int), genre (str), city (str), month (str)",
                        ),
                    },
                    required=["metric", "group_by"],
                ),
            ),
            genai.protos.FunctionDeclaration(
                name="generate_chart",
                description=(
                    "Generate a chart specification from data. "
                    "Use when the user would benefit from a visual summary of retrieved data."
                ),
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "chart_type": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            enum=["bar", "line", "scatter", "pie"],
                        ),
                        "data": genai.protos.Schema(
                            type=genai.protos.Type.ARRAY,
                            items=genai.protos.Schema(type=genai.protos.Type.OBJECT),
                        ),
                        "x_key": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "y_key": genai.protos.Schema(type=genai.protos.Type.STRING),
                        "title": genai.protos.Schema(type=genai.protos.Type.STRING),
                    },
                    required=["chart_type", "data", "x_key", "y_key", "title"],
                ),
            ),
        ]
    )
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


def _convert_history_to_gemini(messages: list[dict]) -> list[dict]:
    """Convert OpenAI-style message list to Gemini-style history list."""
    history = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "assistant":
            role = "model"
        if role in ("user", "model") and content:
            history.append({"role": role, "parts": [content]})
    return history


async def run_conversation(
    messages: list[dict],
    filters: dict | None = None,
    user_role: str = "analyst",
) -> OrchestratorResponse:
    """
    Run the Gemini agentic function-calling loop.
    Continues dispatching tool calls until Gemini produces a final text answer.
    """
    tool_trace = []
    chart_spec = None
    sources_used = set()

    # Build system instruction with optional active filters
    system_instruction = SYSTEM_PROMPT
    if filters:
        system_instruction += f"\n\nActive user filters: {json.dumps(filters)}"

    # Initialise the model
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        tools=TOOLS,
        system_instruction=system_instruction,
    )

    # Separate the last user message from history
    history = _convert_history_to_gemini(messages[:-1])
    last_user_message = messages[-1]["content"] if messages else ""

    # Start chat session with existing history
    chat = model.start_chat(history=history)

    # Agentic loop
    for _round in range(MAX_TOOL_ROUNDS):
        response = await chat.send_message_async(last_user_message if _round == 0 else tool_results_part)

        # Collect all parts from the response
        has_function_call = False
        tool_results_part = []

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.function_call.name:
                    has_function_call = True
                    fn_name = part.function_call.name
                    fn_args = dict(part.function_call.args)

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

                    # Build the function response part for the next turn
                    tool_results_part.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_name,
                                response={"result": json.dumps(result, default=str)},
                            )
                        )
                    )

        if not has_function_call:
            # Final text answer
            answer = response.text or "I was unable to generate a response."
            break
    else:
        answer = "I reached the maximum number of tool calls. Please try a simpler question."

    return OrchestratorResponse(
        answer=answer,
        tool_trace=tool_trace,
        chart_spec=chart_spec,
        sources=list(sources_used),
    )

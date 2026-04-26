from dataclasses import dataclass
from typing import Any, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from sqlalchemy import select

from models import Embedding
from schemas.chat import RetrievedChunk
from services.embeding_service import create_embedding
from utils.logger import get_logger
from worker import load_model

logger = get_logger()
model = load_model()


@dataclass
class ChatState:
    query: str
    top_k: int
    answer: str
    context: Optional[str]
    file_id: str
    retrieved_chunks: list[RetrievedChunk]


@dataclass
class ChatContext:
    db: Any
    llm: Any
    model: Any


SYSTEM_PROMPT = ChatPromptTemplate.from_template(
    """You are the official AI Assistant for the AI study budy
## YOUR ROLE
Answer questions *you are free to be as much as creative as you want* but always use the following rules:
- For coding questions, provide code snippets
- for science questions, provide detailed explanations and examples
- for general questions, provide concise and accurate answers


## CONTEXT (from the report):
{context}

## USER QUESTION:
{query}

## ANSWER:"""
)


def no_context(state: ChatState) -> ChatState:
    """function to handle when no context is found"""
    if state.context is None:
        state.answer = "No context found for the query"
    return state


async def vector_search(query: str, db, model, file_id: str, top_k: int = 10):
    query_embedding = create_embedding(model, [query])[0]

    distance = Embedding.embedding.cosine_distance(query_embedding)

    stmt = (
        select(Embedding)
        .where(Embedding.file_id == file_id, distance < 0.5)
        .order_by(distance)
        .limit(top_k)
    )

    results = await db.execute(stmt)
    return results.scalars().all()


async def node_with_context(
    state: ChatState, runtime: Runtime[ChatContext]
) -> ChatState:
    db = runtime.context.db
    model = runtime.context.model
    if not db or not model:
        raise ValueError("Database session or model not found in runtime context")

    top_k = state.top_k
    if top_k is None:
        raise ValueError

    rows = await vector_search(state.query, db, model, state.file_id, top_k)

    if not rows:
        state.context = None
        state.retrieved_chunks = []
        return state

    state.retrieved_chunks = [
        RetrievedChunk(text=row.chunks, source=row.file_id) for row in rows
    ]
    state.context = state.retrieved_chunks[0].text if state.retrieved_chunks else None
    return state


async def node_llm(state: ChatState, runtime: Runtime[ChatContext]) -> ChatState:
    """function to handle when llm is called"""

    llm = runtime.context.llm
    if not llm:
        raise ValueError("LLM chat model is required")

    prompt = ChatPromptTemplate.from_messages(["system", SYSTEM_PROMPT])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    result = await chain.ainvoke({"context": state.context, "query": state.query})
    state.answer = result
    return state


def route(state: ChatState):
    if state.context is None:
        return "no_context"
    return "llm"


graph = StateGraph(state_schema=ChatState, context_schema=ChatContext)
graph.add_node("no_context", no_context)
graph.add_node("with_context", node_with_context)
graph.add_node("llm", node_llm)

graph.add_edge(START, "with_context")
graph.add_conditional_edges("with_context", route)

graph.add_edge("no_context", END)
graph.add_edge("llm", END)

chatbot = graph.compile()

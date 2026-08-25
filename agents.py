"""Agent and LCEL chain setup for the research assistant."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from tools import scrape_url, web_search

load_dotenv()


def get_llm():
    """Return the configured chat model (Groq or OpenAI) using API credentials from .env."""
    if os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        return ChatGroq(model=model_name, temperature=0, api_key=os.getenv("GROQ_API_KEY"))

    api_key = os.getenv("OPENAI_API_KEY") or "sk-placeholder"
    return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)


llm = get_llm()


def build_search_agent():
    """Create the search agent with live web search capability."""
    return create_agent(model=llm, tools=[web_search])


def build_reader_agent():
    """Create the reader agent that can scrape relevant URLs."""
    return create_agent(model=llm, tools=[scrape_url])


writer_parser = JsonOutputParser()
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured, insightful, and professional reports based only on the provided evidence. Return a valid JSON object with keys: introduction, key_findings, conclusion, and sources.",
        ),
        (
            "human",
            "Research Topic: {topic}\n\nResearch Notes:\n{research}\n\n{format_instructions}",
        ),
    ]
).partial(format_instructions=writer_parser.get_format_instructions())
writer_chain = writer_prompt | llm | writer_parser

critic_parser = JsonOutputParser()
critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp, constructive research critic. Be honest, specific, and balanced. Focus on factual quality, clarity, and completeness. Return a valid JSON object with keys: score, strengths, areas_for_improvement, and verdict.",
        ),
        (
            "human",
            "Critique the following research report. Provide a score out of 10, strengths, areas for improvement, and a concise verdict.\n\nReport:\n{report}\n\n{format_instructions}",
        ),
    ]
).partial(format_instructions=critic_parser.get_format_instructions())
critic_chain = critic_prompt | llm | critic_parser

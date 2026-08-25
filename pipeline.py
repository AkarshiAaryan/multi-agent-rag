"""Pipeline orchestration for the multi-agent research assistant."""

from __future__ import annotations

import os

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain


def run_research_pipeline(topic: str) -> dict:
    """Run the complete multi-agent research flow for a given topic."""
    if not (os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise RuntimeError("Neither GROQ_API_KEY nor OPENAI_API_KEY was found. Add an API key to the project .env file.")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY is missing. Add it to the project .env file before running the pipeline.")

    state: dict[str, str | dict] = {}

    print("Step 1: Search agent is gathering recent, relevant sources...")
    search_agent = build_search_agent()
    search_response = search_agent.invoke(
        {"messages": [("user", f"Find recent, reliable, and detailed information about: {topic}")]}
    )
    state["search_results"] = (
        search_response["messages"][-1].content if search_response.get("messages") else str(search_response)
    )
    print("Step 1 complete. Search results captured.")
    print(state["search_results"][:1000])

    print("Step 2: Reader agent is selecting the most relevant URLs and scraping them...")
    reader_agent = build_reader_agent()
    source_context = state["search_results"][-800:] if isinstance(state["search_results"], str) else ""
    reader_prompt = (
        f"Research Topic: {topic}\n\nUse the source list below to identify the best URLs and scrape them "
        f"for deeper evidence. Return only the most useful, relevant factual content.\n\n{source_context}"
    )
    reader_response = reader_agent.invoke({"messages": [("user", reader_prompt)]})
    state["scraped_content"] = (
        reader_response["messages"][-1].content if reader_response.get("messages") else str(reader_response)
    )
    print("Step 2 complete. Scraped content captured.")
    print(state["scraped_content"][:1000])

    print("Step 3: Writer agent is composing the final research report...")
    research_combined = (
        f"SEARCH RESULTS\n\n{state['search_results']}\n\n\nSCRAPED CONTENT\n\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    print("Step 3 complete. Report generated.")
    print(state["report"])

    print("Step 4: Critic is evaluating the report...")
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    print("Step 4 complete. Feedback generated.")
    print(state["feedback"])

    return state


if __name__ == "__main__":
    user_topic = input("Enter a research topic: ").strip()
    if not user_topic:
        print("No topic entered. Please provide a research topic.")
    else:
        result = run_research_pipeline(user_topic)
        print("\nFinal Report:\n")
        print(result["report"])
        print("\nCritic Feedback:\n")
        print(result["feedback"])

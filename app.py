"""Streamlit interface for the multi-agent research assistant."""

from __future__ import annotations

import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(page_title="Multi-Agent Research Assistant", layout="wide")


def format_report_markdown(report: object) -> str:
    """Convert a structured report into markdown for UI display and download."""
    if isinstance(report, str):
        return report

    if not isinstance(report, dict):
        return str(report)

    introduction = report.get("introduction") or report.get("Introduction") or ""
    findings = report.get("key_findings") or report.get("Key Findings") or []
    conclusion = report.get("conclusion") or report.get("Conclusion") or ""
    sources = report.get("sources") or report.get("Sources") or []

    if isinstance(findings, str):
        findings_list = [findings]
    elif isinstance(findings, list):
        findings_list = findings
    else:
        findings_list = [str(findings)]

    if isinstance(sources, str):
        sources_list = [sources]
    elif isinstance(sources, list):
        sources_list = sources
    else:
        sources_list = [str(sources)]

    findings_md = "\n".join(f"- {item}" for item in findings_list)
    sources_md = "\n".join(f"- {item}" for item in sources_list)

    return (
        "## Introduction\n\n"
        f"{introduction}\n\n"
        "## Key Findings\n\n"
        f"{findings_md}\n\n"
        "## Conclusion\n\n"
        f"{conclusion}\n\n"
        "## Sources\n\n"
        f"{sources_md}"
    )


st.title("Multi-Agent Research Assistant")
st.caption("Search, scrape, write, and critique a research report with a small team of specialized agents.")

with st.form("research_form"):
    topic = st.text_input("Research topic", placeholder="e.g. The impact of AI on software development")
    submitted = st.form_submit_button("Run Research")

if submitted and topic.strip():
    try:
        with st.spinner("Searching the web..."):
            state = run_research_pipeline(topic.strip())

        with st.expander("Raw Search Results", expanded=False):
            st.text(state.get("search_results", "No search results found."))

        with st.expander("Scraped Content", expanded=False):
            st.text(state.get("scraped_content", "No scraped content found."))

        report = state.get("report", {})
        feedback = state.get("feedback", {})

        st.subheader("Research Report")
        st.markdown(format_report_markdown(report))

        st.subheader("Critic Feedback")
        st.write(f"**Score:** {feedback.get('score', 'N/A')}/10")

        strengths = feedback.get("strengths") or []
        if isinstance(strengths, str):
            strengths = [strengths]
        st.write("**Strengths:**")
        for item in strengths:
            st.write(f"- {item}")

        improvements = feedback.get("areas_for_improvement") or []
        if isinstance(improvements, str):
            improvements = [improvements]
        st.write("**Areas for Improvement:**")
        for item in improvements:
            st.write(f"- {item}")

        verdict = feedback.get("verdict") or "No verdict available."
        st.write(f"**Verdict:** {verdict}")

        report_markdown = format_report_markdown(report)
        st.download_button(
            label="Download report as .md",
            data=report_markdown,
            file_name="research_report.md",
            mime="text/markdown",
        )
    except Exception as exc:
        st.error(f"The research pipeline could not run. {exc}")
else:
    st.info("Enter a topic and click 'Run Research' to begin.")

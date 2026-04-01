import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import dotenv
dotenv.load_dotenv()

from config.settings import settings  
from core import build_research_graph, PipelineState

st.set_page_config(page_title="Veritas7 AI", layout="wide", page_icon="🕵️")
st.title("🕵️ Veritas7 AI")
st.markdown("A robust 7-stage automated research pipeline powered by LangGraph.")

with st.sidebar:
    st.header("Configuration")
    st.markdown("Provide the API Keys below:")
    groq_key = st.text_input("Groq API Key (Llama 3)", type="password", value=os.environ.get("GROQ_API_KEY", ""))
    
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    else:
        st.warning("Please provide an API key to get real LLM responses.")

query = st.text_input("Enter your complex research question:", placeholder="E.g., What are the latest advancements in AI agent architectures?")

if st.button("Run Research Pipeline", type="primary"):
    if not query.strip():
        st.warning("Please enter a valid query to proceed.")
    elif not groq_key:
        st.error("Stop! You must provide either a Groq API key in the sidebar before running the pipeline.")
    else:
        with st.spinner("Running LangGraph Pipeline... This might take a minute."):
            try:
                app_graph = build_research_graph()
                initial_state = {"user_query": query} 
                final_state = app_graph.invoke(initial_state) 
                errors = final_state.get("errors", [])
                iteration_count = final_state.get("iteration_count", 0)
                
                if errors:
                    st.error("Pipeline finished with errors. See trace below.")
                else:
                    st.success(f"Pipeline finished successfully in {iteration_count} iterations!")
                
                st.subheader("Final Synthesized Answer")
                st.info(final_state.get("final_answer", "No final answer generated."))
                
                confidence = final_state.get("confidence_score", 0.0)
                st.metric("Information Confidence", f"{confidence * 100:.0f}%")

                with st.expander("🛠️ View Internal Pipeline Trace & Working Data"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 1. Planner (Sub-Questions)")
                        for q in final_state.get("sub_questions", []) or ["No sub-questions generated."]:
                            st.markdown(f"- {q}")

                        st.markdown("### 2. Query Rewriter (Search Keywords)")
                        for q in final_state.get("rewritten_queries", []) or ["No queries rewritten."]:
                            st.markdown(f"- {q}")

                    with col2:
                        st.markdown("### 3. Researcher (Gathered Context)")
                        docs = final_state.get("raw_documents", [])
                        st.markdown(f"**Gathered {len(docs)} unique context chunks.**")
                        if docs:
                            first_doc = docs[0]
                            if isinstance(first_doc, dict):
                                first_source = first_doc.get("source", "Unknown Source")
                            else:
                                first_source = getattr(first_doc, "source", "Unknown Source")
                            st.write(f"Top Source: {first_source}")
                    
                    st.divider()
                    
                    st.markdown("### 4. Summarizer (Context Brief)")
                    st.caption(final_state.get("context_summary", "No summary generated."))

                    st.markdown("### 5. Generator (First Draft)")
                    st.caption(final_state.get("draft_answer", "No draft generated."))

                    critic_res = final_state.get("critic_result")
                    if critic_res:
                        st.markdown("### 6. Critic (Evaluation)")
                        if isinstance(critic_res, dict):
                            verdict = critic_res.get("verdict", "Unknown")
                            score = critic_res.get("overall_score", 0)
                        else:
                            verdict = getattr(critic_res, "verdict", "Unknown")
                            score = getattr(critic_res, "overall_score", 0)
                        
                        st.json({
                            "Verdict": verdict,
                            "Score": score
                        })
                        
                    st.markdown("### 7. Refiner (Corrections)")
                    if iteration_count > 0:
                        st.success(f"Refiner successfully corrected the draft {iteration_count} time(s) based on Critic feedback!")
                    else:
                        st.info("Draft was deemed good enough initially; Refiner was bypassed.")

                if errors:
                    st.error("Errors encountered during execution:")
                    for e in errors:
                        st.write(f"  - {e}")

            except Exception as e:
                st.error(f"Critical failure running LangGraph pipeline: {e}")
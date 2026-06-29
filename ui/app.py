"""
Streamlit UI for RAG-GOV.

Sections:
1. Sidebar  — Download PDFs from a URL + user profile inputs.
2. Main area — Ask a question, view eligibility results + evidence.
"""

import sys
from pathlib import Path

import requests
import streamlit as st

# ------------------------------------------------------------------
# Ensure the project root is on sys.path so our local imports work
# when Streamlit is launched from inside the ui/ folder.
# ------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config                          # noqa: E402
from ingestion.downloader import (                  # noqa: E402
    find_pdf_links,
    download_pdf,
    download_pdfs_from_url,
)

API_URL = "http://localhost:8000/query"


# ===================================================================
# Page config
# ===================================================================
st.set_page_config(page_title="RAG-GOV", page_icon="🏛️", layout="wide")
st.title("🏛️ RAG-GOV: Policy-Aware Scheme Eligibility")

# ===================================================================
# SIDEBAR — Section 1: PDF downloader
# ===================================================================
st.sidebar.header("📥 Download Scheme PDFs")
st.sidebar.caption(
    "Paste the URL of a government page that lists scheme PDFs. "
    "The system will find and download all linked PDFs automatically."
)

site_url = st.sidebar.text_input(
    "Website URL",
    placeholder="https://scholarships.gov.in/public/schemeGuidelines",
)

if st.sidebar.button("🔍 Scan & Download PDFs"):
    if not site_url.strip():
        st.sidebar.warning("Please enter a URL first.")
    else:
        with st.sidebar.status("Scanning page for PDFs...", expanded=True) as status:
            try:
                pdf_links = find_pdf_links(site_url.strip())
                if not pdf_links:
                    status.update(label="No PDF links found on that page.", state="error")
                else:
                    st.sidebar.write(f"Found **{len(pdf_links)}** PDF link(s). Downloading...")
                    downloaded = []
                    progress = st.sidebar.progress(0)
                    for i, link in enumerate(pdf_links):
                        path = download_pdf(link)
                        if path:
                            downloaded.append(path)
                        progress.progress((i + 1) / len(pdf_links))

                    status.update(
                        label=f"✅ Downloaded {len(downloaded)}/{len(pdf_links)} PDFs",
                        state="complete",
                    )
                    for p in downloaded:
                        st.sidebar.write(f"  • `{p.name}`")
            except Exception as exc:
                status.update(label=f"Error: {exc}", state="error")

# Show what's already in data/raw
raw_dir = config.paths.data_raw
raw_dir.mkdir(parents=True, exist_ok=True)
existing_pdfs = sorted(raw_dir.glob("*.pdf"))
if existing_pdfs:
    with st.sidebar.expander(f"📂 PDFs in data/raw/ ({len(existing_pdfs)})"):
        for p in existing_pdfs:
            size_kb = p.stat().st_size / 1024
            st.write(f"• **{p.name}** ({size_kb:.0f} KB)")
else:
    st.sidebar.info("No PDFs in data/raw/ yet. Download or drop files there.")

st.sidebar.divider()

# ===================================================================
# SIDEBAR — Section 2: User profile
# ===================================================================
st.sidebar.header("👤 Your Profile")
age = st.sidebar.number_input("Age", min_value=0, max_value=120, value=21)
income = st.sidebar.number_input(
    "Annual income (₹)", min_value=0.0, step=1000.0, value=150000.0
)
category = st.sidebar.selectbox(
    "Category", ["", "SC", "ST", "OBC", "General", "EWS", "Minority"]
)
state = st.sidebar.text_input("State", value="")
student = st.sidebar.checkbox("Student", value=True)

st.sidebar.divider()

# ===================================================================
# MAIN — Ask a question
# ===================================================================
question = st.text_input(
    "💬 Your question",
    value="Which schemes am I eligible for?",
)

col1, col2 = st.columns([1, 4])
with col1:
    check = st.button("Check eligibility", type="primary")

if check:
    payload = {
        "profile": {
            "age": age,
            "income": income,
            "category": category or None,
            "state": state or None,
            "student": student,
        },
        "question": question,
        "top_k": 5,
    }

    with st.spinner("Evaluating eligibility & searching documents..."):
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.ConnectionError:
            st.error(
                "Could not connect to the API server. "
                "Make sure it is running:  `uvicorn api.server:app --reload`"
            )
            st.stop()
        except Exception as exc:
            st.error(f"API error: {exc}")
            st.stop()

    results = data.get("results", [])
    if not results:
        st.info("No schemes evaluated. Make sure the API has loaded eligibility rules.")
    else:
        for r in results:
            label = r["label"]
            icon = {"ELIGIBLE": "✅", "NOT_ELIGIBLE": "❌", "INSUFFICIENT_INFO": "⚠️"}.get(
                label, "ℹ️"
            )
            st.subheader(f"{icon} Scheme: {r['scheme_id']}  —  {label}")

            if r["missing_fields"]:
                st.warning(f"Missing profile fields: {', '.join(r['missing_fields'])}")

            st.markdown(f"**Rule trace:** {r['explanation']}")

            evidence_list = r.get("evidence", [])
            if evidence_list:
                with st.expander(f"📄 Supporting evidence ({len(evidence_list)} chunks)"):
                    for ev in evidence_list:
                        st.markdown(
                            f"> {ev['text']}\n\n"
                            f"**Score:** {ev['score']:.3f}  "
                            f"| **Source:** {ev.get('metadata', {}).get('filename', 'unknown')}"
                        )
            else:
                st.caption("No document evidence retrieved for this query.")


# ===================================================================
# Footer
# ===================================================================
st.divider()
st.caption(
    "RAG-GOV: Policy-Aware Graph-Enhanced RAG System  •  "
    "PDFs are saved in `data/raw/`  •  "
    "Run `python ingestion/run_ingest.py` after downloading new PDFs to index them."
)

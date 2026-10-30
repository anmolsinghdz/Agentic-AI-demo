from dotenv import load_dotenv
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(page_title="Blood Work Analyzer", layout="wide")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

st.title("Blood Work Analyzer")

# Initialize session state for persistence across reruns
if "health_summary" not in st.session_state:
    st.session_state.health_summary = ""
if "diet_plan" not in st.session_state:
    st.session_state.diet_plan = ""

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Blood Work Report")
    blood_report = st.text_area(
        label="Paste your report below",
        height=500,
        placeholder="Paste your blood work report here...",
        label_visibility="collapsed"
    )
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

with right_col:
    st.subheader("Health Summary")
    health_container = st.container(height=230)
    if st.session_state.health_summary:
        health_container.markdown(st.session_state.health_summary)

    st.subheader("Suggested Diet Plan")
    diet_container = st.container(height=250)
    if st.session_state.diet_plan:
        diet_container.markdown(st.session_state.diet_plan)

if analyze_clicked:
    if not blood_report.strip():
        st.warning("Please paste a blood work report before analyzing.")
    else:
        with st.spinner("Analyzing your blood work..."):
            # Stage 1: Extract values
            extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL
based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{blood_report}
"""
            extraction_response = llm.invoke(extraction_prompt)
            extracted_values = str(extraction_response.content)

            # Stage 2: Health summary and Indian diet plan
            diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, provide two clearly separated sections using the exact delimiter [SPLIT_HERE]:

SECTION 1:
Write 4-5 lines explaining the patient's condition in simple, non-technical language.

[SPLIT_HERE]

SECTION 2:
List foods to eat more of and foods to avoid, using commonly available Indian foods
like dal, sabzi, roti, rice, etc. Keep it practical and concise.

Blood Work Analysis:
{extracted_values}
"""
            diet_response = llm.invoke(diet_prompt)
            full_response = str(diet_response.content)

            # Split reliably using the explicit token
            if "[SPLIT_HERE]" in full_response:
                summary, diet = full_response.split("[SPLIT_HERE]", 1)
                st.session_state.health_summary = summary.replace("SECTION 1:", "").strip()
                st.session_state.diet_plan = diet.replace("SECTION 2:", "").strip()
            else:
                st.session_state.health_summary = full_response
                st.session_state.diet_plan = "Could not cleanly separate diet plan."

            st.rerun()
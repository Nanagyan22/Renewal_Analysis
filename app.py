# ===============================================================
# optisecure_dashboard.py — OptiSecure Insurance Renewal Assistant
# ===============================================================
import streamlit as st
import os
import pandas as pd
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------
# AI LOGIC FUNCTIONS (Merged to prevent Import Errors)
# ---------------------------------------------------------------
def get_client():
    """Get or create Gemini client"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in .env or Streamlit secrets.")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def chat_with_knowledge_base(user_question: str, knowledge_base: str, chat_history: list = None) -> str:
    """Chat with AI using the OptiSecure knowledge base"""
    system_prompt = f"""You are an expert AI Data Analyst for OptiSecure Insurance. 
You specialize in analyzing policy renewals, marketing campaign performance, and customer propensity using the 'Marketing_Campaign_Data' dataset.

YOUR ROLE:
- Answer questions using ONLY the knowledge base provided below.
- Provide clear, specific, and data-driven responses.
- Use exact numbers (e.g., "14.91% renewal rate", "Campaign 2").
- If a question is outside the scope, politely explain you can only answer based on OptiSecure’s data.

RESPONSE GUIDELINES:
1. Start with a direct, factual answer.
2. Support with precise numbers and statistics.
3. Use bullet points (-) for lists.
4. Keep your tone professional and strategic.
5. Format currency values with £ (e.g., £1,946).

KNOWLEDGE BASE:
{knowledge_base}
"""
    try:
        model = get_client()
        if chat_history is None: chat_history = []
        chat = model.start_chat(history=[])
        chat.send_message(system_prompt)
        response = chat.send_message(user_question)
        return response.text or "I apologize, but I couldn’t generate a response."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_comprehensive_report(knowledge_base: str) -> str:
    """Generate a comprehensive OptiSecure Strategic Renewal Report"""
    prompt = f"""
You are the Lead Business Intelligence Specialist for OptiSecure Insurance.
Generate a professional, strategic report strictly about OptiSecure’s Campaign Targeting & Policy Renewal Analysis.

Title: OPTISECURE INSURANCE – CAMPAIGN TARGETING & RENEWAL ANALYSIS REPORT

KNOWLEDGE BASE:
{knowledge_base}

Structure:
1. Executive Summary (Renewal Rate vs High Propensity opportunity)
2. Data & Customer Profile (Demographics, Income)
3. Segmentation Analysis (High/Mid/Low Propensity Buckets)
4. Campaign Performance Review (Campaign 2 Failure vs Campaign 4 Success)
5. Strategic Recommendations
"""
    try:
        model = get_client()
        response = model.generate_content(prompt)
        return response.text or "Unable to generate report."
    except Exception as e:
        return f"Error generating report: {str(e)}"

# ---------------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------------
st.set_page_config(
    page_title="OptiSecure Analytics Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------
# Knowledge Base Loader
# ---------------------------------------------------------------
@st.cache_data
def load_knowledge_base():
    """Load knowledge base from docx and Consolidated Excel Data"""
    try:
        # 1. Load Text Doc
        kb_path = "attached_assets/OptiSecure_Knowledge_Base.docx"
        if os.path.exists(kb_path):
            doc = Document(kb_path)
            knowledge_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            knowledge_text = "OptiSecure General Knowledge Base."
        
        # 2. Load Excel Data
        data_path = "attached_assets/Marketing_Campaign_Data.xlsx"
        if os.path.exists(data_path):
            df = pd.read_excel(data_path, sheet_name='Consolidated_data')
        else:
            # Fallback to CSV if Excel not found
            df = pd.read_csv("attached_assets/Consolidated_data.csv")

        # 3. Calculate Metrics
        total_customers = len(df)
        renewal_rate = df['Response'].mean() * 100
        avg_income = df['Income'].mean()
        avg_spend = df['Total Spent'].mean()
        
        # Campaign Stats
        camp_cols = ['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']
        # Handle missing columns gracefully
        available_camps = [c for c in camp_cols if c in df.columns]
        avg_campaign_acceptance = df[available_camps].mean().mean() * 100 if available_camps else 0
        
        # Segmentation
        high_propensity_count = df[df['Renewal_Bucket_2'] == 'High'].shape[0] if 'Renewal_Bucket_2' in df.columns else 0
        
        # Formatting the summary exactly like the Veritas example
        excel_summary = f"""

ADDITIONAL DATASET SUMMARY – OPTISECURE INSURANCE PORTFOLIO:

CUSTOMER OVERVIEW:
- Total Policyholders: {total_customers}
- Average Renewal Rate: {renewal_rate:.2f}%
- Average Household Income: £{avg_income:,.0f}

ACCOUNT INFORMATION:
- Average Customer Value (Total Spent): £{avg_spend:,.2f}
- High Propensity Segment Size: {high_propensity_count} customers
- Campaign Acceptance Rate: {avg_campaign_acceptance:.2f}%

CRITICAL INSIGHTS:
- Campaign 2 is underperforming (approx 1.3% acceptance).
- High Propensity customers renew at ~30.7%.
- Low Propensity customers renew at ~6.1%.
"""
        return knowledge_text + excel_summary
    except Exception as e:
        st.error(f"Error loading knowledge base: {e}")
        return ""

# ---------------------------------------------------------------
# UI Header
# ---------------------------------------------------------------
def display_header():
    """Display header with OptiSecure branding"""
    st.markdown("""
        <h1 style='text-align: center; color: #D1A658; font-size: 48px;'>🛡️ OptiSecure Insurance</h1>
        <p style='text-align: center; font-size: 24px; color: #2C3E50;'>Policy Renewal Analysis Dashboard & AI Assistant</p>
        <hr style='margin-bottom: 20px; border-top: 2px solid #18BC9C;'>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------
# Main App Logic
# ---------------------------------------------------------------
def main():
    display_header()
    
    knowledge_base = load_knowledge_base()
    
    main_col, chat_col = st.columns([2, 1])
    
    # ----------------- MAIN COLUMN -----------------
    with main_col:
        st.markdown("### 📊 Interactive Looker Studio Dashboard")

        # Embed Looker Studio (Using User's specific link)
        st.markdown(
            """
            <div style="border: 1px solid #ccc; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <iframe width="100%" height="700" 
                src="https://lookerstudio.google.com/embed/reporting/6414d2cf-4ab8-4678-9511-e61b5f0c715b/page/dshfF" 
                frameborder="0" style="border:0" allowfullscreen 
                sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>
            </div>
            <p style="text-align:center; font-size:12px; color:#666; margin-top: 5px;">*Live connection to Marketing_Campaign_Data.xlsx*</p>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("📄 Generate Strategic Renewal Report", type="primary"):
            with st.spinner("Generating OptiSecure strategic insights report..."):
                if not os.environ.get("GEMINI_API_KEY") and "GEMINI_API_KEY" not in st.secrets:
                    st.error("⚠️ GEMINI_API_KEY not set. Please add API key in your .env file.")
                else:
                    report = generate_comprehensive_report(knowledge_base)
                    st.markdown("### 📋 Strategic Insight Report")
                    st.markdown(report)
    
    # ----------------- CHAT COLUMN -----------------
    with chat_col:
        st.markdown("### 🤖 AI Assistant")
        st.markdown("*Ask questions about renewals, campaigns, or customer segments*")
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        chat_container = st.container(height=500)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask about renewal rate, campaign ROI, or segments..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            if not os.environ.get("GEMINI_API_KEY") and "GEMINI_API_KEY" not in st.secrets:
                response = "⚠️ Please set your GEMINI_API_KEY to use the chatbot."
            else:
                with st.spinner("Analyzing data..."):
                    response = chat_with_knowledge_base(prompt, knowledge_base, st.session_state.chat_history)
                    st.session_state.chat_history.append(f"User: {prompt}")
                    st.session_state.chat_history.append(f"Assistant: {response}")
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
        
        with st.expander("💡 Sample Questions"):
            st.markdown("""
            - What is the overall renewal rate?
            - Which campaign is underperforming?
            - How does catalog usage impact renewals?
            - What defines the High Propensity segment?
            - How does income affect renewal likelihood?
            """)

# ---------------------------------------------------------------
# Run the Streamlit App
# ---------------------------------------------------------------
if __name__ == "__main__":
    main()
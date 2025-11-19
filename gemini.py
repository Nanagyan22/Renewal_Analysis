# ===============================================================
# optisecure_ai.py — OptiSecure Insurance Analytics Assistant
# ===============================================================

import os
import google.generativeai as genai

def get_client():
    """Get or create Gemini client"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    # Configure the library directly if using google.generativeai
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')


def chat_with_knowledge_base(user_question: str, knowledge_base: str, chat_history: list = None) -> str:
    """
    Chat with AI using the OptiSecure Insurance knowledge base.
    """
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
6. Focus on "Renewals", "Campaigns", and "Propensity" rather than "Churn".

EXAMPLE INTERACTIONS:

User: "What is the overall renewal rate?"
Response: "The overall policy renewal rate is 14.91 percent across the customer base of 2,240 policyholders. However, this varies significantly by segment."

User: "Which campaign is underperforming?"
Response: "Campaign 2 is the primary underperformer with an acceptance rate of just 1.34 percent, significantly lower than the top performer, Campaign 4, which achieved 7.46 percent."

User: "Who are our best customers?"
Response: "The 'High Propensity' segment represents your best customers. They:
- Have a renewal rate of 30.7 percent
- Spend an average of £1,946
- Are frequent Catalog shoppers (4.2 purchases avg)
- Often hold PhD or Master's degrees"

KNOWLEDGE BASE:
{knowledge_base}

Remember: Use specific metrics, write professionally, and focus on OptiSecure's renewal optimization.
"""
    
    try:
        model = get_client()
        
        if chat_history is None:
            chat_history = []
        
        # Construct the chat session
        chat = model.start_chat(history=[])
        
        # Send the context/system prompt first
        chat.send_message(system_prompt)
        
        # Send history context if needed (simplified for single-turn logic here)
        # For true history, we would append previous turns. 
        # Here we just send the user question with context.
        
        response = chat.send_message(user_question)
        
        return response.text or "I apologize, but I couldn’t generate a response. Please try again."
    
    except Exception as e:
        return f"Error: {str(e)}"


def generate_comprehensive_report(knowledge_base: str) -> str:
    """
    Generate a comprehensive OptiSecure Strategic Renewal Report.
    """
    prompt = f"""
You are the Lead Business Intelligence Specialist for OptiSecure Insurance.

Your task is to generate a professional, strategic report strictly about OptiSecure’s Campaign Targeting & Policy Renewal Analysis.
Do NOT include any other companies or unrelated data.

The report MUST begin with this title:
OPTISECURE INSURANCE – CAMPAIGN TARGETING & RENEWAL ANALYSIS REPORT

KNOWLEDGE BASE (OptiSecure data):
{knowledge_base}

Use this exact structure:

# OPTISECURE INSURANCE – CAMPAIGN TARGETING & RENEWAL ANALYSIS REPORT
Date: November 2025
Prepared by:Francis Afful Gyan - Business Intelligence Strategist

## 1. Executive Summary
- Summarize the 14.9% renewal rate vs. the 30.7% High Propensity opportunity.
- Highlight the failure of Campaign 2 and the success of Catalogs.

## 2. Data & Customer Profile
- Total customers (2,240).
- Demographics: Education (PhD/Master impact), Marital Status.
- Income Analysis: Impact of High Income on renewal.

## 3. Segmentation Analysis (Propensity)
- Define the three buckets: High, Mid, Low.
- Compare Renewal Rates and Total Spend per bucket.

## 4. Campaign Performance Review
- Compare Campaign 4 (Top) vs. Campaign 2 (Fail).
- Provide exact acceptance percentages.

## 5. Channel Engagement Strategy
- Analyze the "Catalog" vs. "Web" purchase behavior for High Propensity customers.
- Discuss the impact of Recency (days since last interaction).

## 6. Strategic Recommendations
- 3-5 actionable steps (e.g., Pause Campaign 2, Target Catalogs to High segment).

## 7. Conclusion
- Summary of the revenue opportunity.

RESPONSE RULES:
- Mention "OptiSecure Insurance" in the title.
- Use £ for currency.
- Use clear markdown headings (#, ##).
- Maintain a formal, strategic tone.
"""

    try:
        # Always create a fresh client/model call
        model = get_client()

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=8192
            )
        )

        return response.text or "Unable to generate report."

    except Exception as e:
        return f"Error generating report: {str(e)}"
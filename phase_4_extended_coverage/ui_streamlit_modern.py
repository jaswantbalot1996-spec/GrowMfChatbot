"""
Phase 4 Streamlit UI - Modern Chatbot Theme (Groww Style)

Provides:
- Modern chatbot interface with message bubbles
- Groww color theme (teal/green)
- Professional layout with custom CSS
- Language selector (English / हिंदी)
- Multi-language query input
- Advanced filter UI
- Response display with translation indicators
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from enum import Enum

# Set page config
st.set_page_config(
    page_title="Groww Mutual Fund FAQ",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

PHASE4_API_URL = "http://localhost:8000"

# Custom CSS for modern chatbot theme
CUSTOM_CSS = """
<style>
    /* Main theme colors - Groww teal/green */
    :root {
        --primary: #00A651;
        --primary-light: #00D97F;
        --primary-dark: #006B3B;
        --secondary: #1F3A3D;
        --accent: #00D97F;
        --bg-light: #F5F7FA;
        --text-dark: #1F3A3D;
        --text-light: #6B7280;
        --border-light: #E5E7EB;
    }
    
    /* Main background - Enhanced gradient */
    .stApp {
        background: linear-gradient(135deg, #F5F7FA 0%, #FFFFFF 50%, #F0FEFF 100%) !important;
    }
    
    /* Remove default padding */
    .main {
        padding: 2rem 1rem;
    }
    
    /* Sidebar styling - Enhanced gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F2F32 0%, #1F3A3D 50%, #2D5558 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Container styling */
    .stContainer {
        background: transparent !important;
    }
    
    /* Header styling - Enhanced */
    h1, h2, h3 {
        color: var(--primary-dark) !important;
        font-weight: 700 !important;
    }
    
    /* Input fields - Enhanced */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid var(--border-light) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 4px rgba(0, 166, 81, 0.15) !important;
    }
    
    /* User message bubble - Enhanced */
    .user-message {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        padding: 14px 18px !important;
        border-radius: 18px 18px 4px 18px !important;
        margin: 10px 0 10px 40% !important;
        text-align: right !important;
        font-size: 15px !important;
        line-height: 1.5 !important;
        box-shadow: 0 4px 12px rgba(0, 166, 81, 0.25) !important;
        word-wrap: break-word;
    }
    
    /* Bot message bubble - Enhanced */
    .bot-message {
        background: white !important;
        color: var(--text-dark) !important;
        padding: 14px 18px !important;
        border-radius: 18px 18px 18px 4px !important;
        margin: 10px 0 10px 0 !important;
        border: 2px solid var(--border-light) !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        max-width: 90% !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        word-wrap: break-word;
    }
    
    /* Buttons - Enhanced */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(0, 166, 81, 0.35) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0, 166, 81, 0.45) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Metric cards - Enhanced */
    .stMetric {
        background: white !important;
        padding: 16px !important;
        border-radius: 12px !important;
        border-left: 4px solid var(--primary) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        box-shadow: 0 8px 16px rgba(0, 166, 81, 0.15) !important;
        transform: translateY(-2px);
    }
    
    /* Expander styling - Enhanced */
    .streamlit-expanderHeader {
        background: var(--bg-light) !important;
        border-radius: 12px !important;
        border: 2px solid var(--border-light) !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(0, 166, 81, 0.08) 0%, rgba(0, 217, 127, 0.08) 100%) !important;
        border-color: var(--primary) !important;
    }
    
    /* Info/success boxes - Enhanced */
    .stSuccess, [data-testid="stCalloutContainer"] {
        background: rgba(0, 166, 81, 0.12) !important;
        border-left: 4px solid var(--primary) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 166, 81, 0.1) !important;
    }
    
    /* Divider - Enhanced */
    hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, var(--primary), transparent) !important;
        margin: 24px 0 !important;
    }
    
    /* Cards container - Enhanced */
    .card {
        background: white !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid var(--border-light) !important;
        transition: all 0.3s ease !important;
    }
    
    .card:hover {
        box-shadow: 0 12px 32px rgba(0, 166, 81, 0.2) !important;
        border-color: var(--primary) !important;
        transform: translateY(-4px);
    }
    
    /* Top bar styling - Enhanced */
    .top-banner {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
        color: white !important;
        padding: 32px !important;
        border-radius: 16px !important;
        margin-bottom: 32px !important;
        box-shadow: 0 12px 32px rgba(0, 166, 81, 0.3) !important;
        border: 1px solid rgba(0, 217, 127, 0.3);
    }
    
    .top-banner h1 {
        color: white !important;
        margin: 0 !important;
        font-size: 28px !important;
    }
    
    .top-banner p {
        color: rgba(255, 255, 255, 0.95) !important;
        margin: 8px 0 0 0 !important;
    }
    
    /* Language selector */
    .lang-selector {
        display: flex;
        gap: 12px;
        margin: 16px 0;
    }
    
    .lang-btn {
        flex: 1;
        padding: 10px 16px;
        border-radius: 8px;
        border: 2px solid var(--border-light);
        background: white;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .lang-btn.active {
        background: var(--primary);
        color: white;
        border-color: var(--primary);
    }
    
    /* Source items - Enhanced */
    .source-item {
        background: linear-gradient(135deg, rgba(0, 166, 81, 0.08) 0%, rgba(0, 217, 127, 0.08) 100%) !important;
        padding: 14px !important;
        border-radius: 10px !important;
        border-left: 4px solid var(--primary) !important;
        margin: 10px 0 !important;
        transition: all 0.3s ease;
    }
    
    .source-item:hover {
        box-shadow: 0 4px 12px rgba(0, 166, 81, 0.15);
        transform: translateX(4px);
    }
    
    /* Chat container */
    .chat-container {
        height: 600px;
        overflow-y: auto;
        padding: 20px;
        background: white;
        border-radius: 16px;
        border: 1px solid var(--border-light);
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }
    
    /* Answer section - Enhanced */
    .answer-section {
        background: linear-gradient(135deg, rgba(0, 166, 81, 0.08) 0%, rgba(0, 217, 127, 0.08) 100%) !important;
        padding: 24px !important;
        border-radius: 14px !important;
        border-left: 5px solid var(--primary) !important;
        margin: 16px 0 !important;
        box-shadow: 0 4px 12px rgba(0, 166, 81, 0.1) !important;
    }
    
    /* Loading indicator */
    .stSpinner {
        color: var(--primary) !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"


class UIComponents:
    """Reusable Streamlit UI components."""
    
    @staticmethod
    def render_header() -> None:
        """Render professional header with enhancements."""
        st.markdown(
            """
            <div class="top-banner">
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
                    <div>
                        <h1 style="color: white; margin: 0;">💡 Mutual Fund FAQ Assistant</h1>
                        <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 16px;">
                            Get instant, factual answers about funds, expense ratios, ELSS, SIP, and more
                        </p>
                    </div>
                    <div style="font-size: 64px; opacity: 0.3;">📊</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def language_selector() -> str:
        """Language selector widget with modern styling."""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            selected = st.radio(
                "Select Language",
                ["🇬🇧 English", "🇮🇳 हिंदी"],
                horizontal=True,
                label_visibility="collapsed"
            )
        
        return "en" if "🇬🇧" in selected else "hi"
    
    @staticmethod
    def query_input(language: str) -> str:
        """Modern query input widget."""
        if language == Language.ENGLISH.value:
            placeholder = "💬 Ask about expense ratios, minimum SIP, ELSS lock-in, risk levels..."
            label = "What would you like to know?"
        else:
            placeholder = "💬 व्यय अनुपात, न्यूनतम SIP, ELSS लॉक-इन, जोखिम स्तर के बारे में पूछें..."
            label = "आप क्या जानना चाहते हैं?"
        
        query = st.text_input(
            label,
            placeholder=placeholder,
            key="query_input",
            help="Type your question and press Enter"
        )
        
        return query
    
    @staticmethod
    def filter_expander(language: str) -> Dict[str, Any]:
        """Advanced filter UI in expandable section."""
        filters = {}
        
        with st.expander(
            "🔽 Advanced Filters" if language == Language.ENGLISH.value else "🔽 उन्नत फ़िल्टर",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                risk_label = "Risk Level" if language == Language.ENGLISH.value else "जोखिम स्तर"
                risk_options = ["Any", "Low", "Moderate", "High"]
                risk_hindi = ["कोई भी", "कम", "मध्यम", "अधिक"]
                
                selected_risk = st.selectbox(
                    risk_label,
                    risk_options if language == Language.ENGLISH.value else risk_hindi,
                    key="risk_filter"
                )
                
                if selected_risk != ("Any" if language == Language.ENGLISH.value else "कोई भी"):
                    filters["max_risk_level"] = selected_risk.lower()
            
            with col2:
                cat_label = "Category" if language == Language.ENGLISH.value else "श्रेणी"
                cat_options = ["Any", "Equity", "Debt", "Hybrid"]
                cat_hindi = ["कोई भी", "इक्विटी", "ऋण", "संकर"]
                
                selected_category = st.selectbox(
                    cat_label,
                    cat_options if language == Language.ENGLISH.value else cat_hindi,
                    key="category_filter"
                )
                
                if selected_category != ("Any" if language == Language.ENGLISH.value else "कोई भी"):
                    filters["categories"] = [selected_category]
            
            col3, col4 = st.columns(2)
            
            with col3:
                exp_label = "Max Expense Ratio (%)" if language == Language.ENGLISH.value else "अधिकतम व्यय अनुपात (%)"
                max_exp = st.number_input(
                    exp_label,
                    min_value=0.0,
                    max_value=5.0,
                    value=2.0,
                    step=0.1,
                    key="expense_filter"
                )
                filters["max_expense_ratio"] = max_exp
            
            with col4:
                aum_label = "Max AUM (₹ Crore)" if language == Language.ENGLISH.value else "अधिकतम AUM (₹ करोड़)"
                max_aum = st.number_input(
                    aum_label,
                    min_value=0.0,
                    value=50000.0,
                    step=1000.0,
                    key="aum_filter"
                )
                if max_aum > 0:
                    filters["max_aum_cr"] = max_aum
        
        return filters
    
    @staticmethod
    def render_response(
        response: Dict[str, Any],
        language: str
    ) -> None:
        """Render API response with enhanced graphics and visualizations."""
        if not response:
            return
        
        # Main answer section with gradient background
        st.markdown("---")
        
        answer = response.get("answer", "No answer generated")
        if language == Language.HINDI.value:
            answer = response.get("answer_hi", answer)
        
        # Enhanced answer display with icon
        st.markdown(
            f"""
            <div class="answer-section">
                <div style="display: flex; align-items: start; gap: 12px;">
                    <div style="font-size: 28px; margin-top: 2px;">✨</div>
                    <div style="flex: 1;">
                        <h3 style="margin: 0 0 8px 0; color: #00A651;">Answer</h3>
                        <p style="margin: 0; line-height: 1.6; font-size: 15px; color: #1F3A3D;">{answer}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Sources section with enhanced styling
        if response.get("sources"):
            st.markdown("### 📚 Sources")
            sources = response.get("sources", [])
            
            cols = st.columns(len(sources[:3]) if sources else 1)
            
            for i, (col, source) in enumerate(zip(cols, sources[:3])):
                source_name = source.get('source', f'Source {i+1}')
                relevance = source.get('relevance', 0)
                
                with col:
                    st.markdown(
                        f"""
                        <div style="background: linear-gradient(135deg, rgba(0, 166, 81, 0.1) 0%, rgba(0, 217, 127, 0.1) 100%);
                                    padding: 16px; border-radius: 12px; border-left: 4px solid #00A651;
                                    text-align: center;">
                            <div style="font-size: 12px; font-weight: 600; color: #6B7280; margin-bottom: 8px;">
                                📄 {source_name}
                            </div>
                            <div style="font-size: 18px; font-weight: 700; color: #00A651;">
                                {relevance:.0%}
                            </div>
                            <div style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">Relevance</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Performance Metrics section with enhanced cards
        st.markdown("### ⚡ Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics_data = [
            {
                "col": col1,
                "icon": "⏱️",
                "label": "Response Time",
                "value": f"{int(response.get('latency_ms', 0))}ms",
                "delta": "⚡ Fast" if response.get('latency_ms', 0) < 1000 else "⏳ Slow"
            },
            {
                "col": col2,
                "icon": "🌐",
                "label": "Language",
                "value": response.get("language_detected", "en").upper(),
                "delta": "✓" if response.get("language_detected", "en").upper() == language.upper() else "Auto"
            },
            {
                "col": col3,
                "icon": "🔍",
                "label": "Filters",
                "value": "✓ On" if response.get('filters_applied', False) else "Off",
                "delta": str(len(response.get('active_filters', [])))
            },
            {
                "col": col4,
                "icon": "📊",
                "label": "Documents",
                "value": response.get('matched_chunks', 0),
                "delta": "matches" if response.get('matched_chunks', 0) > 1 else "match"
            }
        ]
        
        for metric in metrics_data:
            with metric["col"]:
                st.markdown(
                    f"""
                    <div style="background: white; padding: 16px; border-radius: 12px;
                                border-left: 4px solid #00A651; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                        <div style="font-size: 20px; margin-bottom: 4px;">{metric['icon']}</div>
                        <div style="font-size: 12px; color: #6B7280; margin-bottom: 4px;">{metric['label']}</div>
                        <div style="font-size: 18px; font-weight: 700; color: #00A651;">{metric['value']}</div>
                        <div style="font-size: 11px; color: #9CA3AF; margin-top: 4px;">{metric['delta']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Success message with graphics
        if response.get("matched_chunks"):
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, rgba(0, 166, 81, 0.1) 0%, rgba(0, 217, 127, 0.1) 100%);
                            border: 1px solid #00A651; border-radius: 12px; padding: 16px; margin: 16px 0;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="font-size: 24px;">✓</div>
                        <div>
                            <strong style="color: #00A651;">Success!</strong><br>
                            <small style="color: #6B7280;">Found {response.get('matched_chunks')} relevant documents • 
                                         Response generated in {int(response.get('latency_ms', 0))}ms</small>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


class APIClient:
    """API client for Phase 4 endpoints."""
    
    def __init__(self, base_url: str = PHASE4_API_URL):
        """Initialize API client."""
        self.base_url = base_url
    
    def query(
        self,
        query: str,
        language: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Send query to API."""
        try:
            payload = {
                "query": query,
                "language": language,
            }
            
            if filters:
                payload.update(filters)
            
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    def health(self) -> bool:
        """Check if API is available."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


def main():
    """Main Streamlit application."""
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "en"
    if "chat_container_key" not in st.session_state:
        st.session_state.chat_container_key = 0
    
    # Render enhanced header with logo
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
            <div style="font-size: 40px; font-weight: bold; background: linear-gradient(135deg, #00A651 0%, #00D97F 100%); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                💰
            </div>
            <div>
                <h1 style="margin: 0; color: #1F3A3D; font-size: 28px;">Groww Fund Assistant</h1>
                <p style="margin: 4px 0 0 0; color: #6B7280; font-size: 13px;">Ask anything about mutual funds</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Main content area - Pure chat interface
    col1, col2 = st.columns([2.5, 1], gap="large")
    
    with col1:
        # API health check with visual indicator
        api_client = APIClient()
        health_status = api_client.health()
        
        if not health_status:
            st.markdown(
                """
                <div style="background: rgba(220,38,38,0.1); border: 2px solid #DC2626; border-radius: 12px;
                            padding: 14px; text-align: center; margin-bottom: 16px;">
                    <div style="color: #DC2626; font-weight: 700; font-size: 15px;">⚠️ API Server Offline</div>
                    <small style="color: #9CA3AF;">Please start the API on port 8000</small>
                </div>
                """,
                unsafe_allow_html=True
            )
            return
        
        # ===== CHAT DISPLAY AREA =====
        st.markdown(
            """
            <div style="background: white; border-radius: 16px; border: 2px solid #E5E7EB;
                       height: 350px; overflow-y: auto; padding: 20px; 
                       box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                       display: flex; flex-direction: column;">
            """,
            unsafe_allow_html=True
        )
        
        # Display chat messages
        if st.session_state.messages:
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    # User message - right aligned, green gradient
                    st.markdown(
                        f"""
                        <div style="margin: 12px 0; display: flex; justify-content: flex-end;">
                            <div style="background: linear-gradient(135deg, #00A651 0%, #00D97F 100%);
                                       color: white; padding: 14px 18px; border-radius: 18px 18px 4px 18px;
                                       max-width: 75%; word-wrap: break-word; font-size: 15px; line-height: 1.5;
                                       box-shadow: 0 2px 8px rgba(0, 166, 81, 0.3);">
                                {message["content"]}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Bot message - left aligned, white
                    response = message["content"]
                    answer = response.get("answer", "No answer generated")
                    
                    st.markdown(
                        f"""
                        <div style="margin: 12px 0; display: flex; justify-content: flex-start;">
                            <div style="background: white; color: #1F3A3D; padding: 14px 18px; 
                                       border-radius: 18px 18px 18px 4px; border: 2px solid #E5E7EB;
                                       max-width: 75%; word-wrap: break-word; font-size: 15px; line-height: 1.6;
                                       box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                                {answer}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Show expandable response details
                    with st.expander(f"📊 Details & Sources", expanded=False, key=f"details_{i}"):
                        UIComponents.render_response(response, st.session_state.language)
        else:
            # Empty state message
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                           height: 100%; color: #9CA3AF; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 12px;">💬</div>
                    <div style="font-size: 16px; font-weight: 600; color: #6B7280;">No messages yet</div>
                    <div style="font-size: 13px; color: #9CA3AF; margin-top: 4px;">Ask a question to get started!</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===== CHAT INPUT AREA =====
        st.markdown("---")
        
        # Input section with better styling
        st.markdown(
            """
            <div style="padding: 12px 0;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="font-size: 18px;">💭</span>
                    <span style="font-weight: 600; color: #1F3A3D;">Your Question</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        query = UIComponents.query_input(st.session_state.language)
        
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            search_button = st.button("🚀 Send", use_container_width=True, key="send_btn")
        
        with col_btn2:
            clear_button = st.button("🗑️ Clear", use_container_width=True, key="clear_btn")
        
        with col_btn3:
            st.write("")  # Placeholder
        
        with col_btn4:
            st.write("")  # Placeholder
        
        if clear_button:
            st.session_state.messages = []
            st.rerun()
        
        # Advanced filters
        filters = UIComponents.filter_expander(st.session_state.language)
        
        # ===== WHAT YOU CAN ASK SECTION =====
        st.markdown("---")
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0, 166, 81, 0.08) 0%, rgba(0, 217, 127, 0.08) 100%);
                        padding: 18px; border-radius: 12px; border-left: 4px solid #00A651; margin: 16px 0;">
                <h4 style="margin: 0 0 12px 0; color: #00A651; display: flex; align-items: center; gap: 8px;">
                    <span>✅</span> You Can Ask (Facts Only)
                </h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div>🔹 Expense ratio?</div>
                    <div>🔹 Minimum SIP?</div>
                    <div>🔹 ELSS lock-in?</div>
                    <div>🔹 Exit load?</div>
                    <div>🔹 Riskometer level?</div>
                    <div>🔹 Fund benchmark?</div>
                    <div>🔹 How to download statements?</div>
                    <div>🔹 What is NAV?</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # ===== WHAT YOU CANNOT ASK SECTION =====
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.08) 0%, rgba(239, 68, 68, 0.08) 100%);
                        padding: 18px; border-radius: 12px; border-left: 4px solid #DC2626; margin: 16px 0;">
                <h4 style="margin: 0 0 12px 0; color: #DC2626; display: flex; align-items: center; gap: 8px;">
                    <span>❌</span> We Don't Provide (No Investment Advice)
                </h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div>❌ Should I buy/sell?</div>
                    <div>❌ Which fund is best?</div>
                    <div>❌ Portfolio recommendations</div>
                    <div>❌ Return predictions</div>
                    <div>❌ Market timing advice</div>
                    <div>❌ Risk tolerance assessment</div>
                    <div>❌ Tax planning strategies</div>
                    <div>❌ Personal financial advice</div>
                </div>
                <p style="margin: 12px 0 0 0; font-size: 12px; color: #9CA3AF;">
                    💡 <strong>Disclaimer:</strong> We provide facts only. Consult a SEBI-registered advisor for investment decisions.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Process query
        if search_button and query:
            with st.spinner("⏳ Getting answer..."):
                response = api_client.query(
                    query,
                    st.session_state.language,
                    filters
                )
                
                if response:
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "timestamp": datetime.now()
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now()
                    })
                    
                    st.rerun()
                else:
                    st.error("❌ Failed to get response from API")
    
    with col2:
        # Sidebar content in right column
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0,166,81,0.1) 0%, rgba(0,217,127,0.1) 100%);
                        padding: 20px; border-radius: 12px; border: 1px solid rgba(0,166,81,0.2);
                        margin-bottom: 20px;">
                <h3 style="margin: 0 0 16px 0; color: #00A651; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">⚙️</span> Settings
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Language selector
        lang = UIComponents.language_selector()
        st.session_state.language = lang
        
        st.markdown("---")
        
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0,166,81,0.1) 0%, rgba(0,217,127,0.1) 100%);
                        padding: 20px; border-radius: 12px; border: 1px solid rgba(0,166,81,0.2);">
                <h3 style="margin: 0 0 16px 0; color: #00A651; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">💡</span> Quick Tips
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        quick_tips = {
            "en": [
                ("🔹 ELSS Lock-in", "Learn 3-year lock-in details"),
                ("🔹 Expense Ratios", "Compare fund costs"),
                ("🔹 Minimum SIP", "Check minimum amounts"),
                ("🔹 Risk Levels", "Understand fund risk"),
                ("🔹 Fund Performance", "View recent returns")
            ],
            "hi": [
                ("🔹 ELSS लॉक-इन", "3 साल की जानकारी"),
                ("🔹 व्यय अनुपात", "फंड लागत तुलना"),
                ("🔹 न्यूनतम SIP", "न्यूनतम राशि जांचें"),
                ("🔹 जोखिम स्तर", "फंड जोखिम समझें"),
                ("🔹 फंड प्रदर्शन", "हाल के रिटर्न देखें")
            ]
        }
        
        lang = st.session_state.language
        tips = quick_tips.get(lang, quick_tips["en"])
        
        for tip_title, tip_desc in tips:
            st.markdown(
                f"""
                <div style="background: white; padding: 10px 12px; border-radius: 8px; margin-bottom: 8px;
                            border-left: 3px solid #00A651; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <strong style="color: #00A651; font-size: 13px;">{tip_title}</strong><br>
                    <small style="color: #6B7280; font-size: 11px;">{tip_desc}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("---")
        
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0,166,81,0.1) 0%, rgba(0,217,127,0.1) 100%);
                        padding: 16px; border-radius: 12px; border: 1px solid rgba(0,166,81,0.2);">
                <h3 style="margin: 0 0 12px 0; color: #00A651; display: flex; align-items: center; gap: 8px; font-size: 14px;">
                    <span style="font-size: 16px;">📝</span> Quick Questions
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        sample_queries = {
            "en": [
                "What is ELSS?",
                "Minimum SIP?",
                "Expense ratio?",
                "Low-risk funds?"
            ],
            "hi": [
                "ELSS क्या है?",
                "न्यूनतम SIP?",
                "व्यय अनुपात?",
                "कम जोखिम?"
            ]
        }
        
        lang = st.session_state.language
        queries = sample_queries.get(lang, sample_queries["en"])
        
        for q in queries:
            if st.button(q, use_container_width=True, key=f"sample_{q}"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": q,
                    "timestamp": datetime.now()
                })
                
                with st.spinner("⏳ Getting answer..."):
                    response = api_client.query(q, st.session_state.language, {})
                    if response:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": datetime.now()
                        })
                
                st.rerun()
        
        st.markdown("---")
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(0,166,81,0.1) 0%, rgba(0,217,127,0.1) 100%);
                        padding: 16px; border-radius: 12px; border: 1px solid rgba(0,166,81,0.2);">
                <h3 style="margin: 0 0 8px 0; color: #00A651; font-size: 13px; font-weight: 700;">📊 Corpus</h3>
                <p style="margin: 0; font-size: 12px; color: #6B7280;">
                    <strong>47</strong> documents • <strong>6</strong> funds • <strong>Ollama LLM</strong>
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # ===== PROFESSIONAL FOOTER =====
    st.markdown("---")
    
    # Footer in columns
    col_f1, col_f2, col_f3, col_f4 = st.columns(4, gap="large")
    
    with col_f1:
        st.markdown(
            """
            ### 🏢 GROWW
            [📱 About Us](https://groww.in/about)  
            [💼 Careers](https://careers.groww.in)  
            [📰 Blog](https://groww.in/blog)  
            [🤝 Help & Support](https://groww.in/help)
            """,
            unsafe_allow_html=True
        )
    
    with col_f2:
        st.markdown(
            """
            ### 📊 PRODUCTS
            [📈 Stocks](https://groww.in/stocks)  
            [💰 Mutual Funds](https://groww.in/mutual-funds)  
            [💵 ETFs](https://groww.in/etf)  
            [🏦 Fixed Deposits](https://groww.in/fixed-deposits)
            """,
            unsafe_allow_html=True
        )
    
    with col_f3:
        st.markdown(
            """
            ### ⚖️ COMPLIANCE
            [Policies](https://groww.in/policies)  
            [🔐 Privacy](https://groww.in/privacy)  
            [📋 Disclosure](https://groww.in/disclosure)  
            [✅ Trust & Safety](https://groww.in/trust-safety)
            """,
            unsafe_allow_html=True
        )
    
    with col_f4:
        st.markdown(
            """
            ### 💻 THIS TOOL
            🤖 **Ollama LLM**  
            📦 **Chroma Cloud**  
            🎨 **Streamlit**  
            📄 **47 Documents**
            """,
            unsafe_allow_html=True
        )
    
    # Bottom disclaimers
    st.markdown("---")
    
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; color: #6B7280;">
            <p><strong>© 2024 Groww. All rights reserved.</strong></p>
            <p style="font-size: 12px; margin: 10px 0;">
                Built for educational & informational purposes only.
            </p>
            <p style="font-size: 11px; color: #9CA3AF; margin: 15px 0;">
                ✓ <strong>Disclaimer:</strong> This tool provides factual information from official sources only. 
                It does <strong>NOT</strong> provide investment advice, recommendations, or portfolio suggestions.
                Consult a SEBI-registered financial advisor before making investment decisions.
                <strong>No PII collected.</strong> All data remains local.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

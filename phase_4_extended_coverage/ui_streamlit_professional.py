"""
Phase 4 Streamlit UI - Professional Design (Inspired by dummyUi.py Reference)

Enhanced with:
- Professional topbar with navigation, branding, and language selector
- Redesigned footer with site map grid layout
- Premium color scheme and typography
- Improved spacing and visual hierarchy
- Responsive design for all screen sizes
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# Set page config
st.set_page_config(
    page_title="Groww Mutual Fund FAQ",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

PHASE4_API_URL = "http://localhost:8000"

# Professional CSS with modern design inspired by reference
PROFESSIONAL_CSS = """
<style>
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    }

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
    
    /* Main app */
    .stApp {
        background: #F8F9FB;
    }
    
    .main {
        padding: 0 !important;
    }

    /* ======================== TOPBAR ======================== */
    .topbar-wrapper {
        background: white;
        border-bottom: 1px solid #ECEEF2;
        position: sticky;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin: -1rem -1rem 0 -1rem;
        padding: 0;
    }

    .topbar {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 64px;
        gap: 24px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 48px;
        flex: 1;
    }

    .topbar-branding {
        display: flex;
        align-items: center;
        gap: 12px;
        white-space: nowrap;
    }

    .topbar-logo {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00A651 0%, #00D97F 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
    }

    .topbar-brand-text {
        font-size: 16px;
        font-weight: 700;
        color: #1F3A3D;
    }

    .topbar-tagline {
        font-size: 12px;
        color: #98A1B3;
    }

    .topbar-nav {
        display: flex;
        gap: 32px;
        align-items: center;
    }

    .topbar-nav-item {
        font-size: 14px;
        color: #344054;
        font-weight: 500;
        cursor: pointer;
        transition: color 0.3s;
        white-space: nowrap;
    }

    .topbar-nav-item:hover {
        color: #00A651;
    }

    .topbar-right {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .topbar-language {
        display: flex;
        gap: 8px;
        align-items: center;
        padding: 6px 12px;
        border-radius: 8px;
        background: #F3F4F6;
    }

    .topbar-language span {
        font-size: 13px;
        cursor: pointer;
        font-weight: 500;
        color: #6B7280;
        transition: all 0.3s;
    }

    .topbar-language span.active {
        color: #00A651;
        font-weight: 700;
    }

    /* ======================== MAIN CONTENT ======================== */
    .content-wrapper {
        max-width: 1400px;
        margin: 0 auto;
        padding: 32px 32px;
    }

    .chat-card {
        background: white;
        border-radius: 16px;
        border: 1px solid #ECEEF2;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }

    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 16px;
        background: #FAFBFC;
        border-radius: 12px;
        border: 1px solid #EDF2F7;
        margin-bottom: 20px;
    }

    .chat-container::-webkit-scrollbar {
        width: 8px;
    }

    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: #D0D5DD;
        border-radius: 4px;
    }

    .chat-container::-webkit-scrollbar-thumb:hover {
        background: #B0B5BD;
    }

    .message-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 14px;
    }

    .message-bubble-user {
        background: linear-gradient(135deg, #00A651 0%, #00D97F 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0, 166, 81, 0.2);
    }

    .message-bot {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 14px;
    }

    .message-bubble-bot {
        background: white;
        color: #1F3A3D;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        border: 1px solid #E5E7EB;
        max-width: 70%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .input-section {
        display: flex;
        gap: 12px;
        align-items: center;
        margin-bottom: 16px;
    }

    .input-section input {
        flex: 1;
        padding: 12px 16px;
        border: 2px solid #E5E7EB;
        border-radius: 10px;
        font-size: 14px;
        transition: border-color 0.3s;
    }

    .input-section input:focus {
        outline: none;
        border-color: #00A651;
        box-shadow: 0 0 0 3px rgba(0, 166, 81, 0.1);
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 20px;
    }

    .info-card {
        background: linear-gradient(135deg, rgba(0, 166, 81, 0.08) 0%, rgba(0, 217, 127, 0.08) 100%);
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #00A651;
    }

    .info-card h4 {
        margin: 0 0 8px 0;
        font-size: 14px;
        color: #00A651;
        font-weight: 700;
    }

    .info-card ul {
        margin: 0;
        padding-left: 20px;
        font-size: 13px;
        color: #4B5563;
    }

    .info-card li {
        margin-bottom: 4px;
    }

    /* ======================== FOOTER ======================== */
    .footer-section {
        background: #1F3A3D;
        color: white;
        margin: 60px -1rem -1rem -1rem;
        padding: 60px 32px 40px;
        border-top: 1px solid #2D5558;
    }

    .footer-container {
        max-width: 1400px;
        margin: 0 auto;
    }

    .footer-main {
        display: grid;
        grid-template-columns: 1.3fr repeat(3, 1fr);
        gap: 48px;
        margin-bottom: 48px;
    }

    .footer-company {
        display: flex;
        flex-direction: column;
        gap: 16px;
    }

    .footer-company-branding {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 800;
    }

    .footer-company-logo {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00A651 0%, #00D97F 100%);
    }

    .footer-company-info {
        font-size: 13px;
        line-height: 1.7;
        color: #D1D5DB;
    }

    .footer-company-info div {
        margin-bottom: 8px;
    }

    .footer-social {
        display: flex;
        gap: 12px;
        margin-top: 12px;
    }

    .social-icon {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 1px solid #4B5563;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.3s;
        background: rgba(255,255,255,0.05);
    }

    .social-icon:hover {
        border-color: #00A651;
        background: rgba(0, 166, 81, 0.15);
        color: #00A651;
    }

    .footer-col h4 {
        font-size: 15px;
        font-weight: 700;
        color: white;
        margin: 0 0 16px 0;
    }

    .footer-col a {
        display: block;
        font-size: 13px;
        color: #D1D5DB;
        text-decoration: none;
        margin-bottom: 12px;
        transition: color 0.3s;
    }

    .footer-col a:hover {
        color: #00A651;
    }

    .footer-divider {
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 32px 0;
    }

    .footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: #9CA3AF;
        flex-wrap: wrap;
        gap: 16px;
    }

    .footer-bottom-links {
        display: flex;
        gap: 24px;
    }

    .footer-bottom-links a {
        color: #9CA3AF;
        text-decoration: none;
        transition: color 0.3s;
    }

    .footer-bottom-links a:hover {
        color: #00A651;
    }

    /* ======================== BUTTONS ======================== */
    .btn {
        padding: 10px 16px;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
    }

    .btn-primary {
        background: linear-gradient(135deg, #00A651 0%, #00D97F 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(0, 166, 81, 0.2);
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 166, 81, 0.3);
    }

    .btn-secondary {
        background: #F3F4F6;
        color: #6B7280;
    }

    .btn-secondary:hover {
        background: #E5E7EB;
        color: #4B5563;
    }

    /* ======================== RESPONSIVE ======================== */
    @media (max-width: 1200px) {
        .topbar {
            padding: 0 24px;
        }
        .topbar-nav {
            gap: 24px;
        }
        .footer-main {
            grid-template-columns: 1fr 1fr;
            gap: 32px;
        }
        .content-wrapper {
            padding: 24px;
        }
    }

    @media (max-width: 768px) {
        .topbar {
            height: auto;
            flex-wrap: wrap;
            padding: 12px 16px;
        }
        .topbar-left {
            gap: 16px;
            flex-basis: 100%;
        }
        .topbar-nav {
            display: none;
        }
        .topbar-right {
            flex-basis: 100%;
            justify-content: flex-end;
        }
        .footer-main {
            grid-template-columns: 1fr;
            gap: 24px;
        }
        .footer-bottom {
            flex-direction: column;
            align-items: flex-start;
        }
        .chat-container {
            height: 300px;
        }
        .message-bubble-user,
        .message-bubble-bot {
            max-width: 90%;
        }
        .info-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""

st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"


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


def render_topbar():
    """Render professional topbar with navigation."""
    st.markdown(
        """
        <div class="topbar-wrapper">
            <div class="topbar">
                <div class="topbar-left">
                    <div class="topbar-branding">
                        <div class="topbar-logo">₹</div>
                        <div>
                            <div class="topbar-brand-text">Groww</div>
                            <div class="topbar-tagline">Fund FAQ</div>
                        </div>
                    </div>
                    <div class="topbar-nav">
                        <div class="topbar-nav-item">About</div>
                        <div class="topbar-nav-item">Funds</div>
                        <div class="topbar-nav-item">Resources</div>
                        <div class="topbar-nav-item">Help</div>
                    </div>
                </div>
                <div class="topbar-right">
                    <div class="topbar-language">
                        <span class="active">🇬🇧 EN</span>
                        <span>|</span>
                        <span>🇮🇳 HI</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_footer():
    """Render professional footer using native Streamlit columns."""
    st.markdown("---")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4, gap="large")
    
    with col_f1:
        st.markdown(
            """
            ### 🏢 COMPANY
            [About Us](https://groww.in/about)  
            [Careers](https://careers.groww.in)  
            [Blog](https://groww.in/blog)  
            [Press](https://groww.in/press)
            """,
            unsafe_allow_html=True
        )
    
    with col_f2:
        st.markdown(
            """
            ### 📊 PRODUCTS
            [Stocks](https://groww.in/stocks)  
            [Mutual Funds](https://groww.in/mutual-funds)  
            [ETFs](https://groww.in/etf)  
            [Fixed Deposits](https://groww.in/fixed-deposits)
            """,
            unsafe_allow_html=True
        )
    
    with col_f3:
        st.markdown(
            """
            ### ⚖️ SUPPORT
            [Help Center](https://groww.in/help)  
            [Policies](https://groww.in/policies)  
            [Privacy](https://groww.in/privacy)  
            [Contact](https://groww.in/contact)
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
    
    st.markdown("---")
    
    st.markdown(
        """
        <div style="text-align: center; padding: 20px; color: #6B7280;">
            <p><strong>© 2024 Groww. All rights reserved.</strong></p>
            <p style="font-size: 12px; margin: 10px 0;">
                Built for educational & informational purposes only.
            </p>
            <p style="font-size: 11px; color: #9CA3AF; margin: 15px 0;">
                ✓ <strong>Disclaimer:</strong> This application provides factual information from official public sources only. 
                It does NOT provide investment advice, recommendations, or portfolio suggestions.
                Always consult a SEBI-registered financial advisor before making investment decisions.
                No personal information is collected or stored.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """Main Streamlit application."""
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "en"
    
    # Render topbar
    render_topbar()
    
    # Sticky header section
    st.markdown(
        """
        <div style="position: sticky; top: 64px; background: #F8F9FB; padding: 16px 32px; margin: 0 -1rem 0 -1rem; z-index: 999; border-bottom: 1px solid #ECEEF2;">
            <h1 style="margin: 0 0 4px 0; font-size: 28px; color: #1F3A3D; font-weight: 800;">
                💡 Mutual Fund FAQ Assistant
            </h1>
            <p style="margin: 0; font-size: 14px; color: #6B7280;">
                Get instant answers about mutual funds, expense ratios, ELSS, SIP, and more
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Main content
    st.markdown('<div class="content-wrapper" style="padding-top: 12px;">', unsafe_allow_html=True)
    
    # API health check
    api_client = APIClient()
    health_status = api_client.health()
    
    if not health_status:
        st.error("⚠️ API Server Offline - Please start the API on port 8000")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Page layout
    col_main, col_sidebar = st.columns([2.5, 1], gap="large")
    
    with col_main:
        
        # Chat card
        st.markdown('<div class="chat-card">', unsafe_allow_html=True)
        
        # Chat display
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        if st.session_state.messages:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="message-user"><div class="message-bubble-user">{msg["content"]}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    response = msg["content"]
                    answer = response.get("answer", "No answer generated")
                    st.markdown(
                        f'<div class="message-bot"><div class="message-bubble-bot">{answer}</div></div>',
                        unsafe_allow_html=True
                    )
        else:
            st.markdown(
                """
                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;
                           height: 200px; color: #9CA3AF; text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 12px;">💬</div>
                    <div style="font-size: 16px; font-weight: 600; color: #6B7280;">No messages yet</div>
                    <div style="font-size: 13px; color: #9CA3AF; margin-top: 4px;">Ask a question to get started!</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input section
        query = st.text_input(
            "💭 Your Question",
            placeholder="Ask about expense ratios, SIP, ELSS lock-in...",
            key="query_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            search_btn = st.button("🚀 Send", use_container_width=True, key="send")
        
        with col_btn2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True, key="clear")
        
        if clear_btn:
            st.session_state.messages = []
            st.rerun()
        
        if search_btn and query:
            with st.spinner("⏳ Getting answer..."):
                response = api_client.query(query, st.session_state.language, {})
                
                if response:
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
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close chat-card
        
        # Info sections
        st.markdown(
            """
            <div class="info-grid">
                <div class="info-card">
                    <h4>✅ You Can Ask (Facts Only)</h4>
                    <ul>
                        <li>Expense ratio?</li>
                        <li>Minimum SIP amount?</li>
                        <li>ELSS lock-in period?</li>
                        <li>Fund riskometer level?</li>
                        <li>How to download statements?</li>
                    </ul>
                </div>
                <div style="background: linear-gradient(135deg, rgba(220, 38, 38, 0.08) 0%, rgba(239, 68, 68, 0.08) 100%);
                           padding: 16px; border-radius: 12px; border-left: 4px solid #DC2626;">
                    <h4 style="color: #DC2626; margin: 0 0 8px 0;">❌ We Don't Provide</h4>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #4B5563;">
                        <li style="margin-bottom: 4px;">Investment advice or recommendations</li>
                        <li style="margin-bottom: 4px;">Buy/sell suggestions</li>
                        <li style="margin-bottom: 4px;">Portfolio planning</li>
                        <li style="margin-bottom: 4px;">Return predictions</li>
                        <li>Personal financial advice</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_sidebar:
        st.subheader("⚙️ Settings")
        
        lang = st.radio(
            "Language",
            ["🇬🇧 English", "🇮🇳 हिंदी"],
            label_visibility="collapsed"
        )
        st.session_state.language = "en" if "🇬🇧" in lang else "hi"
        
        st.divider()
        
        st.subheader("💡 Quick Tips")
        tips = [
            ("ELSS Basics", "3-year lock-in explained"),
            ("Expense Ratios", "Compare fund costs"),
            ("Minimum SIP", "Check minimums"),
            ("Risk Levels", "Understand riskometer"),
            ("Fund Performance", "View recent returns")
        ]
        
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
        
        st.divider()
        
        st.subheader("📊 Corpus Info")
        st.markdown(
            """
            - **47** documents indexed
            - **6** mutual funds covered
            - **Ollama LLM** (local)
            - **Chroma Cloud** (vector DB)
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close content-wrapper
    
    # Render professional footer
    render_footer()


if __name__ == "__main__":
    main()

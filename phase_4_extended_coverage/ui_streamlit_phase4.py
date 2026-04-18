"""
Phase 4 Streamlit UI Components

Provides:
- Language selector (English / हिंदी)
- Multi-language query input
- Advanced filter UI
- Response display with translation indicators
- Query history with language tracking
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from enum import Enum

PHASE4_API_URL = "http://localhost:8000"


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"


class UIComponents:
    """Reusable Streamlit UI components."""
    
    @staticmethod
    def language_selector() -> str:
        """
        Language selector widget.
        
        Returns:
            Selected language code ("en" or "hi")
        """
        st.sidebar.markdown("### 🌍 Language")
        
        language_options = {
            "🇬🇧 English": Language.ENGLISH.value,
            "🇮🇳 हिंदी": Language.HINDI.value
        }
        
        selected_display = st.sidebar.radio(
            "Select your language:",
            list(language_options.keys()),
            key="language_selector",
            horizontal=True
        )
        
        return language_options[selected_display]
    
    @staticmethod
    def query_input(language: str) -> str:
        """
        Query input widget with language-specific placeholder.
        
        Args:
            language: Selected language ("en" or "hi")
        
        Returns:
            User query text
        """
        if language == Language.ENGLISH.value:
            placeholder = "Ask about mutual funds, expense ratios, ELSS, etc."
            label = "🔍 Search Query"
        else:  # Hindi
            placeholder = "म्यूचुअल फंड, व्यय अनुपात, ELSS आदि के बारे में पूछें"
            label = "🔍 खोज क्वेरी"
        
        query = st.text_input(
            label,
            placeholder=placeholder,
            key="query_input"
        )
        
        return query
    
    @staticmethod
    def filter_expander(language: str) -> Dict[str, Any]:
        """
        Advanced filter UI in expandable section.
        
        Args:
            language: Selected language
        
        Returns:
            Filter criteria dictionary
        """
        filters = {}
        
        with st.expander(
            "🔽 Advanced Filters" if language == Language.ENGLISH.value else "🔽 उन्नत फ़िल्टर",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk level filter
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
                # Category filter
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
                # Expense ratio filter
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
                # AUM filter
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
        """
        Render API response with formatting.
        
        Args:
            response: API response dictionary
            language: Selected language
        """
        if not response:
            return
        
        # Main answer section
        st.markdown("---")
        st.markdown("### 📝 Answer")
        
        answer = response.get("answer", "No answer generated")
        if language == Language.HINDI.value:
            answer = response.get("answer_hi", answer)
        
        st.write(answer)
        
        # Sources section
        if response.get("sources"):
            st.markdown("### 📚 Sources")
            sources = response.get("sources", [])
            
            for i, source in enumerate(sources, 1):
                with st.expander(
                    f"Source {i}: {source.get('source', 'Unknown')}",
                    expanded=(i == 1)
                ):
                    st.write(f"**Relevance:** {source.get('relevance', 0):.1%}")
                    st.write(f"**Content:**\n{source.get('chunk', 'N/A')}")
        
        # Metadata section
        st.markdown("### ⏱️ Metadata")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            latency = response.get("latency_ms", 0)
            st.metric(
                "Response Time",
                f"{latency}ms",
                delta="⚡" if latency < 1000 else "⏳"
            )
        
        with col2:
            lang_detected = response.get("language_detected", "en").upper()
            st.metric(
                "Language Detected",
                lang_detected,
                delta="✓ Auto" if lang_detected != language.upper() else ""
            )
        
        with col3:
            filters_applied = response.get("filters_applied", False)
            st.metric(
                "Filters",
                "Applied" if filters_applied else "None",
                delta=f"({response.get('active_filters', [])})" if filters_applied else ""
            )
        
        # Additional info
        if response.get("matched_chunks"):
            st.info(
                f"**Found** {response.get('matched_chunks')} matching documents | "
                f"**Filtered** {response.get('filtered_chunks')} results"
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
        """
        Send query to API.
        
        Args:
            query: User query
            language: Language code
            filters: Filter criteria
        
        Returns:
            API response or None if error
        """
        try:
            payload = {
                "query": query,
                "language": language
            }
            
            if filters:
                payload["filters"] = filters
            
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {str(e)}")
            return None
    
    def get_languages(self) -> List[str]:
        """Get supported languages."""
        try:
            response = requests.get(
                f"{self.base_url}/languages",
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("languages", ["en", "hi"])
        except Exception as e:
            st.warning(f"Could not fetch languages: {e}")
        
        return ["en", "hi"]
    
    def get_filters(self) -> Dict[str, Any]:
        """Get available filters."""
        try:
            response = requests.get(
                f"{self.base_url}/filters",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.warning(f"Could not fetch filters: {e}")
        
        return {}
    
    def health_check(self) -> bool:
        """Check API health."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []
    
    if "last_response" not in st.session_state:
        st.session_state.last_response = None
    
    if "query_input_value" not in st.session_state:
        st.session_state.query_input_value = ""


def render_page():
    """Main page rendering logic."""
    # Initialize
    initialize_session_state()
    api_client = APIClient()
    
    # Page config
    st.set_page_config(
        page_title="Groww Mutual Fund FAQ - Phase 4",
        page_icon="💰",
        layout="wide"
    )
    
    # Page title and disclaimer at TOP (prominent)
    st.markdown("""
    # 💰 Groww Mutual Fund FAQ Assistant
    
    ### 📋 Important: Facts Only. No Investment Advice.
    
    This assistant answers **factual questions only** about mutual fund schemes using official sources.  
    We do not provide investment advice, portfolio recommendations, or performance predictions.  
    
    ✓ **We can answer:** Expense ratio, ELSS lock-in, minimum SIP, exit load, NAV, riskometer, benchmarks, how to download statements  
    ✗ **We cannot answer:** Should I buy/sell? Best fund for me? Will returns be higher? Portfolio advice  
    
    ---
    """)
    
    # Sidebar
    st.sidebar.title("🚀 Phase 4 Features")
    st.sidebar.markdown("""
    ✨ **Capabilities**:
    - 🌍 Multi-language (English + हिंदी)
    - 🔍 Advanced filtering
    - ⚡ Fast responses
    - 📚 Official sources only
    """)
    
    # Language selection
    language = UIComponents.language_selector()
    
    # API health check
    if not api_client.health_check():
        st.error(
            "⚠️ API Server Unavailable\n\n"
            "Please ensure the Phase 4 API is running:\n"
            "`python phase_4_extended_coverage/api_server_phase4.py 8000`"
        )
        return
    
    # ========================================================================
    # WELCOME SECTION WITH EXAMPLE QUESTIONS
    # ========================================================================
    
    st.markdown("### 💬 Example Questions")
    
    if language == Language.ENGLISH.value:
        examples = [
            "What is the expense ratio of a typical large-cap fund?",
            "What does ELSS lock-in period mean?",
            "How do I download my mutual fund statement?",
        ]
        instruction_text = "**Click an example or ask your own factual question about mutual funds:**"
    else:
        examples = [
            "एक विशिष्ट लार्ज-कैप फंड का व्यय अनुपात क्या है?",
            "ELSS लॉक-इन अवधि का क्या मतलब है?",
            "मैं अपना म्यूचुअल फंड स्टेटमेंट कैसे डाउनलोड करूं?",
        ]
        instruction_text = "**एक उदाहरण पर क्लिक करें या म्यूचुअल फंड के बारे में अपना प्रश्न पूछें:**"
    
    st.markdown(instruction_text)
    
    # Display clickable example buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(examples[0], key="ex1"):
            st.session_state.query_input_value = examples[0]
    
    with col2:
        if st.button(examples[1], key="ex2"):
            st.session_state.query_input_value = examples[1]
    
    with col3:
        if st.button(examples[2], key="ex3"):
            st.session_state.query_input_value = examples[2]
    
    st.markdown("---")
    
    # Query input
    if language == Language.ENGLISH.value:
        query = st.text_input(
            "🔍 Your Question",
            value=st.session_state.get("query_input_value", ""),
            placeholder="Ask about expense ratios, ELSS, NAV, minimum SIP, etc.",
            key="query_input_field"
        )
    else:
        query = st.text_input(
            "🔍 आपका प्रश्न",
            value=st.session_state.get("query_input_value", ""),
            placeholder="व्यय अनुपात, ELSS, NAV आदि के बारे में पूछें",
            key="query_input_field"
        )
    
    # Clear the session value after use
    st.session_state.query_input_value = ""
    
    # Filters
    filters = UIComponents.filter_expander(language)
    
    # Search button
    if st.button(
        "🔍 Search" if language == Language.ENGLISH.value else "🔍 खोजें",
        type="primary"
    ):
        if query:
            with st.spinner(
                "Searching..." if language == Language.ENGLISH.value else "खोज रहे हैं..."
            ):
                response = api_client.query(query, language, filters)
                
                if response:
                    st.session_state.last_response = response
                    
                    # Add to history
                    st.session_state.query_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "query": query,
                        "language": language,
                        "filters_count": len(filters)
                    })
                    
                    # Render response
                    UIComponents.render_response(response, language)
                else:
                    st.error(
                        "Failed to process query" if language == Language.ENGLISH.value 
                        else "क्वेरी को प्रोसेस करने में विफल"
                    )
        else:
            st.warning(
                "Please enter a query" if language == Language.ENGLISH.value 
                else "कृपया एक क्वेरी दर्ज करें"
            )
    
    # Show previous response if available
    if st.session_state.last_response and not query:
        UIComponents.render_response(st.session_state.last_response, language)
    
    # Query history sidebar
    if st.session_state.query_history:
        st.sidebar.markdown("### 📜 Query History")
        for i, item in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            timestamp = item["timestamp"][:16]
            lang_icon = "🇬🇧" if item["language"] == "en" else "🇮🇳"
            st.sidebar.caption(f"{i}. {lang_icon} {timestamp}\n_{item['query'][:40]}..._")


if __name__ == "__main__":
    render_page()

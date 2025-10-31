import streamlit as st
import re
import json

def main():
    st.set_page_config(
        page_title="UScan - Universal Structure Scanner",
        page_icon="🔍",
        layout="wide"
    )
    
    # Header
    st.title("🔍 UScan - Universal Structure Scanner")
    st.markdown("### Empower everyone. Level the playing field.")
    st.markdown("*Parse any financial structure — FCN, Autocall, Reverse Convertible — from email, PDF, or chat*")
    
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📥 Input")
        text_input = st.text_area(
            "Paste your financial structure text:",
            placeholder="Example: USD Call Option on AAPL, Strike: 220, Maturity: 3 months, Coupon: 8%...",
            height=200
        )
        
        analyze_btn = st.button("🚀 Analyze Structure", type="primary")
    
    with col2:
        st.subheader("💡 Examples")
        st.markdown("""
        **FCN Example:**
        ```
        USD FCN on TSLA
        Strike: 850
        Maturity: 1 year
        Coupon: 15%
        ```
        
        **Autocall Example:**
        ```
        EUR Autocall on NVDA
        Strike: 95%
        Barrier: 70%
        Coupon: 8% quarterly
        ```
        """)
    
    if analyze_btn:
        if text_input.strip():
            with st.spinner("Analyzing structure..."):
                analyze_structure(text_input)
        else:
            st.warning("⚠️ Please enter some text to analyze")

def analyze_structure(text):
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Detection patterns
    patterns = {
        "Instrument Type": {
            "pattern": r'\b(FCN|Autocall|Reverse Convertible|Call Option|Put Option|Structured Note)\b',
            "description": "Type of financial instrument"
        },
        "Underlying Asset": {
            "pattern": r'(?:on|underlying|reference)\s+([A-Z]{1,5})',
            "description": "Stock or index the instrument is based on"
        },
        "Strike Price": {
            "pattern": r'(?:strike|strik)[:\s]+([0-9.,]+)',
            "description": "Strike price level"
        },
        "Maturity": {
            "pattern": r'(?:maturity|tenor|term)[:\s]+([0-9]+\s*(?:months?|years?|days?|weeks?))',
            "description": "Time to expiration"
        },
        "Currency": {
            "pattern": r'([A-Z]{3})\s+(?:FCN|Call|Put|Autocall)',
            "description": "Currency denomination"
        },
        "Coupon": {
            "pattern": r'(?:coupon|interest)[:\s]+([0-9.]+%)',
            "description": "Interest or coupon rate"
        }
    }
    
    results = {}
    
    # Analyze each pattern
    for field, config in patterns.items():
        match = re.search(config['pattern'], text, re.IGNORECASE)
        if match:
            results[field] = {
                "value": match.group(1),
                "description": config['description']
            }
    
    # Display results
    if results:
        for field, data in results.items():
            st.success(f"**{field}:** {data['value']}")
            st.caption(f"*{data['description']}*")
    else:
        st.error("❌ No financial structure patterns detected.")
        st.info("💡 Try using one of the example formats above.")
    
    # Raw text preview
    with st.expander("🔍 View Raw Text Analysis"):
        st.text(text)

if __name__ == "__main__":
    main()

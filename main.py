import streamlit as st
from src.drift_detector import IntentDriftDetector

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Placement Intent Tracker",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------
st.markdown("""
<style>
    /* Global Styles */
    .block-container { padding-top: 2rem; }
    
    /* Intent Badge (Pill) */
    .intent-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 0.3rem;
        letter-spacing: 0.05em;
    }
    
    /* Intent Colors */
    .intent-interest { background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    .intent-information { background-color: #e0e7ff; color: #3730a3; border: 1px solid #a5b4fc; }
    .intent-comparison { background-color: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
    .intent-complaint { background-color: #ffe4e6; color: #be123c; border: 1px solid #fda4af; }
    .intent-decision { background-color: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
    .intent-unknown { background-color: #f3f4f6; color: #4b5563; border: 1px solid #d1d5db; }
    
    /* Drift Alert Box */
    .drift-alert {
        margin-top: 0.5rem;
        padding: 0.75rem;
        background-color: #fff1f2;
        border-left: 4px solid #f43f5e;
        border-radius: 4px;
        color: #881337;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input Field Fix */
    .stChatInput { position: fixed; bottom: 0; }
    
    /* Sidebar Status */
    .status-box { padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; font-weight: bold; text-align: center; }
    .status-active { background-color: #ecfccb; color: #365314; border: 1px solid #bef264; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Utils
# --------------------------------------------------
def get_intent_class(intent_name):
    """Map intent names to CSS classes."""
    if not intent_name: return "intent-unknown"
    return f"intent-{intent_name.lower().replace(' ', '-')}"

# --------------------------------------------------
# Initialize Detector
# --------------------------------------------------
@st.cache_resource
def load_detector():
    return IntentDriftDetector()

detector = load_detector()

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("🎓 Tracker Status")
    
    if st.button("Start New Session", type="primary"):
        detector.reset()
        st.session_state.messages = []
        st.session_state.turn_count = 0
        st.rerun()

    st.divider()
    
    # Legend
    st.markdown("### Intent Legend")
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
        <span class="intent-badge intent-interest">INTEREST</span>
        <span class="intent-badge intent-information">INFORMATION</span>
        <span class="intent-badge intent-comparison">COMPARISON</span>
        <span class="intent-badge intent-complaint">COMPLAINT</span>
        <span class="intent-badge intent-decision">DECISION</span>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# Main Chat UI
# --------------------------------------------------
st.markdown("## Student Placement Intent Journey Tracker")
st.caption("Monitoring intent evolution from ambition to decision.")

# Render Messages
for msg in st.session_state.messages:
    # User Message
    with st.chat_message("user"):
        st.write(msg["content"])
        
        # Metadata Display
        analysis = msg["analysis"]
        detected = analysis.get("detected_intent", "unknown")
        current = analysis.get("current_intent", "unknown")
        
        # Check for Unknown Input Case
        if detected == "unknown" and current != "unknown":
            # 1. Intent Badge: UNKNOWN
            st.markdown(f"""
                <span class="intent-badge intent-unknown">
                    Intent: UNKNOWN
                </span>
            """, unsafe_allow_html=True)
            
            # 2. Continuation Message
            st.caption(f"Input unclear, continuing old intent: **{current.upper()}**")
            
        else:
            # Standard Case
            css_class = get_intent_class(current)
            st.markdown(f"""
                <span class="intent-badge {css_class}">
                    Intent: {current}
                </span>
            """, unsafe_allow_html=True)
        
        # 3. Drift Alert (if applicable)
        if analysis["intent_drift"]:
            prev = analysis["previous_intent"]
            curr = analysis["current_intent"]
            st.markdown(f"""
                <div class="drift-alert">
                    <span>🚨 <b>Drift Detected:</b> {prev.upper()} → {curr.upper()}</span>
                </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# Chat Input
# --------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.turn_count += 1
    
    # Run Detection
    result = detector.update(prompt)
    
    # Store message + analysis
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "analysis": result
    })
    
    st.rerun()

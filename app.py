import streamlit as st
from integration import IntegrationEngine, ComputationResult

class ApplicationUI:
    def __init__(self):
        self.engine = IntegrationEngine()
        self._initialize_state()
        
    def _initialize_state(self):
        if "history" not in st.session_state:
            st.session_state.history = []
        if "expr_input" not in st.session_state:
            st.session_state.expr_input = ""
        if "last_result" not in st.session_state:
            st.session_state.last_result = None

    def _handle_keypress(self, label: str, val: str):
        if label == "C":
            st.session_state.expr_input = ""
        elif label == "⌫":
            st.session_state.expr_input = st.session_state.expr_input[:-1]
        else:
            st.session_state.expr_input += val

    def render_live_preview(self):
        raw = st.session_state.expr_input
        if raw:
            # Swap python syntax for math syntax purely for visual preview
            pretty = raw.replace("**", "^").replace("*", "·").replace("/", "÷")
            st.markdown(
                f"**Live Preview:** &nbsp; <span style='color: #4CAF50; font-family: monospace; font-size: 1.1rem;'>{pretty}</span>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown("**Live Preview:** &nbsp; *Type an expression...*")

    def render_virtual_keyboard(self):
        # Using Full-width '＋' so Streamlit doesn't render it as a markdown bullet point
        keys = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("⌫", "BACKSPACE"), ("C", "CLEAR")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("÷", "/")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("＋", "+"), ("−", "-")],
            [("0", "0"), (".", "."), ("x", "x"), ("(", "("), (")", ")")],
            [("x²", "**2"), ("xⁿ", "**"), ("√", "sqrt("), ("sin", "sin("), ("cos", "cos(")]
        ]
        
        # Squeezed the button height slightly to ensure it fits without scrolling
        st.markdown("""
        <style>
            div[data-testid='stButton'] button {
                height: 2.0rem;
                min-height: 2.0rem;
                padding: 0.1rem;
            }
        </style>
        """, unsafe_allow_html=True)
        
        for r_idx, row in enumerate(keys):
            cols = st.columns(5)
            for c_idx, (label, val) in enumerate(row):
                with cols[c_idx]:
                    st.button(
                        label, 
                        on_click=self._handle_keypress, 
                        args=(label, val), 
                        use_container_width=True, 
                        key=f"btn_{r_idx}_{c_idx}"
                    )

    def render_trail(self, res: ComputationResult):
        st.markdown("### ✨ Final Answer")
        st.success(f"$$ \\int f(x)dx = {res.final_answer} $$")
        
        st.divider()
        
        st.markdown("#### Problem Breakdown")
        st.info(f"$$ {res.given} $$")
        st.caption(f"**Method Used:** {res.method}")
        
        with st.expander("View Step-by-Step Breakdown", expanded=False):
            for i, step in enumerate(res.steps, 1):
                st.markdown(f"**Step {i}:**")
                st.latex(step)
                
        with st.expander("View Verification (Derivative Check)", expanded=False):
            parts = res.verification.split("\n\n")
            if len(parts) >= 2:
                st.latex(parts[0])
                if "Successful" in parts[1]:
                    st.success(parts[1])
                else:
                    st.warning(parts[1])
            else:
                st.warning(res.verification)
                
        runtime = res.summary.get("Runtime", "N/A")
        iterations = res.summary.get("Iterations", "N/A")
        time_computed = res.summary.get("Timestamp", " N/A").split(" ")[1]
        
        st.markdown(
            f"<p style='text-align: right; font-size: 0.8rem; color: #888; margin-top: 1rem;'>"
            f"⏱ {runtime} &nbsp;|&nbsp; 🔄 {iterations} iter &nbsp;|&nbsp; 🕒 {time_computed}</p>", 
            unsafe_allow_html=True
        )

    def run(self):
        st.set_page_config(page_title="Symbolic Integrator", layout="wide", page_icon="∫")
        
        # --- UI REFINEMENT: CUSTOM CSS ---
        st.markdown("""
        <style>
            [data-testid="stHeader"] { display: none !important; }
            .main .block-container {
                padding-top: 1rem !important; 
                padding-bottom: 0rem !important;
                max-height: 100vh;
            }
            html, body, [data-testid="stAppViewContainer"] {
                overflow: hidden !important;
            }
            
            /* STRICT VERTICAL SEPARATOR */
            [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-of-type(1) {
                border-right: 2px solid rgba(128, 128, 128, 0.4) !important; 
                padding-right: 2rem !important;
                height: 95vh;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-of-type(2) {
                padding-left: 1.5rem !important;
                height: 95vh; 
                overflow-y: auto; 
                padding-right: 1rem; 
            }
            
            /* Remove margins to fit everything on one screen */
            h1 {
                margin-top: -15px !important;
                padding-bottom: 0px !important;
                margin-bottom: 0px !important;
            }
            div[data-testid="stExpanderDetails"] {
                padding-bottom: 20px !important; 
            }
            
            footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
        # ---------------------------------
        
        col_left, col_right = st.columns([1, 1.3], gap="large")
        
        with col_left:
            st.markdown("<h1>∫ Indefinite Integration</h1>", unsafe_allow_html=True)
            st.caption("Enter a mathematical expression to compute its indefinite integral.")
            
            # 1. Live Preview
            self.render_live_preview()
            
            # 2. Input Text
            st.text_input("Integrand f(x)", key="expr_input", placeholder="e.g., 3*x**2 or sin(x)", label_visibility="collapsed")
            
            # 3. Quick Hand Calculator
            with st.expander("🖩 Quick Hand Calculator", expanded=True):
                self.render_virtual_keyboard()
                
            # Removed the extra <br> here so the button hugs the calculator and doesn't require scrolling
            submit_button = st.button("Compute Integral", type="primary", use_container_width=True)

            if submit_button:
                if not st.session_state.expr_input.strip():
                    st.error("Please enter an integrand.")
                else:
                    with st.spinner("Integrating..."):
                        current_input = st.session_state.expr_input.strip()
                        result = self.engine.compute(current_input)
                        
                        st.session_state.last_result = result
                        
                        if result.is_success:
                            if not st.session_state.history or st.session_state.history[-1]["input"] != current_input:
                                st.session_state.history.append({
                                    "input": current_input,
                                    "result": result
                                })

        with col_right:
            if st.session_state.last_result:
                if st.session_state.last_result.is_success:
                    self.render_trail(st.session_state.last_result)
                else:
                    st.error(f"Computation Failed: {st.session_state.last_result.error_message}")
            else:
                st.info("Enter an expression on the left and click **Compute Integral** to see the solution here.")
                
                # Replaced margin-top with Flexbox to perfectly center the credits block vertically and horizontally
                st.markdown(
                    """
                    <div style='display: flex; flex-direction: column; justify-content: center; align-items: center; height: 70vh; color: rgba(128,128,128,0.5);'>
                        <h4 style='margin-bottom: 0; color: rgba(128,128,128,0.5);'>MADE BY UNDISPUTEDS</h4>
                        <p style='font-size: 0.9rem;'>Aaron Mayor &nbsp;|&nbsp; Henry Pula &nbsp;|&nbsp; Johnbert Malinis</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    app = ApplicationUI()
    app.run()
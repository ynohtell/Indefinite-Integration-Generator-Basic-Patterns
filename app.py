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

    def _append_to_input(self, val: str):
        st.session_state.expr_input += val

    def render_virtual_keyboard(self):
        keys = [
            [("x²", "**2"), ("x³", "**3"), ("xⁿ", "**"), ("√", "sqrt(")],
            [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("eˣ", "exp(")],
            [("π", "pi"), ("+", " + "), ("-", " - "), ("*", " * ")],
            [("/", " / "), ("(", "("), (")", ")"), ("Clear", "CLEAR")]
        ]
        
        for row in keys:
            cols = st.columns(4)
            for i, (label, val) in enumerate(row):
                with cols[i]:
                    if label == "Clear":
                        if st.button(label, use_container_width=True, key=f"btn_{label}"):
                            st.session_state.expr_input = ""
                    else:
                        st.button(label, on_click=self._append_to_input, args=(val,), use_container_width=True, key=f"btn_{label}")

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
                
        # Subdued metrics at the bottom
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
            /* 1. Remove top padding and lock global scroll */
            .main .block-container {
                padding-top: 2rem !important; 
                padding-bottom: 0rem !important;
                max-height: 100vh;
            }
            html, body, [data-testid="stAppViewContainer"] {
                overflow: hidden !important;
            }
            
            /* 2. Create the vertical separator and handle independent scrolling */
            div[data-testid="column"]:nth-of-type(1) {
                border-right: 1px solid rgba(128, 128, 128, 0.3); 
                padding-right: 2rem;
                height: 90vh;
            }
            div[data-testid="column"]:nth-of-type(2) {
                padding-left: 2rem;
                height: 90vh; 
                overflow-y: auto; /* Independent scrollbar for results */
                padding-right: 1rem; 
            }
            
            /* 3. Refine typography spacing to close the gaps */
            h1 {
                margin-top: -20px !important;
                padding-bottom: 0px !important;
                margin-bottom: 0px !important;
            }
            div[data-testid="stCaptionContainer"] {
                margin-bottom: 1rem;
            }
            
            /* Hide Streamlit header/footer for cleaner app feel */
            header {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)
        # ---------------------------------
        
        col_left, col_right = st.columns([1, 1.3], gap="small")
        
        with col_left:
            st.markdown("<h1>∫ Indefinite Integration</h1>", unsafe_allow_html=True)
            st.caption("Enter a mathematical expression to compute its indefinite integral.")
            
            st.text_input("Integrand f(x)", key="expr_input", placeholder="e.g., 3*x**2 or sin(x)")
            
            with st.expander("⌨️ Virtual Math Keyboard", expanded=True):
                self.render_virtual_keyboard()
                
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
                
                # Credits pushed down using margin instead of <br> tags
                st.markdown(
                    """
                    <div style='text-align: center; color: rgba(128,128,128,0.5); margin-top: 40vh;'>
                        <h4 style='margin-bottom: 0;'>MADE BY UNDISPUTEDS</h4>
                        <p style='font-size: 0.9rem;'>Aaron Mayor &nbsp;|&nbsp; Henry Pula &nbsp;|&nbsp; Johnbert Malinis</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

if __name__ == "__main__":
    app = ApplicationUI()
    app.run()
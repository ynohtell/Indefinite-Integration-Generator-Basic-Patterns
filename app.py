import streamlit as st
from integration import IntegrationEngine, ComputationResult, generate_plot_cached

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
        if "selected_method" not in st.session_state:
            st.session_state.selected_method = "Auto"
        if "last_raw_input" not in st.session_state:
            st.session_state.last_raw_input = ""

    def _handle_keypress(self, label: str, val: str):
        if label == "C":
            st.session_state.expr_input = ""
        elif label == "⌫":
            st.session_state.expr_input = st.session_state.expr_input[:-1]
        else:
            st.session_state.expr_input += val

    def generate_html_report(self, res: ComputationResult) -> str:
        parts = res.verification.split("\n\n")
        math_check = parts[0]
        status_check = parts[1].replace("**", "") if len(parts) > 1 else ""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Integration Report</title>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 40px; color: #333; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1, h2, h3 {{ color: #2C3E50; }}
                .step-card {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin-bottom: 10px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>∫ Symbolic Integration Report (v1.0)</h2>
                <p><strong>Generated on:</strong> {res.summary.get('Timestamp', 'N/A')}</p>
                <hr>
                
                <h3>[1] Problem Overview</h3>
                <p><strong>Integrand:</strong> $$ {res.given} $$</p>
                <p><strong>Method Used:</strong> {res.method}</p>
                
                <h3>[2] Step-by-Step Solution</h3>
        """
        for i, step in enumerate(res.steps, 1):
            html += f'<div class="step-card"><strong>Step {i}:</strong> $$ {step} $$</div>'
            
        html += f"""
                <h3>[3] Final Answer</h3>
                <div style="font-size: 1.2em; padding: 20px; background: #e8f5e9; border-radius: 8px; border: 1px solid #c8e6c9;">
                    $$ F(x) = {res.final_answer} $$
                </div>
                
                <h3>[4] Verification & Auditing</h3>
                <p><strong>Status:</strong> {res.stopping_reason}</p>
                <p><strong>Derivative Back-Check:</strong> $$ {math_check} $$</p>
                <p><strong>Result:</strong> {status_check}</p>
                
                <hr>
                <p style="text-align:center; color: #7f8c8d; font-size: 0.9em;">
                    Created by Group UNDISPUTEDS | BSCS 4B | 2025-2026
                </p>
            </div>
        </body>
        </html>
        """
        return html

    @st.dialog("About the Developers")
    def show_about_modal(self):
        st.markdown("""
        ### Group UNDISPUTEDS
        **Course:** BSCS 4B  
        **School Year:** 2025-2026
        
        #### Members:
        * 👨‍💻 **Mayor, Mark Aaron A.**
        * 👨‍💻 **Malinis, Johnbert**
        * 👨‍💻 **Pula, Henry Luis P.**
        
        **Project:** Symbolic Indefinite Integration Generator (v1.0)
        """)
        st.info("This project dynamically resolves integrals using SymPy, generating step-by-step logic and graphical area mapping.")

    def render_virtual_keyboard(self):
        keys = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("⌫", "BACKSPACE"), ("C", "CLEAR")],
            # CHANGED: Used Unicode Asterisk Operator (∗) to bypass Markdown hiding the symbol, and changed ÷ to /
            [("4", "4"), ("5", "5"), ("6", "6"), ("∗", "*"), ("/", "/")], 
            [("1", "1"), ("2", "2"), ("3", "3"), ("＋", "+"), ("−", "-")],
            [("0", "0"), (".", "."), ("x", "x"), ("(", "("), (")", ")")],
            [("x²", "**2"), ("xⁿ", "**"), ("√", "sqrt("), ("sin", "sin("), ("cos", "cos(")]
        ]
        st.markdown("""<style>div[data-testid='stButton'] button {height: 2.5rem; min-height: 2.5rem;}</style>""", unsafe_allow_html=True)
        for r_idx, row in enumerate(keys):
            cols = st.columns(5)
            for c_idx, (label, val) in enumerate(row):
                with cols[c_idx]:
                    st.button(label, on_click=self._handle_keypress, args=(label, val), use_container_width=True, key=f"btn_{r_idx}_{c_idx}")

    def run(self):
        st.set_page_config(page_title="Symbolic Integrator v1.0", layout="wide", page_icon="∫")
        
        with st.sidebar:
            st.header("⚙️ Configuration")
            st.session_state.selected_method = st.selectbox(
                "Preferred Integration Method",
                options=["Auto", "Basic Standard Patterns", "U-Substitution", "Partial Fractions"],
                help="Select 'Auto' to let the engine decide, or force a specific method. Invalid forces will throw an error."
            )
            
            st.divider()
            st.header("📜 History")
            if not st.session_state.history:
                st.info("Your computations will appear here.")
            else:
                for idx, item in enumerate(reversed(st.session_state.history)):
                    if st.button(f"∫ {item['input']} dx", key=f"hist_{idx}", use_container_width=True):
                        st.session_state.expr_input = item['input']
                        st.session_state.last_result = item['result']
                        st.session_state.last_raw_input = item['input']
                        st.rerun()
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()

            st.divider()
            if st.button("ℹ️ About UNDISPUTEDS", use_container_width=True):
                self.show_about_modal()

        st.title("∫ Indefinite Integration Solver")
        st.caption("Enter a mathematical expression to compute its indefinite integral.")
        
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            raw = st.session_state.expr_input
            if raw:
                pretty = raw.replace("**", "^").replace("/", "÷")
                st.markdown(f"**Live Preview:** <span style='color:#4CAF50; font-family:monospace; font-size:1.2rem;'>{pretty}</span>", unsafe_allow_html=True)
            else:
                st.markdown("**Live Preview:** *Type an expression...*")
                
            st.text_input("Integrand f(x)", key="expr_input", placeholder="e.g., 3*x**2 or 1/(x**2 - 1)", label_visibility="collapsed")
            
            with st.expander("🖩 Quick Hand Calculator", expanded=True):
                self.render_virtual_keyboard()
                
            if st.button("Compute Integral", type="primary", use_container_width=True):
                if not st.session_state.expr_input.strip():
                    st.error("Please enter an integrand.")
                else:
                    with st.spinner("Integrating..."):
                        current_input = st.session_state.expr_input.strip()
                        st.session_state.last_raw_input = current_input
                        result = self.engine.compute(current_input, st.session_state.selected_method)
                        st.session_state.last_result = result
                        
                        if result.is_success:
                            st.session_state.history = [i for i in st.session_state.history if i["input"] != current_input]
                            st.session_state.history.append({"input": current_input, "result": result})

        with col_right:
            if st.session_state.last_result:
                res = st.session_state.last_result
                if res.is_success:
                    st.markdown("### ✨ Final Answer")
                    st.success(f"$$ \\int f(x)dx = {res.final_answer} $$")
                    
                    st.divider()
                    st.markdown("#### Problem Breakdown")
                    st.info(f"$$ {res.given} $$")
                    st.caption(f"**Method Used:** {res.method}")
                    st.caption(f"**Completion Rule:** {res.stopping_reason}")

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
                            
                    st.caption(f"⏱ {res.summary.get('Runtime', 'N/A')} | 🕒 {res.summary.get('Timestamp', 'N/A')}")
                    
                    report_html = self.generate_html_report(res)
                    filename = f"integration_report_{res.summary.get('Timestamp', 'report').replace(':', '').replace(' ', '_')}.html"
                    st.download_button(label="📄 Export Report (HTML - Best Format)", data=report_html, file_name=filename, mime="text/html", use_container_width=True)

                else:
                    st.error(f"Computation Failed")
                    st.warning(res.error_message)
                    st.info(f"System Note: {res.stopping_reason}")
            elif not st.session_state.expr_input.strip():
                st.info("👈 Enter an expression on the left and click **Compute Integral** to see the solution here.")

            current_input = st.session_state.expr_input.strip()
            
            is_failed_state = (st.session_state.last_result 
                               and not st.session_state.last_result.is_success 
                               and st.session_state.last_raw_input == current_input)

            if current_input and not is_failed_state:
                st.divider()
                fig = generate_plot_cached(current_input)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    app = ApplicationUI()
    app.run()
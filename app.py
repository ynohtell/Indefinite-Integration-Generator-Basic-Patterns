import streamlit as st
import sympy as sp
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from integration import IntegrationEngine, ComputationResult, generate_plot_cached

# ==========================================
# WEEK 7, 11, 13: UI & FORMATTING 
# ==========================================
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

    def _handle_keypress(self, label: str, val: str):
        if label == "C":
            st.session_state.expr_input = ""
        elif label == "⌫":
            st.session_state.expr_input = st.session_state.expr_input[:-1]
        else:
            st.session_state.expr_input += val

    # Week 10: Export Feature
    def generate_text_report(self, res: ComputationResult) -> str:
        report = f"========================================\n"
        report += f" SYMBOLIC INTEGRATION REPORT v1.0\n"
        report += f" Generated on: {res.summary.get('Timestamp', 'N/A')}\n"
        report += f"========================================\n\n"
        
        report += f"[1] GIVEN PROBLEM\n-----------------\n"
        report += f"Integrand: {res.given}\n"
        report += f"Method Used: {res.method}\n\n"
        
        report += f"[2] STEP-BY-STEP SOLUTION\n-------------------------\n"
        for i, step in enumerate(res.steps, 1):
            clean_step = step.replace(r"\text{", "").replace("}", "").replace(r"\frac", "frac")
            report += f"Step {i}: {clean_step}\n"
            
        report += f"\n[3] FINAL ANSWER\n----------------\n"
        report += f"F(x) = {res.final_answer.replace(r'\\', '')}\n\n"
        
        report += f"[4] VERIFICATION & STOPPING RULE\n--------------------------------\n"
        report += f"Status: {res.stopping_reason}\n"
        clean_ver = res.verification.replace(r"\text{", "").replace("}", "")
        report += f"Check: {clean_ver}\n\n"
        
        report += f"========================================\n"
        report += f" End of Report | Undisputeds BSCS 4B\n"
        report += f"========================================\n"
        return report

    def render_virtual_keyboard(self):
        keys = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("⌫", "BACKSPACE"), ("C", "CLEAR")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("÷", "/")],
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
        
        # WEEK 7 & 13: Sidebar & Help/About Documentation
        with st.sidebar:
            st.header("⚙️ Configuration")
            # Week 6: UI Method Selection
            st.session_state.selected_method = st.selectbox(
                "Preferred Integration Method",
                options=["Auto", "Basic Standard Patterns", "U-Substitution", "Partial Fractions"],
                help="Select 'Auto' to let the engine decide, or force a specific method."
            )
            
            st.divider()
            st.header("📜 History")
            if not st.session_state.history:
                st.info("Your successful computations will appear here.")
            else:
                for idx, item in enumerate(reversed(st.session_state.history)):
                    if st.button(f"∫ {item['input']} dx", key=f"hist_{idx}", use_container_width=True):
                        st.session_state.expr_input = item['input']
                        st.session_state.last_result = item['result']
                        st.rerun()
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()

            st.divider()
            st.markdown("""
            **Symbolic: Indefinite Integration Generator (v1.0)**
            *School Year 2025-2026*
            
            **Group UNDISPUTEDS (BSCS 4B)**
            * Mayor, Mark Aaron A.
            * Malinis, Johnbert
            * Pula, Henry Luis P.
            """)

        # Main Layout
        st.title("∫ Indefinite Integration Solver")
        st.caption("Enter a mathematical expression to compute its indefinite integral.")
        
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            raw = st.session_state.expr_input
            if raw:
                pretty = raw.replace("**", "^").replace("*", "·").replace("/", "÷")
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
                        result = self.engine.compute(current_input, st.session_state.selected_method)
                        st.session_state.last_result = result
                        
                        if result.is_success:
                            st.session_state.history = [i for i in st.session_state.history if i["input"] != current_input]
                            st.session_state.history.append({"input": current_input, "result": result})

        # Output / Trail Area
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
                    
                    # Week 5: Stopping rule info
                    st.caption(f"**Completion Rule:** {res.stopping_reason}")

                    with st.expander("View Step-by-Step Breakdown", expanded=False):
                        for i, step in enumerate(res.steps, 1):
                            st.markdown(f"**Step {i}:**")
                            st.latex(step)
                            
                    # Week 9: Prominent Verification
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
                    
                    # Week 10: Export Feature Button
                    report_txt = self.generate_text_report(res)
                    st.download_button(label="📄 Export Report (TXT)", data=report_txt, file_name="integration_report.txt", mime="text/plain", use_container_width=True)

                    # Graph rendering
                    fig = generate_plot_cached(st.session_state.expr_input)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    # Week 8 Edge case UI rendering
                    st.error(f"Computation Failed")
                    st.warning(res.error_message)
                    st.info(f"System Note: {res.stopping_reason}")
            else:
                st.info("👈 Enter an expression on the left and click **Compute Integral** to see the solution here.")

if __name__ == "__main__":
    app = ApplicationUI()
    app.run()
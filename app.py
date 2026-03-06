import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
from integration import IntegrationEngine, ComputationResult

# --- CACHED GRAPHING FUNCTION ---
@st.cache_data(show_spinner=False)
def generate_plot_cached(expr_str: str):
    x = sp.Symbol('x')
    try:
        expr = sp.sympify(expr_str)
        antideriv = sp.integrate(expr, x)

        f_lambdified = sp.lambdify(x, expr, modules=['numpy'])
        F_lambdified = sp.lambdify(x, antideriv, modules=['numpy'])

        x_vals = np.linspace(-10, 10, 500)
        
        y_f = f_lambdified(x_vals)
        y_F = F_lambdified(x_vals)

        # Mask out massive values for asymptotes
        threshold = 50
        y_f = np.where(np.abs(y_f) > threshold, np.nan, y_f)
        y_F = np.where(np.abs(y_F) > threshold, np.nan, y_F)

        # Build the interactive Plotly figure
        fig = go.Figure()
        
        # Integrand (f(x)) with shaded area to visualize "Integration"
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_f, 
            mode='lines', 
            name='f(x) [Integrand]', 
            line=dict(color='#FF4B4B', width=2),
            fill='tozeroy', 
            fillcolor='rgba(255, 75, 75, 0.15)'
        ))
        
        # Antiderivative (F(x))
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_F, 
            mode='lines', 
            name='F(x) [Antiderivative]', 
            line=dict(color='#0068C9', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title="Function vs. Area (Antiderivative)",
            xaxis_title="x",
            yaxis_title="y",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=50, b=20),
            height=400,
            xaxis=dict(zeroline=True, zerolinewidth=1.5, zerolinecolor='gray'),
            yaxis=dict(zeroline=True, zerolinewidth=1.5, zerolinecolor='gray'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
    except Exception:
        return None

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
            pretty = raw.replace("**", "^").replace("*", "·").replace("/", "÷")
            st.markdown(
                f"**Live Preview:** &nbsp; <span style='color: #4CAF50; font-family: monospace; font-size: 1.2rem;'>{pretty}</span>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown("**Live Preview:** &nbsp; *Type an expression...*")

    def render_virtual_keyboard(self):
        keys = [
            [("7", "7"), ("8", "8"), ("9", "9"), ("⌫", "BACKSPACE"), ("C", "CLEAR")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("÷", "/")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("＋", "+"), ("−", "-")],
            [("0", "0"), (".", "."), ("x", "x"), ("(", "("), (")", ")")],
            [("x²", "**2"), ("xⁿ", "**"), ("√", "sqrt("), ("sin", "sin("), ("cos", "cos(")]
        ]
        
        # Keep only the minimal CSS needed for the keyboard buttons
        st.markdown("""
        <style>
            div[data-testid='stButton'] button {
                height: 2.5rem;
                min-height: 2.5rem;
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

        tutorials = {
            "Integration by Substitution": "https://www.youtube.com/results?search_query=integration+by+u+substitution",
            "Basic Standard Patterns": "https://www.youtube.com/results?search_query=basic+integration+rules"
        }
        if res.method in tutorials:
            st.markdown(f"📺 **Need help?** [Watch a tutorial on {res.method}]({tutorials[res.method]})")
        
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
        
        st.caption(f"⏱ {runtime} | 🔄 {iterations} iter | 🕒 {time_computed}")

    def run(self):
        st.set_page_config(page_title="Symbolic Integrator", layout="wide", page_icon="∫")
        
        # Sidebar History
        with st.sidebar:
            st.header("📜 History")
            if not st.session_state.history:
                st.info("Your successful computations will appear here.")
            else:
                for idx, item in enumerate(reversed(st.session_state.history)):
                    if st.button(f"∫ {item['input']} dx", key=f"hist_{idx}", use_container_width=True):
                        st.session_state.expr_input = item['input']
                        st.session_state.last_result = item['result']
                        st.rerun()
                
                st.divider()
                if st.button("🗑️ Clear History", use_container_width=True):
                    st.session_state.history = []
                    st.rerun()

            st.markdown("<br><br><div style='text-align: center; color: gray; font-size: 0.8rem;'>"
                        "MADE BY UNDISPUTEDS<br>Aaron Mayor | Henry Pula | Johnbert Malinis</div>", 
                        unsafe_allow_html=True)

        # Main Layout
        st.title("∫ Indefinite Integration")
        st.caption("Enter a mathematical expression to compute its indefinite integral.")
        
        col_left, col_right = st.columns([1, 1], gap="large")
        
        with col_left:
            self.render_live_preview()
            st.text_input("Integrand f(x)", key="expr_input", placeholder="e.g., 3*x**2 or sin(x)", label_visibility="collapsed")
            
            with st.expander("🖩 Quick Hand Calculator", expanded=True):
                self.render_virtual_keyboard()
                
            if st.button("Compute Integral", type="primary", use_container_width=True):
                if not st.session_state.expr_input.strip():
                    st.error("Please enter an integrand.")
                else:
                    with st.spinner("Integrating..."):
                        current_input = st.session_state.expr_input.strip()
                        result = self.engine.compute(current_input)
                        st.session_state.last_result = result
                        
                        if result.is_success:
                            st.session_state.history = [
                                item for item in st.session_state.history 
                                if item["input"] != current_input
                            ]
                            st.session_state.history.append({
                                "input": current_input,
                                "result": result
                            })

        with col_right:
            if st.session_state.last_result:
                if st.session_state.last_result.is_success:
                    self.render_trail(st.session_state.last_result)
                    
                    input_to_plot = st.session_state.history[-1]["input"] if st.session_state.history else st.session_state.expr_input
                    fig = generate_plot_cached(input_to_plot)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"Computation Failed: {st.session_state.last_result.error_message}")
            else:
                st.info("👈 Enter an expression on the left and click **Compute Integral** to see the solution here.")

if __name__ == "__main__":
    app = ApplicationUI()
    app.run()
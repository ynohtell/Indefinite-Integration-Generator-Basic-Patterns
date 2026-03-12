from typing import Dict, Any, Optional, Tuple, List
import sympy as sp
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
import time

# ==========================================
# WEEK 5: CORE DATA STRUCTURES & STOPPING
# ==========================================
class ComputationResult:
    def __init__(self):
        self.given: str = ""
        self.method: str = ""
        self.steps: List[str] = []
        self.final_answer: str = ""
        self.verification: str = ""
        self.summary: Dict[str, Any] = {}
        self.is_success: bool = False
        self.error_message: str = ""
        self.stopping_reason: str = "" # Week 5 Requirement

# ==========================================
# WEEK 6 & 8: ENGINE, FEATURES & EDGE CASES
# ==========================================
class IntegrationEngine:
    def __init__(self):
        self.x = sp.Symbol('x')
        self.u = sp.Symbol('u')
        
    def _detect_u_substitution(self, expr) -> Optional[Tuple[sp.Expr, sp.Expr, sp.Expr]]:
        """Scans the expression tree for a valid basic U-Substitution pattern."""
        if not expr.is_Mul:
            return None
            
        u_candidates = []
        for arg in expr.args:
            if arg.is_Pow:
                if arg.base.has(self.x) and arg.base != self.x: 
                    u_candidates.append(arg.base)
                if arg.exp.has(self.x) and arg.exp != self.x: 
                    u_candidates.append(arg.exp)
            elif isinstance(arg, (sp.sin, sp.cos, sp.tan, sp.exp, sp.log)):
                inner_arg = arg.args[0]
                if inner_arg.has(self.x) and inner_arg != self.x: 
                    u_candidates.append(inner_arg)
                    
        for u_expr in u_candidates:
            du_expr = sp.diff(u_expr, self.x)
            if du_expr == 0: 
                continue
            
            integrand_with_dx_divided = sp.simplify(expr / du_expr)
            u_integrand = sp.simplify(integrand_with_dx_divided.subs(u_expr, self.u))
            
            if not u_integrand.has(self.x):
                return u_expr, du_expr, u_integrand
                
        return None

    def _detect_partial_fractions(self, expr) -> Optional[sp.Expr]:
        """Week 6: Detects if Partial Fractions decomposition is applicable."""
        # Check if it's a rational function that can be decomposed
        if expr.is_Mul or expr.is_Add or expr.is_Pow:
            decomposed = sp.apart(expr, self.x)
            if decomposed != expr and not decomposed.has(sp.Integral):
                return decomposed
        return None

    def compute(self, integrand_str: str, method_preference: str = "Auto") -> ComputationResult:
        result = ComputationResult()
        start_time = time.perf_counter()
        
        try:
            # Week 8: Edge Case - Syntax Checking
            if not integrand_str or integrand_str.isspace():
                raise ValueError("Integrand cannot be empty.")
            
            try:
                expr = sp.sympify(integrand_str)
            except sp.SympifyError:
                raise ValueError("Invalid mathematical syntax. Please check your parentheses and operators.")

            # Week 8: Edge Case - Division by Zero or invalid types
            if expr.has(sp.zoo, sp.oo, sp.nan):
                raise ValueError("Expression evaluates to infinity or undefined values.")

            result.given = rf"\int \left( {sp.latex(expr)} \right) \, dx"
            result.steps.append(rf"\text{{Identify the integrand: }} f(x) = {sp.latex(expr)}")
            
            u_sub_data = self._detect_u_substitution(expr)
            partial_frac_data = self._detect_partial_fractions(expr)
            
            # --- Week 6: Method Selection Logic ---
            antiderivative = None

            if method_preference in ["Auto", "U-Substitution"] and u_sub_data:
                u_expr, du_expr, u_integrand = u_sub_data
                result.method = "Integration by Substitution"
                result.steps.append(rf"\text{{Let }} u = {sp.latex(u_expr)}")
                result.steps.append(rf"\text{{Differentiate }} u \text{{: }} \frac{{du}}{{dx}} = {sp.latex(du_expr)}")
                result.steps.append(rf"\text{{Isolate }} dx \text{{: }} dx = \frac{{du}}{{{sp.latex(du_expr)}}}")
                result.steps.append(rf"\text{{Substitute into original integral:}}")
                result.steps.append(rf"\int \left( {sp.latex(u_integrand)} \right) \, du")
                
                antiderivative_u = sp.integrate(u_integrand, self.u)
                result.steps.append(rf"\text{{Evaluate integral: }} {sp.latex(antiderivative_u)}")
                
                antiderivative = antiderivative_u.subs(self.u, u_expr)
                result.steps.append(rf"\text{{Substitute }} u \text{{ back: }} {sp.latex(antiderivative)}")
                result.steps.append(rf"\text{{Add the constant of integration, }} C.")
            
            elif method_preference in ["Auto", "Partial Fractions"] and partial_frac_data:
                result.method = "Partial Fractions Decomposition"
                result.steps.append(rf"\text{{Decompose into partial fractions:}}")
                result.steps.append(rf"= \int \left( {sp.latex(partial_frac_data)} \right) \, dx")
                
                antiderivative = sp.integrate(partial_frac_data, self.x)
                result.steps.append(rf"\text{{Integrate each term: }} {sp.latex(antiderivative)}")
                result.steps.append(rf"\text{{Add the constant of integration, }} C.")

            else:
                result.method = "Basic Standard Patterns"
                antiderivative = sp.integrate(expr, self.x)
                
                # Week 5 & 8: Edge Case - Non-integrable functions
                if isinstance(antiderivative, sp.Integral):
                    raise ValueError("Requires advanced techniques beyond Basic Patterns, or has no closed-form solution.")
                    
                result.steps.append(rf"\text{{Evaluate using basic rules: }} {sp.latex(antiderivative)}")
                result.steps.append(rf"\text{{Add the constant of integration, }} C.")
            
            result.final_answer = rf"{sp.latex(antiderivative)} + C"
            
            # Week 9: Verification Phase
            derivative = sp.diff(antiderivative, self.x)
            residual = sp.simplify(expr - derivative)
            
            verification_text = rf"\text{{Back-check by differentiating: }} \frac{{d}}{{dx}}\left[{sp.latex(antiderivative)}\right] = {sp.latex(derivative)}"
            
            if residual == 0:
                result.verification = verification_text + "\n\n**Verification Successful:** Derivative matches the integrand."
            else:
                result.verification = verification_text + "\n\n**Verification Warning:** Symbolic equivalence to 0 not trivially established."
                
            # Week 5: Stopping Output
            result.stopping_reason = "Exact closed-form antiderivative reached successfully."
                
            result.summary = {
                "Runtime": f"{(time.perf_counter() - start_time) * 1000:.2f} ms",
                "Iterations": "1",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            result.is_success = True
            
        except Exception as e:
            result.is_success = False
            result.error_message = f"Error: {str(e)}"
            result.stopping_reason = "Process halted due to error or lack of closed-form solution."
            
        return result

# ==========================================
# GRAPHING ENGINE (CACHED)
# ==========================================
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

        threshold = 50
        y_f = np.where(np.abs(y_f) > threshold, np.nan, y_f)
        y_F = np.where(np.abs(y_F) > threshold, np.nan, y_F)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_f, mode='lines', name='f(x) [Integrand]', 
                                 line=dict(color='#FF4B4B', width=2), fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.15)'))
        fig.add_trace(go.Scatter(x=x_vals, y=y_F, mode='lines', name='F(x) [Antiderivative]', 
                                 line=dict(color='#0068C9', width=3, dash='dash')))
        
        fig.update_layout(title="Function vs. Area (Antiderivative)", xaxis_title="x", yaxis_title="y",
                          hovermode="x unified", margin=dict(l=20, r=20, t=50, b=20), height=400,
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        return fig
    except Exception:
        return None

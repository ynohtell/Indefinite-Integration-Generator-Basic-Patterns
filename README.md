# Symbolic: Indefinite Integration Generator (Basic Patterns) v1.0
**Institution:** Cavite State University - Imus Campus  
**Course:** BSCS 4B | **School Year:** 2025-2026  
**Group Name:** UNDISPUTEDS  
**Members:** - Mayor, Mark Aaron A.
- Malinis, Johnbert 
- Pula, Henry Luis P.

## Overview
A powerful, interactive Streamlit application built with Python and SymPy to perform indefinite symbolic integration. It provides step-by-step mathematical reasoning, auto-detects integration methods (U-Substitution, Partial Fractions, Basic Patterns), generates dynamic runtime graphs, and performs derivative-based verification auditing.

## Features
* **Intelligent Method Detection:** Automatically routes problems to Basic Patterns, U-Substitution, or Partial Fractions logic.
* **Step-by-Step Trail:** Outputs a beautiful, LaTeX-rendered breakdown of the mathematical process.
* **Derivative Verification:** Automatically differentiates the final answer to back-check against the original integrand, ensuring mathematical integrity.
* **Real-time Graphing:** Instantly plots the integrand $f(x)$ vs. the antiderivative $F(x)$ area.
* **Robust Edge-Case Handling:** Safely catches syntax errors, division by zero, and halts safely on non-elementary integrals (e.g., $e^{x^2}$).
* **Audit Export:** Single-click export of the entire mathematical trail to a beautifully formatted HTML report.

## Setup & Running Instructions
1. Ensure you have `uv` installed.
2. Clone this repository and navigate to the project folder.
3. Install dependencies:
   ```bash
   uv pip install streamlit sympy numpy plotly 
   # OR
   uv sync
4. Run the application:
    ```bash
    uv run streamlit run app.py
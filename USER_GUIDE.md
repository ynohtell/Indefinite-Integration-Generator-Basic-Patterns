# Symbolic Integrator v1.0 - User Guide

#### 1. Interface Overview
The application is divided into three main sections:
* **The Sidebar (Left):** Contains your configuration settings, a history of your successful computations, and information about the developers.
* **The Input Panel (Center):** Where you enter your mathematical expression. It features a "Live Preview" that translates your code syntax into readable math, and a Quick Hand Virtual Keyboard for easy symbol entry.
* **The Output Trail (Right):** Displays the Final Answer, the Step-by-Step Breakdown, the Verification check, and the Interactive Graph.

#### 2. Entering an Expression
1. Click the text box under **Integrand f(x)**.
2. You can type using your physical keyboard (e.g., `3*x**2`) or use the **Quick Hand Calculator** buttons.
3. *Note on Virtual Keyboard:* Clicking virtual buttons will add the character to the *end* of your equation. If you need to fix a typo in the middle of your equation, please click into the text box and use your physical keyboard.
4. Watch the **Live Preview** to ensure your syntax is recognized properly.
5. Click **Compute Integral**.

#### 3. Selecting a Method
By default, the engine is set to **Auto**. It will scan your equation and pick the best method.
* If you want to force the engine to use a specific rule, open the **Sidebar** and change the "Preferred Integration Method" dropdown to *U-Substitution* or *Partial Fractions*.
* If you force a method that does not mathematically work for your equation, the system will safely halt and warn you: "Forced Method Failed."

#### 4. Reviewing and Exporting Results
* **Step-by-Step:** Click the `> View Step-by-Step Breakdown` expander to see the logic the engine used.
* **Verification:** Click the `> View Verification` expander to see the system take the derivative of its own answer to prove it matches your input.
* **Graph:** Scroll to the bottom to interact with the visual area plot. You can hover, zoom, and pan.
* **Export:** Click the **📄 Export Report (HTML)** button to download a permanent, beautifully formatted MathJax report of your problem.

---
import pytest
from integration import IntegrationEngine

@pytest.fixture
def engine():
    """Fixture to provide a fresh IntegrationEngine for each test."""
    return IntegrationEngine()

# ==========================================
# WEEK 4: BASIC PATTERNS & TRAIL TESTS
# ==========================================

def test_w4_01_basic_polynomial(engine):
    """Test ID W4-01: Basic polynomial integration."""
    result = engine.compute("3*x**2")
    
    assert result.is_success is True
    # SymPy latex formats x^3 as x^{3}
    assert "x^{3}" in result.final_answer 
    assert "+ C" in result.final_answer
    assert result.method == "Basic Standard Patterns"

def test_w4_02_basic_trigonometric(engine):
    """Test ID W4-02: Basic trigonometric integration."""
    result = engine.compute("sin(x)")
    
    assert result.is_success is True
    assert "\\cos{\\left(x \\right)}" in result.final_answer # SymPy's latex output for cos(x)
    assert "-" in result.final_answer # It should be negative
    assert result.method == "Basic Standard Patterns"

def test_w4_03_basic_exponential(engine):
    """Test ID W4-03: Basic exponential integration."""
    result = engine.compute("exp(x)")
    
    assert result.is_success is True
    assert "e^{x}" in result.final_answer
    assert result.method == "Basic Standard Patterns"

def test_w4_computation_steps_exist(engine):
    """Verify that the engine generates a step-by-step trail, not just an answer."""
    result = engine.compute("3*x**2")
    
    assert result.is_success is True
    assert len(result.steps) > 0, "Steps trail should not be empty."
    
    # Check that it includes the initial identification step
    assert any("Identify the integrand" in step for step in result.steps)
    # Check that it explicitly mentions adding the constant C
    assert any("Add the constant of integration" in step for step in result.steps)


# ==========================================
# WEEK 5: COMPLETION / STOPPING RULES TESTS
# ==========================================

def test_w5_01_stopping_rule_exact_form(engine):
    """Test ID W5-01: Process completes normally upon finding an exact closed form."""
    print("\n--- TEST W5-01: Stopping Rule (Exact Form) ---")
    result = engine.compute("x**2")
    
    print(f"Stopping Reason: {result.stopping_reason}")
    assert result.is_success is True
    assert "Exact closed-form antiderivative reached successfully" in result.stopping_reason

def test_w5_02_stopping_rule_no_closed_form(engine):
    """Test ID W5-02: Process halts when no elementary closed form exists."""
    print("\n--- TEST W5-02: Stopping Rule (No Closed Form) ---")
    result = engine.compute("exp(x**2)")
    
    print(f"Error Message: {result.error_message}")
    print(f"Stopping Reason: {result.stopping_reason}")
    assert result.is_success is False
    assert "Process halted due to error or lack of closed-form solution" in result.stopping_reason

def test_w5_03_stopping_rule_syntax_error(engine):
    """Test ID W5-03: Process halts immediately on invalid syntax."""
    print("\n--- TEST W5-03: Stopping Rule (Syntax Error) ---")
    result = engine.compute("3x+")
    
    print(f"Error Message: {result.error_message}")
    print(f"Stopping Reason: {result.stopping_reason}")
    assert result.is_success is False
    assert "Invalid mathematical syntax" in result.error_message
    assert "Process halted due to error" in result.stopping_reason


# ==========================================
# WEEK 6: FEATURE EXPANSION & METHOD UI TESTS
# ==========================================

def test_w6_01_partial_fractions_auto(engine):
    """Test ID W6-01: Auto-detects and applies Partial Fractions."""
    print("\n--- TEST W6-01: Partial Fractions (Auto) ---")
    result = engine.compute("1/(x**2 - 1)", method_preference="Auto")
    
    assert result.is_success is True
    assert result.method == "Partial Fractions Decomposition"
    assert "Decompose into partial fractions" in str(result.steps)

def test_w6_02_force_usub_success(engine):
    """Test ID W6-02: User explicitly forces U-Substitution."""
    print("\n--- TEST W6-02: Force U-Substitution ---")
    result = engine.compute("2*x*cos(x**2)", method_preference="U-Substitution")
    
    assert result.is_success is True
    assert result.method == "Integration by Substitution"

def test_w6_03_force_partial_fractions_success(engine):
    """Test ID W6-03: User explicitly forces Partial Fractions."""
    print("\n--- TEST W6-03: Force Partial Fractions ---")
    result = engine.compute("1/(x**2 + 3*x + 2)", method_preference="Partial Fractions")
    
    assert result.is_success is True
    assert result.method == "Partial Fractions Decomposition"

def test_w6_04_force_method_mismatch_fails(engine):
    """Test ID W6-04: User forces Partial Fractions on an incompatible equation (sin(x))."""
    print("\n--- TEST W6-04: Forced Method Mismatch ---")
    result = engine.compute("sin(x)", method_preference="Partial Fractions")
    
    assert result.is_success is False
    assert "Forced Method Failed" in result.error_message

def test_w6_05_trail_identifies_method(engine):
    """Test ID W6-05: Verifies the trail correctly logs the method used."""
    print("\n--- TEST W6-05: Trail Method Identification ---")
    result = engine.compute("3*x**2", method_preference="Basic Standard Patterns")
    
    assert result.is_success is True
    assert result.method == "Basic Standard Patterns"


# ==========================================
# WEEK 8: ROBUSTNESS & EDGE CASE TESTS
# ==========================================

def test_w8_01_edge_case_no_closed_form(engine):
    """Test ID E-01: Engine catches and halts on non-elementary integrals."""
    print("\n--- TEST W8-01: Edge Case (No Closed Form) ---")
    result = engine.compute("exp(x**2)")
    
    assert result.is_success is False
    assert "Requires advanced techniques" in result.error_message
    assert "Process halted" in result.stopping_reason

def test_w8_02_edge_case_syntax_error(engine):
    """Test ID E-02: Engine catches bad syntax safely without crashing."""
    print("\n--- TEST W8-02: Edge Case (Syntax Error) ---")
    result = engine.compute("sin(x")
    
    assert result.is_success is False
    assert "Invalid mathematical syntax" in result.error_message

def test_w8_03_edge_case_method_mismatch(engine):
    """Test ID E-03: Engine catches when a user forces the wrong method."""
    print("\n--- TEST W8-03: Edge Case (Method Mismatch) ---")
    result = engine.compute("exp(x)", method_preference="Partial Fractions")
    
    assert result.is_success is False
    assert "Forced Method Failed" in result.error_message

def test_w8_04_edge_case_division_by_zero(engine):
    """Test ID E-04: Engine catches undefined math."""
    print("\n--- TEST W8-04: Edge Case (Division by Zero) ---")
    result = engine.compute("1/0")
    
    assert result.is_success is False
    assert "evaluates to infinity or undefined values" in result.error_message


# ==========================================
# WEEK 9: VERIFICATION & AUDIT TESTS
# ==========================================

def test_w9_01_verification_success_polynomial(engine):
    """Test ID W9-01: Verifies the derivative back-check works for polynomials."""
    print("\n--- TEST W9-01: Verification Check (Polynomial) ---")
    result = engine.compute("3*x**2")
    
    assert result.is_success is True
    assert "Verification Successful" in result.verification
    assert "3 x^{2}" in result.verification # Checks if the derivative matches

def test_w9_02_verification_success_usub(engine):
    """Test ID W9-04: Verifies the derivative back-check works for U-Substitution."""
    print("\n--- TEST W9-04: Verification Check (U-Sub) ---")
    result = engine.compute("2*x*cos(x**2)")
    
    assert result.is_success is True
    assert "Verification Successful" in result.verification
    assert "2 x \\cos{\\left(x^{2} \\right)}" in result.verification

# ==========================================
# WEEK 10: EXPORT CAPABILITY TESTS
# ==========================================

def test_w10_01_export_data_contains_all_fields(engine):
    """Test ID W10-01/02: Ensures the result object holds all data needed for the HTML export."""
    print("\n--- TEST W10-01: Export Data Completeness ---")
    result = engine.compute("3*x**2")
    
    # To generate the report, the UI relies on these properties existing and being populated
    assert result.given != ""
    assert result.method != ""
    assert len(result.steps) > 0
    assert result.final_answer != ""
    assert result.verification != ""
    assert "Timestamp" in result.summary
    assert "Runtime" in result.summary
    print("All required export fields are populated and ready for HTML generation.")
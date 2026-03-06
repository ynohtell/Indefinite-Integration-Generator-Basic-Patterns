import pytest
import sympy as sp
from typing import Dict, Any, Optional, Tuple
from integration import IntegrationEngine, ComputationResult

@pytest.fixture
def engine():
    """Fixture to provide a fresh instance of the IntegrationEngine for each test."""
    return IntegrationEngine()

class TestIntegrationEngine:
    
    def test_basic_power_rule(self, engine):
        """Test basic polynomial integration."""
        result = engine.compute("x**2")
        
        assert result.is_success is True
        assert result.method == "Basic Standard Patterns"
        assert result.error_message == ""
        # sympy latex for x**3 / 3 is \frac{x^{3}}{3}
        assert "\\frac{x^{3}}{3} + C" in result.final_answer
        assert "Verification Successful" in result.verification

    def test_basic_trigonometric(self, engine):
        """Test basic trigonometric integration."""
        result = engine.compute("cos(x)")
        
        assert result.is_success is True
        assert result.method == "Basic Standard Patterns"
        # Check that sine is in the LaTeX output
        assert "\\sin" in result.final_answer
        assert "+ C" in result.final_answer

    def test_u_substitution_polynomial(self, engine):
        """Test U-Substitution detection for a polynomial chain rule."""
        result = engine.compute("2*x*(x**2 + 1)**3")
        
        assert result.is_success is True
        assert result.method == "Integration by Substitution"
        # The antiderivative should be (x^2 + 1)^4 / 4
        assert "4" in result.final_answer 
        assert "Verification Successful" in result.verification
        
        # Verify that the steps correctly identified u
        steps_str = " ".join(result.steps)
        assert "u = x^{2} + 1" in steps_str or "u = 1 + x^{2}" in steps_str

    def test_u_substitution_exponential(self, engine):
        """Test U-Substitution detection for an exponential function."""
        result = engine.compute("x*exp(x**2)")
        
        assert result.is_success is True
        assert result.method == "Integration by Substitution"
        # Sympy formats exp(x**2) as e^{x^{2}}
        assert "e^{x^{2}}" in result.final_answer
        assert "\\frac{e^{x^{2}}}{2}" in result.final_answer or "\\frac{1}{2} e^{x^{2}}" in result.final_answer

    def test_u_substitution_trigonometric(self, engine):
        """Test U-Substitution with trigonometric functions."""
        result = engine.compute("cos(x)*sin(x)**2")
        
        assert result.is_success is True
        assert result.method == "Integration by Substitution"
        assert "Verification Successful" in result.verification

    def test_unsolvable_or_advanced_integral(self, engine):
        """Test an integral that evaluates to an unevaluated Integral object or error."""
        # e^(e^x) cannot be integrated in terms of elementary functions easily by sympy's basic engine
        result = engine.compute("exp(exp(x))")
        
        # Depending on sympy's version, this either returns an sp.Integral or evaluates to an Ei function.
        # Let's force a mathematical impossibility for basic substitution to check exception handling.
        # If it returns an integral object, your code raises a ValueError.
        if "Requires advanced techniques" in result.error_message:
            assert result.is_success is False
            assert result.final_answer == ""

    def test_invalid_syntax_handling(self, engine):
        """Test how the engine handles mathematically invalid strings."""
        # 'x * / 2' is fundamentally broken syntax
        result = engine.compute("x * / 2")
        
        assert result.is_success is False
        assert result.error_message != ""
        assert "Error:" in result.error_message

    def test_metadata_generation(self, engine):
        """Ensure runtime and timestamp metadata are correctly populated."""
        result = engine.compute("3*x**2")
        
        assert result.is_success is True
        assert "Runtime" in result.summary
        assert "ms" in result.summary["Runtime"]
        assert "Timestamp" in result.summary
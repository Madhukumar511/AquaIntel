"""Unit and precision tests for AquaIntel spectral decomposition accuracy."""

import pytest
import numpy as np
from benchmark_model import ModelBenchmarkSuite

@pytest.fixture
def benchmark_suite():
    return ModelBenchmarkSuite()

def test_pure_endmember_isolation(benchmark_suite):
    """Test 1: Pure endmembers must isolate correct constituent with > 65% confidence."""
    report = benchmark_suite.test_pure_endmember_isolation()
    assert bool(report["passed"])
    assert report["score"] == 100.0

def test_binary_dilution_linearity(benchmark_suite):
    """Test 2: Binary mixtures must scale linearly with R² >= 0.95."""
    report = benchmark_suite.test_binary_linearity()
    assert bool(report["passed"])
    assert report["score"] >= 95.0

def test_conservation_of_mass(benchmark_suite):
    """Test 3: Abundance percentages must strictly sum to 100.0%."""
    report = benchmark_suite.test_conservation_of_mass()
    assert bool(report["passed"])
    assert report["max_deviation_pct"] <= 0.01

def test_dirichlet_mixture_precision(benchmark_suite):
    """Test 4: Random realistic multi-spectral ocean mixtures must achieve > 90% precision."""
    report = benchmark_suite.test_dirichlet_accuracy_benchmark(num_samples=300)
    assert bool(report["passed"])
    assert report["score"] >= 90.0

def test_overall_precision_grade(benchmark_suite):
    """Test 5: Full battery of tests must achieve >= 95% overall precision grade."""
    report = benchmark_suite.run_all_benchmarks()
    assert bool(report["passed"])
    assert report["overall_score"] >= 95.0

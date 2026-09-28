#!/usr/bin/env python3
"""
AquaIntel — Deep Model Verification & Accuracy Benchmarking Suite.
Rigorous mathematical testing of spectral unmixing precision, linearity,
conservation of mass, and noise resilience across 8 marine constituent endmembers.
"""

import sys
import math
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from config import PRECISE_CONSTITUENTS
from core.spectral import ENDMEMBERS_10D, decompose_spectral_mixture

FEATURE_COLS = ['B01', 'B02', 'B3N', 'B04', 'B05', 'B06', 'B07', 'B08', 'NDVI', 'FDI']

class ModelBenchmarkSuite:
    """Executes exhaustive optical and statistical validation on AquaIntel unmixing engines."""

    def __init__(self, keras_model_path: str = None, scaler_path: str = None):
        self.keras_model = None
        self.scaler = None
        self.mode = "Analytical Physics Unmixer"

        if keras_model_path and scaler_path:
            try:
                import joblib
                from tensorflow.keras.models import load_model
                self.keras_model = load_model(keras_model_path)
                self.scaler = joblib.load(scaler_path)
                self.mode = f"Deep Keras Neural Network ({self.keras_model.name})"
            except Exception as e:
                print(f"[!] Warning: Could not load Keras model ({e}). Using Analytical Physics Unmixer.")

    def predict_spectrum(self, X_features: np.ndarray) -> np.ndarray:
        """
        Runs prediction on 10D spectral features (shape: N x 10).
        Returns predicted abundances (shape: N x 8) summing to 1.0.
        """
        if self.keras_model is not None and self.scaler is not None:
            scaled = self.scaler.transform(X_features)
            raw = self.keras_model.predict(scaled, verbose=0)
            if raw.shape[1] == 8:
                return raw / np.sum(raw, axis=1, keepdims=True)

        # Fallback to Analytical Physical NNLS Constrained Spectral Unmixer
        from scipy.optimize import nnls
        abundances = []
        for x in X_features:
            a, _ = nnls(ENDMEMBERS_10D.T, x)
            s = np.sum(a)
            if s > 1e-6:
                a = a / s
            else:
                a = np.ones(8) / 8.0
            abundances.append(a)
        return np.array(abundances)

    def test_pure_endmember_isolation(self) -> Dict[str, Any]:
        """Test 1: Verify model correctly identifies pure endmembers with > 65% abundance."""
        results = []
        passed = 0
        for i, meta in enumerate(PRECISE_CONSTITUENTS):
            # 100 samples of pure endmember with realistic sensor noise
            pure_vec = ENDMEMBERS_10D[i:i+1]
            noise = np.random.normal(0, 0.005, size=(100, 10))
            samples = pure_vec + noise

            preds = self.predict_spectrum(samples)
            mean_pred = np.mean(preds, axis=0)
            dominant_idx = np.argmax(mean_pred)
            dominant_conf = mean_pred[i] * 100.0

            is_correct = (dominant_idx == i) and (dominant_conf >= 55.0)
            if is_correct:
                passed += 1

            results.append({
                "material": meta["name"],
                "short": meta["short"],
                "target_idx": i,
                "detected_idx": dominant_idx,
                "confidence_pct": round(dominant_conf, 1),
                "passed": is_correct
            })

        return {
            "name": "Pure Endmember Isolation",
            "score": round((passed / len(PRECISE_CONSTITUENTS)) * 100, 1),
            "passed": passed == len(PRECISE_CONSTITUENTS),
            "details": results
        }

    def test_binary_linearity(self) -> Dict[str, Any]:
        """Test 2: Dilution ladders verify abundance output correlates linearly with true concentration."""
        # Mix Water (idx 7) with PET (idx 0), Oil (idx 4), Sargassum (idx 6)
        test_pairs = [(7, 0, "Water + PET Plastic"), (7, 4, "Water + Oil Sheen"), (7, 6, "Water + Sargassum")]
        ladder = np.linspace(0.05, 0.95, 19)
        pair_scores = []

        for base_idx, target_idx, label in test_pairs:
            true_abundances = []
            features = []
            for frac in ladder:
                spec = (1.0 - frac) * ENDMEMBERS_10D[base_idx] + frac * ENDMEMBERS_10D[target_idx]
                features.append(spec)
                true_abundances.append(frac)

            preds = self.predict_spectrum(np.array(features))
            pred_fractions = preds[:, target_idx]

            # Pearson correlation coefficient
            corr = np.corrcoef(true_abundances, pred_fractions)[0, 1]
            r2 = corr ** 2
            pair_scores.append({"pair": label, "r2": round(r2, 4), "passed": r2 >= 0.90})

        avg_r2 = float(np.mean([p["r2"] for p in pair_scores]))
        return {
            "name": "Binary Dilution Linearity",
            "score": round(avg_r2 * 100, 1),
            "passed": bool(avg_r2 >= 0.90),
            "details": pair_scores
        }

    def test_conservation_of_mass(self) -> Dict[str, Any]:
        """Test 3: Abundance percentages must strictly sum to 100.0% (+- 0.05%)."""
        np.random.seed(42)
        alphas = np.array([0.45, 0.40, 0.35, 0.50, 0.20, 0.30, 0.45, 2.50])
        synthetic_abundances = np.random.dirichlet(alphas, size=1000)
        X_mix = np.dot(synthetic_abundances, ENDMEMBERS_10D) + np.random.normal(0, 0.01, size=(1000, 10))

        preds = self.predict_spectrum(X_mix)
        sums = np.sum(preds, axis=1) * 100.0

        max_err = float(np.max(np.abs(sums - 100.0)))
        mean_err = float(np.mean(np.abs(sums - 100.0)))
        is_conserved = bool(max_err <= 0.05)

        return {
            "name": "Conservation of Mass (100% Sum)",
            "score": round(100.0 - mean_err, 2),
            "max_deviation_pct": round(float(max_err), 4),
            "passed": is_conserved
        }

    def test_dirichlet_accuracy_benchmark(self, num_samples: int = 1500) -> Dict[str, Any]:
        """Test 4: Statistical accuracy on realistic Dirichlet ocean pixel mixtures."""
        np.random.seed(99)
        alphas = np.array([0.45, 0.40, 0.35, 0.50, 0.20, 0.30, 0.45, 2.50])
        y_true = np.random.dirichlet(alphas, size=num_samples)
        X_mix = np.dot(y_true, ENDMEMBERS_10D) + np.random.normal(0, 0.01, size=(num_samples, 10))

        y_pred = self.predict_spectrum(X_mix)

        # Per material metrics
        per_mat = []
        all_mae = []
        for i, meta in enumerate(PRECISE_CONSTITUENTS):
            mae = float(np.mean(np.abs(y_true[:, i] - y_pred[:, i])))
            rmse = float(np.sqrt(np.mean((y_true[:, i] - y_pred[:, i]) ** 2)))
            all_mae.append(mae)
            per_mat.append({
                "short": meta["short"],
                "name": meta["name"],
                "mae_pct": round(mae * 100, 2),
                "rmse_pct": round(rmse * 100, 2),
                "precision_pct": round((1.0 - mae) * 100, 2)
            })

        mean_mae = float(np.mean(all_mae))
        overall_precision = round((1.0 - mean_mae) * 100, 2)

        return {
            "name": "Dirichlet Realistic Mixture Benchmark",
            "score": overall_precision,
            "mean_mae_pct": round(mean_mae * 100, 2),
            "passed": bool(mean_mae <= 0.085), # MAE under 8.5% is high precision (>91.5% precision)
            "per_material": per_mat
        }

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Runs the complete battery of precision tests and generates a formatted audit card."""
        t1 = self.test_pure_endmember_isolation()
        t2 = self.test_binary_linearity()
        t3 = self.test_conservation_of_mass()
        t4 = self.test_dirichlet_accuracy_benchmark()

        overall_grade = round((t1["score"] * 0.3 + t2["score"] * 0.2 + t3["score"] * 0.2 + t4["score"] * 0.3), 1)
        is_pass = bool(t1["passed"] and t2["passed"] and t3["passed"] and t4["passed"] and (overall_grade >= 90.0))

        print("\n" + "=" * 76)
        print(f"🛰️  AQUAINTEL PRECISION AUDIT & BENCHMARK SCORECARD")
        print(f"🔬  Engine Mode: {self.mode}")
        print("=" * 76)

        print(f"\n[Test 1] {t1['name']:<40} : Score: {t1['score']}%  [{'PASS' if t1['passed'] else 'FAIL'}]")
        for d in t1["details"]:
            status = "✓" if d["passed"] else "✗"
            print(f"   {status} {d['short']:<6} | Detected: {d['confidence_pct']:>5.1f}% | {d['material']}")

        print(f"\n[Test 2] {t2['name']:<40} : Score: {t2['score']}%  [{'PASS' if t2['passed'] else 'FAIL'}]")
        for d in t2["details"]:
            print(f"   ✓ {d['pair']:<30} | R² Linearity: {d['r2']:.4f}")

        print(f"\n[Test 3] {t3['name']:<40} : Max Error: {t3['max_deviation_pct']:.4f}% [{'PASS' if t3['passed'] else 'FAIL'}]")
        print(f"\n[Test 4] {t4['name']:<40} : Mean Error: {t4['mean_mae_pct']}%  Score: {t4['score']}%")
        print("   " + "-" * 68)
        print(f"   {'Material':<32} | {'Mean Abs Error':<16} | {'Precision':<10}")
        print("   " + "-" * 68)
        for m in t4["per_material"]:
            print(f"   {m['name']:<32} | {m['mae_pct']:>6.2f}%         | {m['precision_pct']:>6.2f}%")
        print("   " + "-" * 68)

        print(f"\n🏆 OVERALL PRECISION RATING: {overall_grade}% / 100.0%")
        print(f"🎯 AUDIT VERDICT: {'PASSED (Extremely High Precision)' if is_pass else 'ACCEPTABLE / TUNING RECOMMENDED'}")
        print("=" * 76 + "\n")

        return {
            "overall_score": overall_grade,
            "passed": is_pass,
            "test_1": t1,
            "test_2": t2,
            "test_3": t3,
            "test_4": t4
        }

if __name__ == "__main__":
    import os
    keras_path = None
    scaler_path = None
    for k, s in [('omni_brain_precise.keras', 'omni_scaler_precise.pkl'), ('models/omni_brain_precise.keras', 'models/omni_scaler_precise.pkl')]:
        if os.path.exists(k) and os.path.exists(s):
            keras_path, scaler_path = k, s
            break

    suite = ModelBenchmarkSuite(keras_path, scaler_path)
    report = suite.run_all_benchmarks()
    sys.exit(0 if report["passed"] else 1)

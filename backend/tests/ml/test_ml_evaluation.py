"""Machine learning evaluation harnesses for LegalEdge models."""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix, classification_report
)

from app.ml.sentiment_analyzer import SentimentAnalyzer
from app.ml.forecasting_model import ForecastingModel
from app.ml.opportunity_ranker import OpportunityRanker
from app.ml.conflict_scorer import ConflictScorer


class MLEvaluationHarness:
    """Base class for ML model evaluation harnesses."""

    def __init__(self):
        self.metrics = {}
        self.predictions = []
        self.ground_truth = []
        self.evaluation_results = {}

    def evaluate_model(self, model, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a model on test data."""
        raise NotImplementedError

    def calculate_metrics(self, predictions: List[Any], ground_truth: List[Any]) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        raise NotImplementedError

    def generate_evaluation_report(self) -> Dict[str, Any]:
        """Generate comprehensive evaluation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "evaluation_summary": self._generate_summary()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate evaluation summary."""
        return {
            "total_samples": len(self.predictions),
            "evaluation_date": datetime.now().isoformat()
        }


class SentimentAnalysisHarness(MLEvaluationHarness):
    """Evaluation harness for sentiment analysis models."""

    def __init__(self):
        super().__init__()
        self.sentiment_labels = ["positive", "negative", "neutral"]

    def evaluate_model(self, model: SentimentAnalyzer, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate sentiment analysis model."""
        texts = test_data.get("texts", [])
        true_sentiments = test_data.get("sentiments", [])
        true_scores = test_data.get("scores", [])

        predictions = []
        pred_scores = []

        for text in texts:
            try:
                result = model.analyze_sentiment(text)
                predictions.append(result["sentiment"])
                pred_scores.append(result["confidence"])
            except Exception as e:
                # Handle prediction errors
                predictions.append("neutral")
                pred_scores.append(0.0)

        self.predictions = predictions
        self.ground_truth = true_sentiments

        # Calculate metrics
        self.metrics = self.calculate_metrics(predictions, true_sentiments)

        # Calculate score-based metrics if available
        if true_scores and pred_scores:
            score_metrics = self._calculate_score_metrics(pred_scores, true_scores)
            self.metrics.update(score_metrics)

        return self.generate_evaluation_report()

    def calculate_metrics(self, predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
        """Calculate sentiment analysis metrics."""
        # Convert labels to numeric for sklearn
        label_to_int = {label: i for i, label in enumerate(self.sentiment_labels)}
        y_true = [label_to_int.get(label, 2) for label in ground_truth]  # Default to neutral
        y_pred = [label_to_int.get(label, 2) for label in predictions]

        # Classification metrics
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
            "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
            "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
            "precision_micro": precision_score(y_true, y_pred, average="micro", zero_division=0),
            "recall_micro": recall_score(y_true, y_pred, average="micro", zero_division=0),
            "f1_micro": f1_score(y_true, y_pred, average="micro", zero_division=0),
        }

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        # Per-class metrics
        report = classification_report(y_true, y_pred, target_names=self.sentiment_labels, zero_division=0, output_dict=True)
        metrics["classification_report"] = report

        return metrics

    def _calculate_score_metrics(self, pred_scores: List[float], true_scores: List[float]) -> Dict[str, float]:
        """Calculate score-based metrics."""
        pred_array = np.array(pred_scores)
        true_array = np.array(true_scores)

        return {
            "mae": mean_absolute_error(true_array, pred_array),
            "mse": mean_squared_error(true_array, pred_array),
            "rmse": np.sqrt(mean_squared_error(true_array, pred_array)),
            "r2_score": r2_score(true_array, pred_array),
        }


class ForecastingHarness(MLEvaluationHarness):
    """Evaluation harness for forecasting models."""

    def __init__(self):
        super().__init__()

    def evaluate_model(self, model: ForecastingModel, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate forecasting model."""
        tickers = test_data.get("tickers", [])
        historical_data = test_data.get("historical_data", {})
        true_prices = test_data.get("true_prices", {})

        predictions = {}
        pred_confidences = {}

        for ticker in tickers:
            try:
                forecast = model.predict(ticker, days_ahead=30)
                predictions[ticker] = forecast["predicted_price"]
                pred_confidences[ticker] = forecast.get("confidence", 0.5)
            except Exception as e:
                predictions[ticker] = None
                pred_confidences[ticker] = 0.0

        # Calculate metrics for each ticker
        all_metrics = {}

        for ticker in tickers:
            if ticker in true_prices and predictions[ticker] is not None:
                ticker_metrics = self._calculate_forecast_metrics(
                    predictions[ticker],
                    true_prices[ticker],
                    pred_confidences.get(ticker, 0.5)
                )
                all_metrics[ticker] = ticker_metrics

        self.metrics = self._aggregate_forecast_metrics(all_metrics)
        self.evaluation_results = {"ticker_metrics": all_metrics}

        return self.generate_evaluation_report()

    def _calculate_forecast_metrics(self, predicted: float, actual: float, confidence: float) -> Dict[str, float]:
        """Calculate metrics for a single forecast."""
        error = abs(predicted - actual)
        percent_error = (error / actual) * 100 if actual != 0 else 0

        return {
            "predicted_price": predicted,
            "actual_price": actual,
            "absolute_error": error,
            "percent_error": percent_error,
            "confidence": confidence,
            "accuracy": 1 - (error / actual) if actual != 0 else 0,
            "directional_accuracy": 1 if (predicted > actual) == (predicted > actual) else 0,
        }

    def _aggregate_forecast_metrics(self, ticker_metrics: Dict[str, Dict]) -> Dict[str, float]:
        """Aggregate metrics across all tickers."""
        if not ticker_metrics:
            return {}

        errors = [metrics["absolute_error"] for metrics in ticker_metrics.values()]
        percent_errors = [metrics["percent_error"] for metrics in ticker_metrics.values()]
        accuracies = [metrics["accuracy"] for metrics in ticker_metrics.values()]
        directional_accuracies = [metrics["directional_accuracy"] for metrics in ticker_metrics.values()]

        return {
            "mean_absolute_error": np.mean(errors),
            "mean_percent_error": np.mean(percent_errors),
            "median_absolute_error": np.median(errors),
            "max_absolute_error": np.max(errors),
            "min_absolute_error": np.min(errors),
            "std_absolute_error": np.std(errors),
            "mean_accuracy": np.mean(accuracies),
            "mean_directional_accuracy": np.mean(directional_accuracies),
            "forecasts_evaluated": len(ticker_metrics)
        }


class OpportunityRankingHarness(MLEvaluationHarness):
    """Evaluation harness for opportunity ranking models."""

    def __init__(self):
        super().__init__()

    def evaluate_model(self, model: OpportunityRanker, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate opportunity ranking model."""
        opportunities = test_data.get("opportunities", [])
        true_rankings = test_data.get("true_rankings", {})

        predictions = []
        pred_scores = []

        for opp in opportunities:
            try:
                score = model.score_opportunity(opp)
                predictions.append(score["rank"])
                pred_scores.append(score["confidence"])
            except Exception as e:
                predictions.append(0)
                pred_scores.append(0.0)

        # Calculate ranking metrics
        self.metrics = self._calculate_ranking_metrics(predictions, true_rankings)

        return self.generate_evaluation_report()

    def _calculate_ranking_metrics(self, predictions: List[int], true_rankings: Dict[str, int]) -> Dict[str, float]:
        """Calculate ranking-specific metrics."""
        # Kendall Tau correlation for ranking quality
        # Spearman's rank correlation coefficient
        # Normalized Discounted Cumulative Gain (NDCG)

        # For now, use basic ranking metrics
        # In a real implementation, you'd calculate proper ranking metrics

        return {
            "mean_predicted_rank": np.mean(predictions),
            "median_predicted_rank": np.median(predictions),
            "rank_correlation": 0.0,  # Placeholder
            "ndcg_score": 0.0,  # Placeholder
            "precision_at_k": 0.0,  # Placeholder
        }


class ConflictScoringHarness(MLEvaluationHarness):
    """Evaluation harness for conflict scoring models."""

    def __init__(self):
        super().__init__()

    def evaluate_model(self, model: ConflictScorer, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate conflict scoring model."""
        portfolios = test_data.get("portfolios", [])
        legislation = test_data.get("legislation", [])
        true_conflicts = test_data.get("true_conflicts", {})

        predictions = []
        pred_scores = []

        for portfolio in portfolios:
            for bill in legislation:
                try:
                    conflict_score = model.score_conflict(portfolio, bill)
                    predictions.append(conflict_score["score"])
                    pred_scores.append(conflict_score["confidence"])
                except Exception as e:
                    predictions.append(0.0)
                    pred_scores.append(0.0)

        self.metrics = self._calculate_conflict_metrics(predictions, true_conflicts)

        return self.generate_evaluation_report()

    def _calculate_conflict_metrics(self, predictions: List[float], true_conflicts: Dict[str, float]) -> Dict[str, float]:
        """Calculate conflict scoring metrics."""
        if not true_conflicts:
            return {"error": "No ground truth data available"}

        pred_array = np.array(predictions)
        true_array = np.array(list(true_conflicts.values()))

        return {
            "mean_absolute_error": mean_absolute_error(true_array, pred_array),
            "mean_squared_error": mean_squared_error(true_array, pred_array),
            "root_mean_squared_error": np.sqrt(mean_squared_error(true_array, pred_array)),
            "r2_score": r2_score(true_array, pred_array),
            "mean_conflict_score": np.mean(pred_array),
            "std_conflict_score": np.std(pred_array),
            "conflict_correlation": np.corrcoef(pred_array, true_array)[0, 1] if len(pred_array) > 1 else 0.0,
        }


class ComprehensiveMLEvaluator:
    """Comprehensive ML evaluation system."""

    def __init__(self):
        self.sentiment_harness = SentimentAnalysisHarness()
        self.forecasting_harness = ForecastingHarness()
        self.opportunity_harness = OpportunityRankingHarness()
        self.conflict_harness = ConflictScoringHarness()

    def run_comprehensive_evaluation(self, models: Dict[str, Any], test_datasets: Dict[str, Dict]) -> Dict[str, Any]:
        """Run comprehensive evaluation of all ML models."""
        results = {}

        # Evaluate sentiment analysis
        if "sentiment_analyzer" in models and "sentiment_data" in test_datasets:
            results["sentiment_analysis"] = self.sentiment_harness.evaluate_model(
                models["sentiment_analyzer"],
                test_datasets["sentiment_data"]
            )

        # Evaluate forecasting
        if "forecasting_model" in models and "forecasting_data" in test_datasets:
            results["forecasting"] = self.forecasting_harness.evaluate_model(
                models["forecasting_model"],
                test_datasets["forecasting_data"]
            )

        # Evaluate opportunity ranking
        if "opportunity_ranker" in models and "opportunity_data" in test_datasets:
            results["opportunity_ranking"] = self.opportunity_harness.evaluate_model(
                models["opportunity_ranker"],
                test_datasets["opportunity_data"]
            )

        # Evaluate conflict scoring
        if "conflict_scorer" in models and "conflict_data" in test_datasets:
            results["conflict_scoring"] = self.conflict_harness.evaluate_model(
                models["conflict_scorer"],
                test_datasets["conflict_data"]
            )

        # Generate overall evaluation summary
        summary = self._generate_overall_summary(results)

        return {
            "timestamp": datetime.now().isoformat(),
            "model_evaluations": results,
            "overall_summary": summary
        }

    def _generate_overall_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall evaluation summary."""
        summary = {
            "total_models_evaluated": len(results),
            "evaluation_date": datetime.now().isoformat(),
            "model_performance": {}
        }

        for model_name, evaluation in results.items():
            if "metrics" in evaluation:
                summary["model_performance"][model_name] = {
                    "key_metrics": self._extract_key_metrics(evaluation["metrics"])
                }

        return summary

    def _extract_key_metrics(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from evaluation results."""
        key_metrics = {}

        # Extract the most important metrics based on model type
        if "accuracy" in metrics:
            key_metrics["accuracy"] = metrics["accuracy"]
        if "f1_macro" in metrics:
            key_metrics["f1_score"] = metrics["f1_macro"]
        if "mean_absolute_error" in metrics:
            key_metrics["mae"] = metrics["mean_absolute_error"]
        if "r2_score" in metrics:
            key_metrics["r2"] = metrics["r2_score"]

        return key_metrics

    def save_evaluation_results(self, results: Dict[str, Any], output_path: str):
        """Save evaluation results to file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def load_evaluation_results(self, input_path: str) -> Dict[str, Any]:
        """Load evaluation results from file."""
        with open(input_path, 'r') as f:
            return json.load(f)


class TestMLEvaluationHarnesses:
    """Tests for ML evaluation harnesses."""

    @pytest.fixture
    def sample_sentiment_data(self):
        """Sample sentiment analysis test data."""
        return {
            "texts": [
                "This new AI regulation is excellent for the industry.",
                "The proposed bill will harm innovation significantly.",
                "The legislation seems balanced and reasonable.",
                "This regulation is terrible for business growth.",
                "The new policy appears to be well thought out."
            ],
            "sentiments": ["positive", "negative", "neutral", "negative", "positive"],
            "scores": [0.8, -0.6, 0.1, -0.7, 0.5]
        }

    @pytest.fixture
    def sample_forecasting_data(self):
        """Sample forecasting test data."""
        return {
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "historical_data": {
                "AAPL": [150.0, 152.0, 148.0, 155.0, 157.0],
                "MSFT": [300.0, 305.0, 298.0, 310.0, 315.0],
                "GOOGL": [2800.0, 2850.0, 2750.0, 2900.0, 2920.0]
            },
            "true_prices": {
                "AAPL": 160.0,
                "MSFT": 320.0,
                "GOOGL": 2950.0
            }
        }

    def test_sentiment_analysis_harness(self, sample_sentiment_data):
        """Test sentiment analysis evaluation harness."""
        harness = SentimentAnalysisHarness()

        # Mock model
        mock_model = Mock()
        mock_model.analyze_sentiment.side_effect = [
            {"sentiment": "positive", "confidence": 0.8},
            {"sentiment": "negative", "confidence": 0.6},
            {"sentiment": "neutral", "confidence": 0.1},
            {"sentiment": "negative", "confidence": 0.7},
            {"sentiment": "positive", "confidence": 0.5}
        ]

        results = harness.evaluate_model(mock_model, sample_sentiment_data)

        assert "timestamp" in results
        assert "metrics" in results
        assert "accuracy" in results["metrics"]
        assert "f1_macro" in results["metrics"]
        assert "confusion_matrix" in results["metrics"]

    def test_forecasting_harness(self, sample_forecasting_data):
        """Test forecasting evaluation harness."""
        harness = ForecastingHarness()

        # Mock model
        mock_model = Mock()
        mock_model.predict.side_effect = [
            {"predicted_price": 158.0, "confidence": 0.7},
            {"predicted_price": 318.0, "confidence": 0.8},
            {"predicted_price": 2930.0, "confidence": 0.6}
        ]

        results = harness.evaluate_model(mock_model, sample_forecasting_data)

        assert "timestamp" in results
        assert "metrics" in results
        assert "mean_absolute_error" in results["metrics"]
        assert "mean_accuracy" in results["metrics"]
        assert "forecasts_evaluated" in results["metrics"]

    def test_comprehensive_evaluator(self, sample_sentiment_data, sample_forecasting_data):
        """Test comprehensive ML evaluator."""
        evaluator = ComprehensiveMLEvaluator()

        # Mock models
        mock_sentiment = Mock()
        mock_sentiment.analyze_sentiment.return_value = {"sentiment": "positive", "confidence": 0.8}

        mock_forecasting = Mock()
        mock_forecasting.predict.return_value = {"predicted_price": 160.0, "confidence": 0.7}

        models = {
            "sentiment_analyzer": mock_sentiment,
            "forecasting_model": mock_forecasting
        }

        test_datasets = {
            "sentiment_data": sample_sentiment_data,
            "forecasting_data": sample_forecasting_data
        }

        results = evaluator.run_comprehensive_evaluation(models, test_datasets)

        assert "timestamp" in results
        assert "model_evaluations" in results
        assert "overall_summary" in results
        assert len(results["model_evaluations"]) == 2

    def test_evaluation_results_saving(self, tmp_path):
        """Test saving and loading evaluation results."""
        evaluator = ComprehensiveMLEvaluator()

        # Create sample results
        results = {
            "timestamp": datetime.now().isoformat(),
            "model_evaluations": {
                "test_model": {
                    "metrics": {"accuracy": 0.95, "f1_score": 0.93}
                }
            }
        }

        # Save results
        output_file = tmp_path / "test_results.json"
        evaluator.save_evaluation_results(results, str(output_file))

        # Load results
        loaded_results = evaluator.load_evaluation_results(str(output_file))

        assert loaded_results["timestamp"] == results["timestamp"]
        assert "test_model" in loaded_results["model_evaluations"]

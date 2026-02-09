"""
Machine Learning Models Module for TradeGenius AI
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report


def train_random_forest(X_train, y_train, X_test=None, y_test=None, n_estimators=100):
    """
    Train Random Forest classifier

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features (optional)
        y_test: Test labels (optional)
        n_estimators: Number of trees

    Returns:
        Trained model and metrics dict
    """
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    metrics = {
        'model_name': 'Random Forest',
        'n_estimators': n_estimators
    }

    # Training metrics
    train_pred = model.predict(X_train)
    metrics['train_accuracy'] = accuracy_score(y_train, train_pred)

    # Test metrics if provided
    if X_test is not None and y_test is not None:
        test_pred = model.predict(X_test)
        metrics['test_accuracy'] = accuracy_score(y_test, test_pred)
        metrics['precision'] = precision_score(y_test, test_pred, zero_division=0)
        metrics['recall'] = recall_score(y_test, test_pred, zero_division=0)
        metrics['f1'] = f1_score(y_test, test_pred, zero_division=0)

    # Feature importance
    if hasattr(model, 'feature_importances_'):
        metrics['feature_importances'] = model.feature_importances_

    return model, metrics


def train_xgboost(X_train, y_train, X_test=None, y_test=None, n_estimators=100):
    """
    Train XGBoost classifier (uses sklearn's GradientBoosting as fallback)

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features (optional)
        y_test: Test labels (optional)
        n_estimators: Number of boosting rounds

    Returns:
        Trained model and metrics dict
    """
    try:
        import xgboost as xgb
        model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    except ImportError:
        # Fallback to sklearn's GradientBoosting
        model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )

    model.fit(X_train, y_train)

    metrics = {
        'model_name': 'XGBoost/GradientBoosting',
        'n_estimators': n_estimators
    }

    # Training metrics
    train_pred = model.predict(X_train)
    metrics['train_accuracy'] = accuracy_score(y_train, train_pred)

    # Test metrics if provided
    if X_test is not None and y_test is not None:
        test_pred = model.predict(X_test)
        metrics['test_accuracy'] = accuracy_score(y_test, test_pred)
        metrics['precision'] = precision_score(y_test, test_pred, zero_division=0)
        metrics['recall'] = recall_score(y_test, test_pred, zero_division=0)
        metrics['f1'] = f1_score(y_test, test_pred, zero_division=0)

    # Feature importance
    if hasattr(model, 'feature_importances_'):
        metrics['feature_importances'] = model.feature_importances_

    return model, metrics


def predict_direction(model, features, scaler=None):
    """
    Predict price direction

    Args:
        model: Trained model
        features: Feature array or DataFrame
        scaler: Optional scaler for features

    Returns:
        Prediction and probability
    """
    if isinstance(features, pd.DataFrame):
        features = features.values

    if len(features.shape) == 1:
        features = features.reshape(1, -1)

    # Handle NaN/Inf
    features = np.nan_to_num(features, nan=0, posinf=0, neginf=0)

    if scaler is not None:
        features = scaler.transform(features)

    prediction = model.predict(features)

    if hasattr(model, 'predict_proba'):
        probability = model.predict_proba(features)
        return prediction[0], probability[0]

    return prediction[0], None


def create_ensemble_model(X_train, y_train, X_test, y_test):
    """
    Create ensemble of multiple models

    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data

    Returns:
        Dict with models and ensemble prediction function
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC

    models = {}

    # Random Forest
    rf_model, rf_metrics = train_random_forest(X_train, y_train, X_test, y_test)
    models['RandomForest'] = {'model': rf_model, 'metrics': rf_metrics}

    # Gradient Boosting / XGBoost
    xgb_model, xgb_metrics = train_xgboost(X_train, y_train, X_test, y_test)
    models['XGBoost'] = {'model': xgb_model, 'metrics': xgb_metrics}

    # Logistic Regression
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    models['LogisticRegression'] = {
        'model': lr_model,
        'metrics': {
            'model_name': 'Logistic Regression',
            'test_accuracy': accuracy_score(y_test, lr_pred),
            'precision': precision_score(y_test, lr_pred, zero_division=0),
            'recall': recall_score(y_test, lr_pred, zero_division=0),
            'f1': f1_score(y_test, lr_pred, zero_division=0)
        }
    }

    # SVM (with probability)
    svm_model = SVC(probability=True, random_state=42)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    models['SVM'] = {
        'model': svm_model,
        'metrics': {
            'model_name': 'SVM',
            'test_accuracy': accuracy_score(y_test, svm_pred),
            'precision': precision_score(y_test, svm_pred, zero_division=0),
            'recall': recall_score(y_test, svm_pred, zero_division=0),
            'f1': f1_score(y_test, svm_pred, zero_division=0)
        }
    }

    def ensemble_predict(features):
        """Ensemble prediction using voting"""
        predictions = []
        probabilities = []

        for name, model_dict in models.items():
            model = model_dict['model']
            pred, prob = predict_direction(model, features)
            predictions.append(pred)
            if prob is not None:
                probabilities.append(prob[1] if len(prob) > 1 else prob[0])

        # Majority vote
        final_pred = 1 if sum(predictions) > len(predictions) / 2 else 0

        # Average probability
        avg_prob = np.mean(probabilities) if probabilities else 0.5

        return final_pred, avg_prob

    return {
        'models': models,
        'ensemble_predict': ensemble_predict
    }


def evaluate_model(model, X_test, y_test):
    """
    Comprehensive model evaluation

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels

    Returns:
        Dict with evaluation metrics
    """
    predictions = model.predict(X_test)

    metrics = {
        'accuracy': accuracy_score(y_test, predictions),
        'precision': precision_score(y_test, predictions, zero_division=0),
        'recall': recall_score(y_test, predictions, zero_division=0),
        'f1': f1_score(y_test, predictions, zero_division=0)
    }

    # Confusion matrix elements
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, predictions)
    if cm.shape == (2, 2):
        metrics['true_negatives'] = cm[0, 0]
        metrics['false_positives'] = cm[0, 1]
        metrics['false_negatives'] = cm[1, 0]
        metrics['true_positives'] = cm[1, 1]

    # Probability metrics if available
    if hasattr(model, 'predict_proba'):
        from sklearn.metrics import roc_auc_score, log_loss
        probabilities = model.predict_proba(X_test)
        try:
            metrics['roc_auc'] = roc_auc_score(y_test, probabilities[:, 1])
            metrics['log_loss'] = log_loss(y_test, probabilities)
        except:
            pass

    return metrics


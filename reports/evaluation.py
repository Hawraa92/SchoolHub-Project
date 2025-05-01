# reports/evaluation.py
"""
This module provides functions to compute evaluation metrics for the predictive model.
"""

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def compute_evaluation_metrics(y_true, y_pred):
    """
    Computes evaluation metrics given true labels and predicted labels.
    
    Parameters:
      - y_true: list or array of true labels.
      - y_pred: list or array of predicted labels.
      
    Returns:
      A dictionary containing accuracy, precision, recall, f1 score, and confusion matrix.
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()  # Convert numpy array to list for JSON serialization
    }
    return metrics

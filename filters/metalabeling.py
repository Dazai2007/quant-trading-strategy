import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

class MetaLabeling:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

    def train(self, X, y):
        """
        Train the secondary model.
        X: Features (e.g., volatility, imbalance, momentum)
        y: Binary label (1 if primary signal was correct, 0 otherwise)
        """
        self.model.fit(X, y)

    def predict(self, X):
        """
        Predict probability of the primary signal being correct.
        """
        # Return probability of class 1 (Signal Correct)
        return self.model.predict_proba(X)[:, 1]

    def filter_signals(self, primary_signals, X, threshold=0.6):
        """
        Filter primary signals based on meta-labeling prediction.
        """
        probs = self.predict(X)
        # Keep signal if probability > threshold, else 0 (No Trade)
        filtered_signals = np.where(probs > threshold, primary_signals, 0)
        return filtered_signals

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        return classification_report(y_test, y_pred)

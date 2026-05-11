"""
Predictor de Random Forest reconstruido a partir de nodos PySpark ML.

Esta clase debe vivir en app.ai para que joblib pueda deserializarla
correctamente cuando model_loader.py cargue el archivo .joblib.
"""

import numpy as np


class SparkRFPredictor:
    """
    Clasificador binario construido con árboles PySpark ML.
    Interfaz compatible con scikit-learn: predict(X) y predict_proba(X).
    """

    def __init__(self, trees: list[dict], n_classes: int = 2):
        self.trees = trees
        self.n_classes = n_classes
        self.classes_ = np.array([0, 1])

    def _predict_tree(self, tree: dict, x: np.ndarray) -> np.ndarray:
        node = tree[0]
        while True:
            left = node["left"]
            if left == -1:
                return np.array(node["proba"])
            if x[node["feature"]] <= node["threshold"]:
                node = tree[node["left"]]
            else:
                node = tree[node["right"]]

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n = X.shape[0]
        proba = np.zeros((n, self.n_classes), dtype=np.float64)
        for i in range(n):
            tree_probas = np.array(
                [self._predict_tree(tree, X[i]) for tree in self.trees]
            )
            proba[i] = tree_probas.mean(axis=0)
        return proba

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.predict_proba(X).argmax(axis=1)

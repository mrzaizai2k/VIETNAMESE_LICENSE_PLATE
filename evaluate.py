import os
import sys
sys.path.append("")

import numpy as np
from utils import read_config
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


# -----------------------------------------------------------
# Load dataset
# -----------------------------------------------------------
def load_dataset(config):
    class_path = config["model"]["classifications_path"]
    flat_path = config["model"]["flattened_images_path"]

    if not os.path.exists(class_path) or not os.path.exists(flat_path):
        raise FileNotFoundError(
            f"❌ Training files missing:\n- {class_path}\n- {flat_path}"
        )

    y = np.loadtxt(class_path, np.float32).reshape(-1)
    X = np.loadtxt(flat_path, np.float32)

    if X.shape[0] != y.shape[0]:
        raise ValueError("❌ Dataset mismatch: X rows != y rows")

    print(f"📌 Loaded dataset: {X.shape[0]} samples, {X.shape[1]} features")

    # Convert numeric ASCII → character labels
    y_labels = np.array([chr(int(v)) for v in y])

    return X, y_labels


# -----------------------------------------------------------
# Evaluate KNN for one K value
# -----------------------------------------------------------
def evaluate_single_k(X_train, X_test, y_train, y_test, k):
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train, y_train)

    y_pred = knn.predict(X_test)

    return {
        "k": k,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred),
    }


# -----------------------------------------------------------
# Evaluate across multiple K values
# -----------------------------------------------------------
def evaluate_knn_range(config, k_values):
    X, y = load_dataset(config)

    # Single train-test split for fairness
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, shuffle=True
    )

    print(f"🔀 Split: Train={len(X_train)}, Test={len(X_test)}\n")

    results = []

    for k in k_values:
        print(f"⚙️ Evaluating K = {k}")
        metrics = evaluate_single_k(X_train, X_test, y_train, y_test, k)
        # print(metrics["classification_report"])
        results.append(metrics)

    return {
        "status": "ok",
        "samples": int(len(X)),
        "results": results,   # List of metrics for each K
    }


# -----------------------------------------------------------
# CLI usage
# -----------------------------------------------------------
if __name__ == "__main__":
    CONFIG_PATH = "config/config.yaml"
    cfg = read_config(CONFIG_PATH)

    # Choose K range here
    K_VALUES = [1, 3, 5, 7, 9]

    result = evaluate_knn_range(cfg, K_VALUES)

    print("\n✅ Summary (per K):")
    for r in result["results"]:
        print(f"K={r['k']} -> acc={r['accuracy']:.4f}, f1={r['f1']:.4f}")

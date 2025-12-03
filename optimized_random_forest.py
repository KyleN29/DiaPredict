"""
Optimized Random Forest:
Uses RandomForestClassifier from scikit-learn with class_weight=
"balanced" which makes mistakes on the imbalanced data (Positive cases)
more costly.

The best threshold is dynamically determined by
what gives the best F1 Score in the validation set.
The threshold is just the cutoff for determining a No or Yes prediction
given the models prediction between 0-1.

This threshold is reduced afterwords to
optimize recall at the cost
of F1 Score, since false negatives are very
bad.

Results:
Using n_estimators=200


Test Precision: 0.31353994665311824
Test Recall: 0.6984014712123355
Test F1: 0.43278544817006354
Test PR AUC: 0.3593693375944958
Test Confusion Matrix:
            Predicted
             No      Yes
Actual  No [[32858 10809]
        Yes [ 2132  4937]]

These numbers honestly don't look great,
but they are pretty decent given the data
the model has to go off of.

"""


from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, classification_report, average_precision_score
import numpy as np
cdc = fetch_ucirepo(id=891)

X = cdc.data.features
y = cdc.data.targets

print("Dataset loaded.")
print("Shape:", X.shape)
print("Target distribution:")
print(y.value_counts())

# First split: train vs temp (val+test)
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.4, random_state=42, stratify=y
)

# Second split: temp -> val and test
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

model = RandomForestClassifier(
    class_weight="balanced",
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

y_val_prob = model.predict_proba(X_val)[:, 1]

best_t = 0
best_f1 = 0
for t in np.linspace(0.05, 0.95, 200):
    preds = (y_val_prob >= t).astype(int)
    score = f1_score(y_val, preds)
    if score > best_f1:
        best_f1 = score
        best_t = t

print("Chosen threshold from validation:", best_t)
print("Best validation F1:", best_f1)

y_test_prob = model.predict_proba(X_test)[:, 1]
y_test_pred = (y_test_prob >= (best_t * .8)).astype(int)

print("Test Precision:", precision_score(y_test, y_test_pred))
print("Test Recall:", recall_score(y_test, y_test_pred))
print("Test F1:", f1_score(y_test, y_test_pred))
print("Test PR AUC:", average_precision_score(y_test, y_test_prob))
print("Test Confusion Matrix:")
print(confusion_matrix(y_test, y_test_pred))






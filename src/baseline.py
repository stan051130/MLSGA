from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, log_loss
from sklearn.linear_model import LogisticRegression
import pandas as pd
from pathlib import Path

data_dir = Path("..") / "data/data"  
pl_files = sorted(data_dir.glob("Premier League-*.csv"))
    
pl_df = pd.concat([pd.read_csv(p) for p in pl_files], ignore_index=True)

pl_df["date"] = pd.to_datetime(pl_df["date"], errors="coerce")
pl_df = pl_df.sort_values("date").reset_index(drop=True)

pl_df["gf5_diff"] = pl_df["home_gf_rolls_mean_5"] - pl_df["away_gf_rolls_mean_5"]
pl_df["pts5_diff"] = pl_df["home_pts_rolls_sum_5"] - pl_df["away_pts_rolls_sum_5"]
feature_cols = ["gf5_diff", "pts5_diff"]
pl_df = pl_df.dropna(subset=feature_cols + ["result"]).copy()
pl_df = pl_df.sort_values(["date", "id"]).reset_index(drop=True)

le = LabelEncoder()
y = le.fit_transform(pl_df["result"])
print("Class mapping:", dict(zip(le.classes_, le.transform(le.classes_))))


split = int(0.8 * len(pl_df))

train = pl_df.iloc[:split]
test = pl_df.iloc[split:]

X_train, y_train = train[feature_cols], le.transform(train["result"])
X_test, y_test = test[feature_cols], le.transform(test["result"])

model = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(multi_class = "multinomial",
                               solver="lbfgs",
                               max_iter=1000,
                               random_state=42
    ))
])

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Log Loss:", log_loss(y_test, y_proba))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=le.classes_))
import os
import glob
import numpy as np
import pandas as pd
import joblib
from tqdm import tqdm
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error
base_path = "/content/drive/MyDrive/Operation_csv_data"
scenarios_folders = ["Normal", "FLB", "LOCA", "LOCAC"]
OUT_DIR = "/content/drive/MyDrive/npp_models"
USE_GRIDSEARCH = False
ROLLING_WINDOW = 3
PRED_PRE_EVENT_SECONDS = 20
sensitive_cols = ["TFPK", "P", "LVCR", "CNH2", "RC87", "RM1"]
os.makedirs(OUT_DIR, exist_ok=True)
def detect_event_time(df, sensitive_columns, smooth_window=5, percentile=99):

    if "TIME" not in df.columns:
        return df.index[-1] if len(df)>0 else 0.0

    grads = []
    for c in sensitive_columns:
        if c in df.columns:
            series = df[c].fillna(method="ffill").fillna(0).values.astype(float)
            g = np.abs(np.gradient(series))
            grads.append(g)
    if len(grads) == 0:
        return df["TIME"].max()

    total_grad = np.sum(grads, axis=0)
    kernel = np.ones(smooth_window) / smooth_window
    total_grad_smooth = np.convolve(total_grad, kernel, mode="same")
    thr = np.percentile(total_grad_smooth, percentile)
    idxs = np.where(total_grad_smooth > thr)[0]
    if len(idxs) == 0:
        return df["TIME"].max()
    event_idx = idxs[0]
    return float(df["TIME"].iloc[event_idx])

def add_time_features(df, feature_cols, rolling_window=3):
    """
    Добавляет для каждого признака:
     - rolling mean (window rolling_window)
     - diff (current - previous)
    Возвращает расширённый DataFrame (copy).
    """
    out = df.copy()
    for c in feature_cols:
        if c not in out.columns:
            out[c] = 0.0
    roll_cols = {}
    diff_cols = {}
    for c in feature_cols:
        roll_name = f"{c}_rm{rolling_window}"
        diff_name = f"{c}_d1"
        out[roll_name] = out[c].rolling(window=rolling_window, min_periods=1).mean()
        out[diff_name] = out[c].diff().fillna(0.0)
        roll_cols[c] = roll_name
        diff_cols[c] = diff_name
    return out

all_dfs = []
print("Читаем CSV и делаем автоматическую разметку...")
for scen in scenarios_folders:
    path = os.path.join(base_path, scen, "*.csv")
    files = sorted(glob.glob(path))
    print(f"  Сценарий {scen}: найдено {len(files)} файлов")
    for f in files:
        try:
            df = pd.read_csv(f)
            df["source_file"] = os.path.basename(f)
            df["scenario_type"] = scen

            if "TIME" not in df.columns:
                print(f"    ⚠ Пропущен (нет TIME): {f}")
                continue
            if scen != "Normal":
                event_time = detect_event_time(df, sensitive_cols, smooth_window=5, percentile=99)
            else:
                event_time = np.inf
            labels = []
            time_to_event = []
            t_end = float(df["TIME"].max())
            for t in df["TIME"].values:
                t_left = t_end - float(t)
                time_to_event.append(t_left)
                if scen == "Normal":
                    label = 0
                else:
                    if t < event_time - PRED_PRE_EVENT_SECONDS:
                        label = 0
                    elif t < event_time:
                        label = 1
                    else:
                        label = 2
                labels.append(label)
            df["label"] = labels
            df["time_to_event"] = time_to_event
            df["detected_event_time"] = event_time
            all_dfs.append(df)
        except Exception as e:
            print(f"    ⚠ Ошибка чтения {f}: {e}")

if len(all_dfs) == 0:
    raise RuntimeError("Ни один CSV не был загружен. Проверь путь base_path и содержимое.")

data = pd.concat(all_dfs, ignore_index=True)
print("Объединили данные. Форма:", data.shape)
print("Распределение классов:\n", data["label"].value_counts())

skip_cols = {"label", "time_to_event", "source_file", "scenario_type", "TIME", "detected_event_time"}
all_cols = [c for c in data.columns if c not in skip_cols]
numeric_cols = [c for c in all_cols if np.issubdtype(data[c].dtype, np.number)]
print(f"Числовых признаков найдено: {len(numeric_cols)}")

print("Делаем feature engineering (rolling mean и diff)...")
data_fe = add_time_features(data[["TIME", "source_file", "scenario_type", "label", "time_to_event", "detected_event_time"] + numeric_cols],
                            numeric_cols, rolling_window=ROLLING_WINDOW)
feat_cols = []
for c in numeric_cols:
    feat_cols.append(c)
    feat_cols.append(f"{c}_rm{ROLLING_WINDOW}")
    feat_cols.append(f"{c}_d1")

feat_cols = [c for c in feat_cols if c in data_fe.columns]
print(f"Итоговое число признаков после FE: {len(feat_cols)}")

scenarios = data_fe["source_file"].unique()
train_files, test_files = train_test_split(scenarios, test_size=0.2, random_state=42)
train_df = data_fe[data_fe["source_file"].isin(train_files)].reset_index(drop=True)
test_df = data_fe[data_fe["source_file"].isin(test_files)].reset_index(drop=True)

X_train = train_df[feat_cols].fillna(0)
y_train_class = train_df["label"].astype(int)
y_train_reg = train_df["time_to_event"].astype(float)

X_test = test_df[feat_cols].fillna(0)
y_test_class = test_df["label"].astype(int)
y_test_reg = test_df["time_to_event"].astype(float)

print("Train shape:", X_train.shape, "Test shape:", X_test.shape)
print("Train class distribution:\n", y_train_class.value_counts(normalize=True))
print("Test class distribution:\n", y_test_class.value_counts(normalize=True))
print("Обучаем RandomForest classifier...")
clf = RandomForestClassifier(n_jobs=-1, random_state=1, class_weight="balanced", n_estimators=300, max_depth=20)
clf.fit(X_train, y_train_class)
y_pred_clf = clf.predict(X_test)

print("\n=== Classification report ===")
print(classification_report(y_test_class, y_pred_clf, digits=4))
print("Confusion matrix:\n", confusion_matrix(y_test_class, y_pred_clf))
importances = pd.Series(clf.feature_importances_, index=feat_cols).sort_values(ascending=False)
print("\nTop-20 feature importances (classifier):")
print(importances.head(20))

print("\nОбучаем RandomForest regressor (time_to_event)...")
reg = RandomForestRegressor(n_jobs=-1, random_state=1, n_estimators=300, max_depth=20)
reg.fit(X_train, y_train_reg)
y_pred_reg = reg.predict(X_test)
print("MAE (regression):", mean_absolute_error(y_test_reg, y_pred_reg))

if USE_GRIDSEARCH:
    print("\nЗапускаем GridSearch (может занять долго)...")
    param_grid = {
        "n_estimators": [200, 400],
        "max_depth": [15, 25],
        "min_samples_split": [2, 5]
    }
    rf = RandomForestClassifier(n_jobs=-1, random_state=1, class_weight="balanced")
    grid = GridSearchCV(rf, param_grid, cv=3, scoring="f1_macro", n_jobs=-1, verbose=2)
    grid.fit(X_train, y_train_class)
    print("Лучшие параметры:", grid.best_params_)
    best_clf = grid.best_estimator_
    # заменить clf на лучший
    clf = best_clf
    y_pred_clf = clf.predict(X_test)
    print(classification_report(y_test_class, y_pred_clf, digits=4))
joblib.dump(clf, os.path.join(OUT_DIR, "clf_model_rf1.joblib"))
joblib.dump(reg, os.path.join(OUT_DIR, "reg_model_rf1.joblib"))
joblib.dump(feat_cols, os.path.join(OUT_DIR, "feature_columns1.joblib"))
print(f"\n✅ Модели и список признаков сохранены в {OUT_DIR}")
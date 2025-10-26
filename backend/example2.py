
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




# === Импорты ===
import os
import gc
import joblib
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import onnxruntime as ort

# === Пути ===
model_dir = "/content/drive/MyDrive/npp_models"
clf_path = os.path.join(model_dir, "clf_model_rf1.joblib")
reg_path = os.path.join(model_dir, "reg_model_rf1.joblib")

# === Освобождаем память перед началом ===
gc.collect()

print("📦 Загружаем модели...")
clf = joblib.load(clf_path)
reg = joblib.load(reg_path)
print("✅ Модели clf и reg загружены!")

# === Определяем количество признаков ===
n_features = clf.n_features_in_
print(f"📊 Количество признаков: {n_features}")

# === Создаем маленький пример данных ===
X_sample = np.random.rand(2, n_features).astype(np.float32)

# === Конвертация с контролем памяти ===
print("\n🔄 Конвертация моделей в ONNX (режим low-memory)...")

initial_type = [('float_input', FloatTensorType([None, n_features]))]

# --- Конвертация классификатора
print("➡ Конвертируем clf...")
clf.estimators_ = clf.estimators_[:20]  # Ограничим до 20 деревьев для экономии памяти
onnx_clf = convert_sklearn(clf, initial_types=initial_type)
onnx_clf_path = os.path.join(model_dir, "clf_model_rf1_small.onnx")
with open(onnx_clf_path, "wb") as f:
    f.write(onnx_clf.SerializeToString())
print(f"💾 ONNX классификатор сохранён: {onnx_clf_path}")

# --- Очистка памяти
del clf
gc.collect()

# --- Конвертация регрессора
print("➡ Конвертируем reg...")
reg.estimators_ = reg.estimators_[:20]  # Аналогично
onnx_reg = convert_sklearn(reg, initial_types=initial_type)
onnx_reg_path = os.path.join(model_dir, "reg_model_rf1_small.onnx")
with open(onnx_reg_path, "wb") as f:
    f.write(onnx_reg.SerializeToString())
print(f"💾 ONNX регрессор сохранён: {onnx_reg_path}")

# === Проверка через onnxruntime ===
print("\n🧠 Проверяем работу...")
sess_clf = ort.InferenceSession(onnx_clf_path)
sess_reg = ort.InferenceSession(onnx_reg_path)

pred_clf = sess_clf.run(None, {sess_clf.get_inputs()[0].name: X_sample})[0]
pred_reg = sess_reg.run(None, {sess_reg.get_inputs()[0].name: X_sample})[0]

print("🎯 Классификатор предсказал:", pred_clf)
print("📉 Регрессор предсказал:", pred_reg)

print("\n✅ Конвертация прошла успешно в low-memory режиме!")






import joblib
import pandas as pd
import numpy as np
from ipywidgets import VBox, HBox, Label, FloatSlider, Button, Output, Accordion, Layout
from IPython.display import display, clear_output

# === ЗАГРУЗКА МОДЕЛЕЙ ===
clf = joblib.load("/content/drive/MyDrive/npp_models/clf_model_rf1.joblib")
reg = joblib.load("/content/drive/MyDrive/npp_models/reg_model_rf1.joblib")
feature_columns = joblib.load("/content/drive/MyDrive/npp_models/feature_columns1.joblib")

# === СЛОВАРЬ ПОЛНЫХ НАЗВАНИЙ ===
feature_names_full = {
    "TIME": "Время (сек)", "TAVG": "Средняя температура RCS", "THA": "Температура горячего канала A",
    "THB": "Температура горячего канала B", "TCA": "Температура холодного канала A",
    "TCB": "Температура холодного канала B", "WRCA": "Поток охлаждающей жидкости реактора A",
    "WRCB": "Поток охлаждающей жидкости реактора B", "PSGA": "Давление парогенератора A",
    "PSGB": "Давление парогенератора B", "WFWA": "Подача воды парогенератора A",
    "WFWB": "Подача воды парогенератора B", "WSTA": "Паровой поток парогенератора A",
    "WSTB": "Паровой поток парогенератора B", "VOL": "Объем жидкости в RCS",
    "LVPZ": "Уровень давления в прессуризаторе", "VOID": "Объем воздуха в RCS",
    "WLR": "Утечка воды из RCS", "WUP": "Подача воды из прессуризатора и защитных клапанов",
    "HUP": "Энтальпия воды из прессуризатора", "HLW": "Энтальпия утечки RCS", "WHPI": "Поток HPI",
    "WECS": "Поток ECCS", "QMWT": "Тепловая мощность реактора", "LSGA": "Уровень воды SG A (широкий диапазон)",
    "LSGB": "Уровень воды SG B (широкий диапазон)", "QMGA": "Теплоотвод SG A", "QMGB": "Теплоотвод SG B",
    "NSGA": "Уровень воды SG A (узкий диапазон)", "NSGB": "Уровень воды SG B (узкий диапазон)",
    "TBLD": "Нагрузка турбины", "WTRA": "Утечка труб SG A", "WTRB": "Утечка труб SG B",
    "TSAT": "Температура насыщения прессуризатора", "QRHR": "Мощность RHR", "LVCR": "Уровень воды в активной зоне",
    "SCMA": "Запас подпитки канала A", "SCMB": "Запас подпитки канала B", "FRCL": "Фракция повреждения оболочки",
    "PRB": "Давление в здании реактора", "PRBA": "Частичное давление воздуха в RB",
    "TRB": "Температура в здании реактора", "LWRB": "Уровень воды в сборнике RB", "DNBR": "Отношение отрыва от кипения",
    "QFCL": "Мощность охлаждающего вентилятора", "WBK": "Поток через разрыв в RB", "WSPY": "Подача спрея прессуризатора",
    "WCSP": "Подача спрея корпуса", "HTR": "Мощность нагревателя прессуризатора",
    "MH2": "Масса водорода, выделенного Zr-H2O", "CNH2": "Концентрация водорода в RB",
    "RHBR": "Реактивность борной кислоты", "RHMT": "Реактивность температуры модератора",
    "RHFL": "Реактивность топлива (Доплер)", "RHRD": "Реактивность стержней", "RH": "Общая реактивность",
    "PWNT": "Мощность нейтронного потока", "PWR": "Тепловая мощность активной зоны",
    "TFSB": "Температура погруженного топлива", "TFPK": "Температура пикового топлива",
    "TF": "Средняя температура топлива", "TPCT": "Температура оболочки пикового топлива",
    "WCFT": "Поток аккумулятора", "WLPI": "Поток LPSI (RHR)", "WCHG": "Поток подпитки",
    "RM1": "Радиация в здании", "RM2": "Радиация в паропроводе", "RM3": "Радиация конденсатора",
    "RM4": "Радиация вспомогательного здания", "RC87": "Активность RCS", "RC131": "Концентрация I-131 в RCS",
    "STRB": "Скорость радиоактивного выброса RB", "STSG": "Скорость радиоактивного выброса SG клапаны",
    "STTB": "Скорость радиоактивного выброса конденсатор", "RBLK": "Масса утечки из RB",
    "SGLK": "Масса утечки из SG", "DTHY": "Доза на щитовидную железу (EAB)", "DWB": "Доза на тело (EAB)",
    "P": "Давление в RCS", "WRLA": "Поток MSV/ADV SG A", "WRLB": "Поток MSV/ADV SG B", "WLD": "Поток отбора",
    "MBK": "Интегрированный поток разрыва", "EBK": "Интегрированная энергия разрыва", "TKLV": "Объем воды RWST",
    "FRZR": "Фракция окисления Zr", "MDBR": "Масса кория в DW", "MCRT": "Масса расплавленного бетона",
    "MGAS": "Масса газов CCI", "TDBR": "Температура обломков в каверне", "TSLP": "Температура обломков в нижнем пленуме",
    "TCRT": "Температура расплавленного бетона", "PPM": "Концентрация бора в RCS", "RRCA": "Соотношение потока канала A",
    "RRCB": "Соотношение потока канала B", "RRCO": "Соотношение потока активной зоны", "WFLB": "Поток по линии FW Break"
}

base_features = list(feature_names_full.keys())

# === ГРУППИРОВКА ПО КАТЕГОРИЯМ ===
temp_features = [f for f in base_features if "T" in f or f.startswith("TH")]
press_features = [f for f in base_features if "P" in f and "PPM" not in f]
flow_features = [f for f in base_features if "W" in f]
react_features = [f for f in base_features if f.startswith("RH")]
rad_features = [f for f in base_features if f.startswith("RM") or f.startswith("RC")]

used = set(temp_features + press_features + flow_features + react_features + rad_features)
other_features = [f for f in base_features if f not in used]

groups = {
    "Температуры": temp_features,
    "Давление": press_features,
    "Потоки": flow_features,
    "Реактивность": react_features,
    "Радиация": rad_features,
    "Прочее": other_features
}

# === СОЗДАНИЕ СЛАЙДЕРОВ ===
slider_dict = {}
accordion_children = []

for group_name, feats in groups.items():
    group_widgets = []
    for f in feats:
        label = Label(value=feature_names_full[f], layout=Layout(width='350px'))
        slider = FloatSlider(min=0, max=1000, step=1, value=0, layout=Layout(width='400px'))
        slider_dict[f] = slider
        group_widgets.append(HBox([label, slider]))
    accordion_children.append(VBox(group_widgets))

accordion = Accordion(children=accordion_children)
for i, name in enumerate(groups.keys()):
    accordion.set_title(i, name)
accordion.layout = Layout(max_height='700px', overflow_y='scroll')

button = Button(description="Сделать прогноз", button_style="success")
output = Output()

# === ЛОГИКА ПРОГНОЗА ===
def predict_status(input_data: dict):
    df = pd.DataFrame([input_data])

    # автоматическое добавление производных признаков
    for base in base_features:
        rm_name = f"{base}_rm3"
        d1_name = f"{base}_d1"
        val = df[base].iloc[0]
        df[rm_name] = val * 0.98  # имитация усреднения
        df[d1_name] = np.random.normal(0, 0.01)  # небольшая динамика

    for f in feature_columns:
        if f not in df.columns:
            df[f] = 0

    df = df[feature_columns].fillna(0)
    pred_class = clf.predict(df)[0]
    probs = clf.predict_proba(df)[0]
    status = {0: "Норма", 1: "Предавария", 2: "Авария"}.get(pred_class, "Неизвестно")
    pred_time = reg.predict(df)[0]
    return status, pred_time, probs

# === КНОПКА ===
def on_button_click(b):
    input_data = {f: slider_dict[f].value for f in base_features}
    status, time_left, probs = predict_status(input_data)
    with output:
        clear_output()
        print("=== Результат ===")
        print(f"Состояние: {status}")
        print(f"Прогноз времени до события: {time_left:.1f} секунд")
        print(f"Вероятности → Норма={probs[0]:.2f}, Предавария={probs[1]:.2f}, Авария={probs[2]:.2f}")

button.on_click(on_button_click)
display(accordion, button, output)

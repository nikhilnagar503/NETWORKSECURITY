# NETWORKSECURITY

An end-to-end, production-style pipeline for phishing detection using URL and website features. The system ingests labeled data from MongoDB, validates schema and drift, transforms features (KNNImputer), trains multiple classifiers with model selection, and logs metrics with MLflow. Final artifacts include a reusable preprocessor and trained model.

---

## Table of Contents
- [Overview](#overview)
- [Dataset](#dataset)
- [ML Problem](#ml-problem)
- [Pipeline Architecture](#pipeline-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Data Ingestion](#data-ingestion)
- [Configuration & Constants](#configuration--constants)
- [MLflow Tracking](#mlflow-tracking)
- [Run the Pipeline](#run-the-pipeline)
- [Notes & Best Practices](#notes--best-practices)
- [License](#license)

---

## Overview
This project builds a phishing URL classifier using a robust ML pipeline:
- Ingests labeled records from MongoDB
- Validates schema and detects data drift
- Transforms features with KNNImputer
- Trains and evaluates multiple models with grid search
- Logs metrics and models to MLflow
- Saves reproducible artifacts for deployment

Use cases:
- Real-time URL phishing detection
- Browser extensions that flag unsafe sites
- API service for URL safety scoring
- Cybersecurity ML portfolio project

---

## Dataset
Each row represents a website URL with engineered features derived from:
- URL structure (length, IP usage, subdomains)
- SSL indicators
- Domain metadata (age, registrar)
- JavaScript behaviors (on_mouseover, popups)

Common categorical encodings: -1, 0, 1 or 0/1/2

Target column:
- `Result` (int64)
  - `1` → Legitimate
  - `-1` → Phishing
  - `0` → Suspicious/Unknown (optional in some datasets)

Example row:
```
having_IP_Address  URL_Length  SSLfinal_State  ...  Result
1                  0           -1              ...  -1
```

---

## ML Problem
- Task: Binary classification (Phishing vs Legitimate)
- Goal: Predict whether a URL is phishing based on extracted features

Models commonly effective:
- Logistic Regression
- Random Forest
- Gradient Boosting / XGBoost / LightGBM
- SVM
- Simple Neural Networks

Random Forest and Gradient Boosting often perform well out-of-the-box for tabular features.

---

## Pipeline Architecture
1) Data Ingestion
   - Load MongoDB collection → DataFrame
   - Save feature store CSV and split train/test

2) Data Validation
   - Enforce schema (column count)
   - Detect dataset drift via KS test
   - Persist drift report YAML

3) Data Transformation
   - Drop target from features
   - Normalize target (`-1` → `0` internally for binary models)
   - Fit `KNNImputer` on train; transform train/test
   - Save arrays (`.npy`) and preprocessor (`preprocessing.pkl`)

4) Model Training
   - Evaluate multiple classifiers via grid search
   - Compute F1, precision, recall on train/test
   - Log to MLflow
   - Save final model and combined preprocessor+model wrapper

---

## Tech Stack
- Python: 3.9+
- MongoDB (data source)
- Libraries:
  - pandas, numpy, scikit-learn
  - pymongo, python-dotenv
  - mlflow (local file store)
  - scipy (KS test)
- Logging: Python `logging` with timestamped logs

---

## Project Structure
```
NETWORKSECURITY/
├─ main.py                                  # Orchestrates the full pipeline run
├─ push_data.py                             # Loads CSV into MongoDB
├─ network_security/
│  ├─ components/
│  │  ├─ data_ingestion.py                 # Mongo -> CSV, split train/test
│  │  ├─ data_validation.py                # Schema + drift check
│  │  ├─ data_transformation.py            # KNNImputer + save npy + preprocessor
│  │  └─ model_trainer.py                  # Model selection, MLflow, final save
│  ├─ constants/
│  │  └─ training_pipeline/__init__.py     # Paths, names, params
│  ├─ entity/
│  │  ├─ config_entity.py                  # Config dataclasses
│  │  └─ artifact_entity.py                # Artifact dataclasses
│  ├─ exception/exception.py               # Custom exception class
│  ├─ logging/logger.py                    # Logging setup
│  └─ utils/
│     ├─ main_utils/utils.py               # IO helpers
│     └─ ml_utils/...                      # Model wrapper, metrics, evaluation
├─ data_schema/schema.yaml                  # Column schema for validation
├─ final_model/                             # Persisted preprocessor/model
└─ logs/                                    # Timestamped run logs
```
Note: Some folders are created at runtime (Artifacts/, final_model/, logs/).

---

## Setup

### 1) Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas numpy scikit-learn pymongo python-dotenv mlflow scipy certifi
```

### 2) MongoDB connection
Create a `.env` at repository root:
```
MONGO_DB_URL=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
```
Used in `data_ingestion.py` and `push_data.py` via `python-dotenv`.

---

## Data Ingestion
If your dataset is not yet in MongoDB, use `push_data.py`:

Defaults in the script:
- `FILE_PATH="Network_Data\phisingData.csv"`
- `DATABASE="Nikhil"`
- `Collection="NetworkData"`

Run:
```bash
python push_data.py
```
This converts the CSV to JSON and inserts into the specified MongoDB collection.

---

## Configuration & Constants
Defined in `network_security/constants/training_pipeline/__init__.py`:

- Target column: `Result`
- Artifacts:
  - `Artifacts/<timestamp>/`
  - Data ingestion: `feature_store/phisingData.csv`, `ingested/train.csv`, `ingested/test.csv`
  - Data validation: `validated/train.csv`, `validated/test.csv`, `drift_report/report.yaml`
  - Data transformation: `transformed/train.npy`, `transformed/test.npy`, `transformed_object/preprocessing.pkl`
  - Model trainer: `trained_model/model.pkl`
- Parameters:
  - Train/test split ratio: `0.2`
  - KNNImputer:
    ```
    {
      "missing_values": np.nan,
      "n_neighbors": 3,
      "weights": "uniform"
    }
    ```
  - Expected accuracy: `0.6`
  - Overfitting threshold: `0.05`
- MongoDB:
  - Database: `"Nikhil"`
  - Collection: `"NetworkData"`

---

## MLflow Tracking
In `model_trainer.py`:
```python
mlflow.set_tracking_uri("file:///C:/desk1/network_security/NETWORKSECURITY/mlruns")
```
- Update this path for your environment
- Metrics logged: `f1_score`, `precision_score`, `recall_score`
- Models logged via:
```python
mlflow.sklearn.log_model(best_model, "model1")
```

To open MLflow UI:
```bash
mlflow ui --backend-store-uri file:///C:/desk1/network_security/NETWORKSECURITY/mlruns
# Visit http://127.0.0.1:5000
```

---

## Run the Pipeline
1) Ensure MongoDB has data (see ingestion)
2) Add `.env` with `MONGO_DB_URL`
3) Optionally update MLflow tracking URI
4) Execute:
```bash
python main.py
```

Artifacts will be created under:
```
Artifacts/<timestamp>/
  data_ingestion/
  data_validation/
  data_transformation/
  model_trainer/
logs/<timestamp>/
final_model/
```

---

## Notes & Best Practices
- Keep `data_schema/schema.yaml` aligned with the dataset; validation checks column count strictly
- Target normalization: `Result == -1` is mapped to `0` internally for binary learners—ensure consistency in evaluation
- Update MLflow tracking URI to a valid local/remote backend
- Custom `NetworkSecurityException` includes filename and line number for easier debugging

---

## License
MIT License. See [LICENSE](LICENSE) for details.

---

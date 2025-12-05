# NETWORKSECURITY

An end-to-end pipeline for network security data processing and classification. It ingests data from MongoDB, validates schema and drift, transforms features using KNNImputer, trains classification models, logs metrics to MLflow, and persists the final model.

---

## What This Dataset Represents (Phishing Detection)

Each row corresponds to a website URL, and each column is a feature engineered from that URL, HTML behavior, or domain metadata. Examples:

- `having_IP_Address`: whether the URL directly uses an IP address
- `URL_Length`: whether the URL is unusually long
- `SSLfinal_State`: whether SSL appears valid/invalid
- `having_Sub_Domain`: whether there are excessive subdomains
- `age_of_domain`: domain age signals
- JavaScript indicators such as `on_mouseover`, `popUpWidnow`, etc.

Most feature values are categorical encodings like `-1`, `0`, `1` (dangerous, suspicious, safe) or `0/1/2`.

The final column:

- `Result` (int64)
  - `1` → Legitimate (safe, valid)
  - `-1` → Phishing (fake, unsafe)
  - Sometimes `0` → Suspicious/Unknown (not always used)

This dataset is widely used in cybersecurity + machine learning for phishing URL detection.

---

## ML Problem Framing

- Task: Binary Classification
- Goal: Given URL-based features, classify the URL as phishing or legitimate.

Commonly effective models:
- Logistic Regression
- Random Forest
- Gradient Boosting / XGBoost / LightGBM
- SVM
- Simple Neural Networks

Random Forest and XGBoost often perform very well out-of-the-box on this type of data.

Example (imagined) row:

```
having_IP_Address  URL_Length  SSLfinal_State  ...  Result
1                  0           -1              ...  -1
```

Interpretation:
- IP present → suspicious/dangerous
- Normal length → okay
- Invalid SSL → suspicious
- Result → phishing (`-1`)

Potential applications:
- Phishing URL detector
- Browser extension to flag dangerous sites
- API service for URL safety checks
- Cybersecurity ML portfolio project

---

## Key Components

- Data ingestion:
  - Reads labeled phishing/benign network records from MongoDB.
  - Exports a feature store CSV and splits train/test.
- Data validation:
  - Enforces schema column count.
  - Performs KS test-based dataset drift checks.
  - Persists a drift report YAML.
- Data transformation:
  - Uses `KNNImputer` with parameters defined in constants.
  - Saves transformed arrays (`.npy`) and the preprocessor object (`preprocessing.pkl`).
- Model training:
  - Evaluates multiple classifiers with grid search (RandomForest, DecisionTree, GradientBoosting, LogisticRegression, AdaBoost).
  - Computes classification metrics (f1, precision, recall).
  - Logs metrics and model to MLflow.
  - Saves final model and a combined preprocessor+model wrapper.

---

## Tech Stack

- Python: 3.9+
- MongoDB: for source data storage
- Libraries:
  - pandas, numpy, scikit-learn
  - pymongo, python-dotenv
  - mlflow (local file store)
  - scipy (KS test)
- Logging: Python logging with rolling timestamped logs

---

## Repository Structure

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
│  │  └─ training_pipeline/__init__.py     # All constants (paths, names, params)
│  ├─ entity/
│  │  ├─ config_entity.py                  # Config dataclasses (paths, thresholds)
│  │  └─ artifact_entity.py                # Artifact dataclasses (paths, metrics)
│  ├─ exception/exception.py               # Custom exception class
│  ├─ logging/logger.py                    # Logging setup
│  └─ utils/
│     ├─ main_utils/utils.py               # IO helpers: save/load arrays/objects
│     └─ ml_utils/...                      # Model wrapper, metrics, evaluation
├─ data_schema/schema.yaml                  # Column schema for validation
├─ final_model/                             # Persisted preprocessor/model
└─ logs/                                    # Timestamped run logs
```

Note: Some folders are created at runtime (Artifacts/, final_model/, logs/).

---

## Environment Setup

### 1) Python dependencies
Create and activate a virtual environment, then install requirements (edit as needed):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas numpy scikit-learn pymongo python-dotenv mlflow scipy certifi
```

### 2) MongoDB connection
Add a `.env` file at the repository root:
```
MONGO_DB_URL=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
```

The code reads this via `python-dotenv` in both `data_ingestion.py` and `push_data.py`.

---

## Data Ingestion into MongoDB

If your raw CSV is not in MongoDB yet, use `push_data.py`:

- Update the CSV path and database/collection names as needed:
  - Default in script:
    - FILE_PATH="Network_Data\phisingData.csv"
    - DATABASE="Nikhil"
    - Collection="NetworkData"
- Run:
```bash
python push_data.py
```

This converts the CSV to JSON records and inserts them into the specified MongoDB collection.

---

## Pipeline Constants and Paths

Defined in `network_security/constants/training_pipeline/__init__.py`:

- Target column: `Result`
- Artifact directories and file names:
  - Artifacts/ (timestamped)
  - Data ingestion:
    - feature_store/phisingData.csv
    - ingested/train.csv, ingested/test.csv
  - Data validation:
    - validated/train.csv, validated/test.csv
    - drift_report/report.yaml
  - Data transformation:
    - transformed/train.npy, transformed/test.npy
    - transformed_object/preprocessing.pkl
  - Model trainer:
    - trained_model/model.pkl
- Parameters:
  - Train/test split ratio: `0.2`
  - KNNImputer params:
    ```
    {
      "missing_values": np.nan,
      "n_neighbors": 3,
      "weights": "uniform"
    }
    ```
  - Expected accuracy: `0.6`
  - Overfitting threshold: `0.05`

MongoDB names:
- Database: `"Nikhil"`
- Collection: `"NetworkData"`

---

## MLflow Tracking

In `model_trainer.py`, MLflow tracking is configured to a local file store:
```python
mlflow.set_tracking_uri("file:///C:/desk1/network_security/NETWORKSECURITY/mlruns")
```

- Change this path to match your environment.
- Metrics logged:
  - `f1_score`, `precision_score`, `recall_score`
- Models logged via `mlflow.sklearn.log_model(best_model, "model1")`.

To view MLflow UI:
```bash
mlflow ui --backend-store-uri file:///C:/desk1/network_security/NETWORKSECURITY/mlruns
# Then open http://127.0.0.1:5000
```

Adjust the path if you changed `set_tracking_uri`.

---

## How the Pipeline Runs

`main.py` orchestrates the following:

1) Build configs (timestamped artifact directory):
   - `TrainingPipelineConfig`
   - `DataIngestionConfig`, `DataValidationConfig`, `DataTransformationConfig`, `ModelTrainerConfig`

2) Data Ingestion:
   - `DataIngestion.export_collection_as_dataframe()` reads from MongoDB.
   - Saves feature store CSV and splits train/test.
   - Produces `DataIngestionArtifact` with train and test file paths.

3) Data Validation:
   - Checks number of columns against `data_schema/schema.yaml`.
   - Runs KS test to detect drift.
   - Writes drift report YAML.
   - Produces `DataValidationArtifact`.

4) Data Transformation:
   - Reads validated train/test CSV.
   - Drops `Result` from features, normalizes target labels (`-1` → `0` during transformation for binary models).
   - Fits `KNNImputer` on train, transforms train and test.
   - Saves `.npy` arrays and `preprocessing.pkl`.
   - Produces `DataTransformationArtifact`.

5) Model Training:
   - Evaluates multiple models with parameter grids via `evaluate_models`.
   - Selects best model by score.
   - Computes classification metrics on train and test.
   - Logs metrics and model to MLflow.
   - Saves final model (`final_model/model.pkl`) and combined wrapper (`trained_model/model.pkl`).
   - Produces `ModelTrainerArtifact`.

---

## Running the Pipeline

1) Ensure MongoDB has data (see ingestion step above).
2) Ensure `.env` contains `MONGO_DB_URL`.
3) Optionally adjust MLflow tracking URI in `model_trainer.py`.
4) Run:
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

## Notes and Tips

- Schema file: Keep `data_schema/schema.yaml` updated with the exact column list used in the dataset; validation strictly checks column count.
- Target normalization: The pipeline maps `Result == -1` to `0` internally for binary learners; ensure this aligns with your evaluation logic.
- Environment paths: Update the MLflow tracking URI to a valid local or remote backend for your machine.
- Error handling: Custom `NetworkSecurityException` captures filename and line number for easier debugging.

---

## License

MIT License. See `LICENSE` for details.

---

## Language Help (Optional)

Original: "so it will predict the that website is valid or not"

Improved: "So it will predict whether the website is valid or not?"

Original: "what is this data i mean can you tell me the ml problem that can be frame using this"

Improved: "What is this dataset? Can you tell me what ML problem can be framed using it?"

Keep going—you’re improving fast!

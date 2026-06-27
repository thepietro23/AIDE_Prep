import mlflow

with mlflow.start_run():
    print("MLflow run started")

mlflow.log_param("max_depth", 10)
mlflow.log_param("n_estimators", 100)
mlflow.log_metric("accuracy", 0.87)
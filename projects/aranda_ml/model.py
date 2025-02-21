import mlflow
import mlflow.spark
import mlflow.pyfunc
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec
from mlflow.tracking import MlflowClient
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import SparkSession
from utils.config import config

params = config

ENVIRONMENT = params["environments"]["develop"]
CATALOG_NAME = ENVIRONMENT["catalog_name"]
SCHEMA_NAME = ENVIRONMENT["schema_name"]
TABLE_NAME = ENVIRONMENT["table_name"]
MODEL_NAME = ENVIRONMENT["model_name"]
CATALOG = f'{CATALOG_NAME}.{SCHEMA_NAME}.{TABLE_NAME}'
VOCAB_SIZE = params["model_params"]["vocab_size"]
LAYER = params["model_params"]["layer"]
MAX_ITER = params["model_params"]["max_iter"]
SOLVER = params["model_params"]["solver"]
STEP_SIZE = params["model_params"]["step_size"]
TOL = float(params["model_params"]["tol"])
SEED = params["model_params"]["seed"]
SPLITS = params["model_params"]["splits"]
DATABRICKS_UC = params["databricks"]["databricks_uc"]
DATASET_DESCRIPTION = params["dataset"]["description"]
EXPERIMENT_NAME = params["experiment"]["name"]
MODEL_FULL_NAME = f'{CATALOG_NAME}.{SCHEMA_NAME}.{MODEL_NAME}'

df = spark.read.table(CATALOG).select("id", "CategoryID_idx", "Description")

tokenizer = Tokenizer(inputCol="Description", outputCol="words")
stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered")
count_vectorizer = CountVectorizer(inputCol="filtered", outputCol="features", vocabSize=VOCAB_SIZE)
num_classes = df.select("CategoryID_idx").distinct().count()
LAYERS = [VOCAB_SIZE, LAYER, num_classes]
mlp = MultilayerPerceptronClassifier(
    layers=LAYERS, labelCol="CategoryID_idx", featuresCol="features", 
    maxIter=MAX_ITER, solver=SOLVER, stepSize=STEP_SIZE, tol=TOL
)
pipeline = Pipeline(stages=[tokenizer, stopwords_remover, count_vectorizer, mlp])
train_data, test_data = df.randomSplit(SPLITS, seed=SEED)
model = pipeline.fit(train_data)

with mlflow.start_run(run_name=EXPERIMENT_NAME) as run:
   
    signature = ModelSignature(
        inputs=Schema([ColSpec(type="string", name="description")]),
        outputs=Schema([ColSpec(type="double", name="categoria")])
    )

    model_info = mlflow.spark.log_model(model, f"{EXPERIMENT_NAME}", signature=signature, )

    mlflow.log_params({
        "maxIter": MAX_ITER, "stepSize": STEP_SIZE, "tol": TOL, "solver": SOLVER,
        "vocabSize": VOCAB_SIZE, "layers": LAYERS, "splits": SPLITS, "dataset": CATALOG,
        "num_rows": df.count(), "num_columns": len(df.columns)
    })

    mlflow.set_tag("dataset_description", DATASET_DESCRIPTION)
    predictions = model.transform(test_data)
    evaluator = MulticlassClassificationEvaluator(labelCol="CategoryID_idx", predictionCol="prediction")

    mlflow.log_metrics({
        "accuracy_score": evaluator.setMetricName("accuracy").evaluate(predictions),
        "f1_score": evaluator.setMetricName("f1").evaluate(predictions)
    })
    mlflow.end_run()
    
mlflow.set_registry_uri(DATABRICKS_UC)
runs = mlflow.search_runs(order_by=['metrics.accuracy_score DESC'])
if not runs.empty:
    best_run = runs.iloc[0]
    model_version = mlflow.register_model(f"runs:/{best_run.run_id}/{EXPERIMENT_NAME}", MODEL_FULL_NAME)
    client = MlflowClient()
    client.set_registered_model_alias(MODEL_FULL_NAME, "Champion", model_version.version)
    
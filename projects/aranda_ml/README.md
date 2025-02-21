# Multilayer Perceptron Classifier Aranda (MLflow & Spark) 🚀

Este proyecto implementa un **clasificador Perceptrón Multicapa (MLP)** utilizando **Spark ML y MLflow** para la gestión de experimentos y seguimiento de modelos.

## 📌 Características
✅ Implementa un **pipeline de preprocesamiento y modelado** con Spark ML.  
✅ Utiliza **MLflow** para seguimiento de experimentos y almacenamiento de modelos.  
✅ Usa **Databricks UC** como repositorio de modelos.  
✅ Soporta múltiples entornos de configuración a través de **config/base.yaml**.

---

## 📂 Estructura del Proyecto
```
📦 project_root/
 ┣ 📂 config/
 ┃ ┗ 📜 base.yaml                       # Configuración general del modelo y datos
 ┣ 📂 notebooks/
 ┃ ┣ 📜 data_preparation.ipynb          # Preparar datos
 ┃ ┣ 📜 eda.ipynb                       # EDA
 ┃ ┣ 📜 test_evaluation.ipynb           # Test
 ┣ 📂 utils/
 ┃ ┣ 📜 config.py                       # Carga de configuraciones YAML
 ┣ 📜 model.py                          # Implementación del modelo MLP con MLflow y Spark
 ┣ 📜 README.md                         # Documentación del proyecto
 ┣ 📜 requirements.txt                  # Dependencias necesarias
```

---

## 🔧 Requisitos
Antes de ejecutar el proyecto, asegúrate de instalar las dependencias necesarias:

```bash
pip install -r requirements.txt
```

También necesitarás un entorno de **Apache Spark** y una configuración activa de **Databricks** si usas UC con ML.

---

## ⚙️ Configuración
El archivo `config/base.yaml` contiene los parámetros del modelo y la configuración del entorno. Aquí un ejemplo:

```yaml
aranda:
  model_params:
    tol: 1e-6
    seed: 123
    layer: 100
    last_run: -1
    max_iter: 300
    vocab_size: 5000
    solver: "l-bfgs"
    step_size: 0.01
    first_element: 0
    splits: [0.76, 0.24]

  databricks:
    databricks_uc: "databricks-uc"

  dataset:
    description: "Este conjunto de datos contiene información sobre incidentes de soporte, con campos como CategoryID_idx y su Description."

  experiment:
    name: "perceptron_classifier_experiment"

  environments:
    develop:
      catalog_name: "tmp_cat_dev"
      schema_name: "aranda_ml"
      table_name: "features"
      model_name: "perceptron_classifier"

    master:
      catalog_name: "tmp_cat_prod"
      schema_name: "aranda_ml"
      table_name: "features"
      model_name: "perceptron_classifier"
```

Puedes cambiar estos valores según sea necesario para ajustarlos a tu entorno.

---

## 🚀 Ejecutar el Entrenamiento
Para entrenar el modelo y registrarlo en MLflow, ejecuta:

```bash
python models/baseline.py
```

Esto:
1. Cargará los datos desde Spark.
2. Aplicará el preprocesamiento (tokenización, eliminación de stopwords y vectorización).
3. Entrenará un **Perceptrón Multicapa (MLP)** con los parámetros definidos en `config/base.yaml`.
4. Evaluará el modelo y guardará los resultados en MLflow.
5. Registrará el mejor modelo en **Databricks UC** como "Champion".

---

## 📊 Seguimiento de Experimentos
Puedes visualizar los experimentos ejecutados con MLflow con:

```bash
mlflow ui
```

Esto abrirá una interfaz web donde podrás ver los experimentos, métricas y modelos registrados.

---

## 📌 Mejoras Futuras
🔹 Soporte para más modelos de clasificación.  
🔹 Implementación de validación cruzada.  
🔹 Optimización automática de hiperparámetros.  

---

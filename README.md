# ml-deploy-hub
Repositorio de proyectos de Machine Learning en Databricks y MLflow, con promoción automatizada de modelos desde develop a master mediante Azure Pipelines. Este es un proceso inicial que se optimizará y evolucionará con el tiempo.

---

# **Gestión de Entornos en Continuous Model Deployment (CMD)**

El proyecto **Continuous Model Deployment (CMD)** utiliza dos entornos principales para gestionar el ciclo de vida de los modelos de machine learning:

1. **Entorno `develop`** (Desarrollo y Validación)
2. **Entorno `master`** (Producción)

Estos entornos permiten controlar la evolución de los modelos, asegurando calidad antes de ser desplegados en producción.

---

## **1. Entorno `develop` (Desarrollo y Validación)**

### **Propósito:**
- Proporciona un espacio seguro para la experimentación de nuevos modelos.
- Permite entrenar, registrar y evaluar modelos sin afectar producción.
- Incluye pruebas automatizadas para validar métricas antes de promover un modelo.

### **Flujo en `develop`**
✅ Entrenamiento y registro de modelos en **MLflow Model Registry** con la etiqueta `staging=dev`.

✅ Validación automática con métricas de desempeño (ej. precisión, recall, latencia).

✅ Si un modelo supera los umbrales definidos, se aprueba para ser promovido a producción.

### **Recursos Asociados**
- **Infraestructura:** Máquinas virtuales, Databricks.
- **Almacenamiento:** Unity Catalog Databricks  para datos y modelos temporales.
- **Monitorización:** Logs de experimentos, métricas de evaluación.

---

## **2. Entorno `master` (Producción)**

### **Propósito:**
- Asegurar que solo los modelos validados sean utilizados en producción.
- Mantener alta disponibilidad y escalabilidad para servir predicciones.
- Monitorear el rendimiento y detectar posibles degradaciones.

### **Flujo en `master`**
✅ Un modelo aprobado en `develop` se mueve a `prod` en **MLflow Model Registry**.

### **Recursos Asociados**
- **Infraestructura:** Servidores optimizados para inferencia.
- **Almacenamiento:** Modelos optimizados y versionados en un repositorio central.
- **Monitorización:** Herramientas Azure Monitor.

---

## **Resumen del Ciclo de Vida**

| **Fase**      | **Entorno `develop`** | **Entorno `master`** |
|--------------|----------------------|----------------------|
| **Propósito** | Entrenamiento y validación | Despliegue en producción |
| **Registro** | MLflow Registry (`staging=dev`) | MLflow Registry (`staging=prod`) |
| **Validaciones** | Pruebas de métricas y rendimiento | Monitoreo en tiempo real |
| **Despliegue** | No expuesto al público | API de inferencia activa |
| **Monitoreo** | Logs de experimentación | Trazabilidad en producción |

---

## **Conclusión**
El uso de los entornos `develop` y `master` en **CMD** permite que los modelos sean probados rigurosamente antes de llegar a producción. Esto garantiza **calidad, seguridad y escalabilidad**, minimizando riesgos y maximizando el valor de los modelos en producción.


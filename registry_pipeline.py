import time
import os
import requests
import json

USER_MAIL = "alepalroj@"
DATABRICKS_HOST = "https://adb-x.x.azuredatabricks.net"
DATABRICKS_TOKEN = "dapix-x" 
HEADERS = {"Authorization": f"Bearer {DATABRICKS_TOKEN}", "Content-Type": "application/json"}
RUTA_ORIGEN = f"/Workspace/Users/{USER_MAIL}/SPD_DATAR_ML_HUB/registry"
RUTA_DESTINO = f"/Workspace/Users/{USER_MAIL}/registry"
RUTA_NOTEBOOK = RUTA_DESTINO
NOMBRE_TRABAJO = "MLOps-Job"
URL_COPIAR = f"{DATABRICKS_HOST}/api/2.0/dbfs/copy"
URL_EXPORT = f"{DATABRICKS_HOST}/api/2.0/workspace/export"
URL_IMPORT = f"{DATABRICKS_HOST}/api/2.0/workspace/import"
URL_ESTADO_NOTEBOOK = f"{DATABRICKS_HOST}/api/2.0/workspace/get-status"
URL_PERMISOS = f"{DATABRICKS_HOST}/api/2.0/permissions/notebooks"
URL_CREAR_TRABAJO = f"{DATABRICKS_HOST}/api/2.0/jobs/create"
URL_EJECUTAR_TRABAJO = f"{DATABRICKS_HOST}/api/2.0/jobs/run-now"
URL_ESTADO_TRABAJO = f"{DATABRICKS_HOST}/api/2.0/jobs/runs/get"
URL_ELIMINAR_TRABAJO = f"{DATABRICKS_HOST}/api/2.0/jobs/delete"
USUARIO_PERMISO = f"{USER_MAIL}"
SPARK_VER = "15.4.x-cpu-ml-scala2.12"
PERMISSION_LEVEL = "CAN_RUN"
NODE_TYPE = "Standard_F16"
NUM_WORKERS = 1
STATES = ["TERMINATED", "SUCCESS", "SKIPPED", "INTERNAL_ERROR", "FAILED"]
SLEEP = 30

def importar_exportar_archivo():
    download_response = requests.get(URL_EXPORT, headers=HEADERS, params={ "path": RUTA_ORIGEN, "format": "SOURCE" })
    if download_response.status_code == 200:
        notebook_content = download_response.json()["content"]
        print("Archivo descargado con éxito.")
    else:
        print(f"Error al descargar el archivo: {download_response.text}")
        exit()
    upload_response = requests.post(URL_IMPORT, headers=HEADERS, json= {"path": RUTA_DESTINO,"format": "SOURCE", "overwrite": True, "language": "PYTHON", "content": notebook_content})
    if upload_response.status_code == 200:
        print("Archivo copiado exitosamente en el nuevo destino.")
    else:
        print(f"Error al subir el archivo: {upload_response.text}")

def copiar_archivo():
    respuesta = requests.post(URL_COPIAR, headers=HEADERS, json={
        "source_path": RUTA_ORIGEN,
        "destination_path": RUTA_DESTINO
    })
    if respuesta.status_code == 200:
        print("Archivo copiado con éxito.")
    else:
        print(f"Error al copiar el archivo: {respuesta.text}")

def obtener_id_notebook():
    respuesta = requests.get(URL_ESTADO_NOTEBOOK, headers=HEADERS, params={"path": RUTA_NOTEBOOK})
    if respuesta.status_code == 200:
        id_notebook = respuesta.json().get("object_id")
        print(f"ID del Notebook: {id_notebook}")
        return id_notebook
    else:
        print(f"Error al obtener el ID del notebook: {respuesta.text}")
        return None

def actualizar_permisos(id_notebook):
    url_permisos_notebook = f"{URL_PERMISOS}/{id_notebook}"
    datos_permisos = {
        "access_control_list": [
            {"user_name": USUARIO_PERMISO, "permission_level": PERMISSION_LEVEL}
        ]
    }
    respuesta = requests.put(url_permisos_notebook, headers=HEADERS, json=datos_permisos)
    if respuesta.status_code == 200:
        print("Permisos actualizados correctamente.")
    else:
        print(f"Error al asignar permisos: {respuesta.text}")

def esperar_finalizacion_trabajo(id_ejecucion):
    while True:
        respuesta = requests.get(URL_ESTADO_TRABAJO, headers=HEADERS, params={"run_id": id_ejecucion})
        if respuesta.status_code == 200:
            estado = respuesta.json().get("state", {}).get("life_cycle_state")
            print(f"Estado del trabajo: {estado}")
            if estado in STATES:
                return True
        else:
            print(f"Error al obtener el estado del trabajo: {respuesta.text}")
            return False
        time.sleep(SLEEP)

def eliminar_trabajo(id_trabajo):
    respuesta = requests.post(URL_ELIMINAR_TRABAJO, headers=HEADERS, json={"job_id": id_trabajo})
    if respuesta.status_code == 200:
        print(f"Trabajo {id_trabajo} eliminado correctamente.")
    else:
        print(f"Error al eliminar el trabajo: {respuesta.text}")

def crear_y_ejecutar_trabajo():
    configuracion_trabajo = {
    "name": NOMBRE_TRABAJO,
    "new_cluster": {
        "spark_version": SPARK_VER,
        "node_type_id": NODE_TYPE,
        "num_workers": NUM_WORKERS
    },
    "notebook_task": {
        "notebook_path": f"{RUTA_NOTEBOOK}"
    }}
    respuesta_crear = requests.post(URL_CREAR_TRABAJO, headers=HEADERS, json=configuracion_trabajo)
    if respuesta_crear.status_code == 200:
        id_trabajo = respuesta_crear.json().get("job_id")
        print(f"Trabajo creado con ID: {id_trabajo}")
        respuesta_ejecutar = requests.post(URL_EJECUTAR_TRABAJO, headers=HEADERS, json={"job_id": id_trabajo})
        if respuesta_ejecutar.status_code == 200:
            id_ejecucion = respuesta_ejecutar.json().get("run_id")
            print(f"Trabajo iniciado con ID de ejecución: {id_ejecucion}")
            if esperar_finalizacion_trabajo(id_ejecucion):
                eliminar_trabajo(id_trabajo)
            else:
                print("No elimina trabajo")
        else:
            print(f"Error al iniciar el trabajo: {respuesta_ejecutar.text}")
    else:
        print(f"Error al crear el trabajo: {respuesta_crear.text}")

importar_exportar_archivo()
id_notebook = obtener_id_notebook()
if id_notebook:
    actualizar_permisos(id_notebook)
    crear_y_ejecutar_trabajo()

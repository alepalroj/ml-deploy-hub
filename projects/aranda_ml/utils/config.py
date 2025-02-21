import yaml
import os

class Config:

    def __init__(self, filepath="config/base.yaml"):
        self.filepath = filepath
        self.params = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"El archivo de configuración '{self.filepath}' no se encuentra.")

        with open(self.filepath, "r") as file:
            try:
                config = yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Error al analizar el archivo YAML: {e}")

        if "aranda" not in config:
            raise KeyError("La clave 'aranda' no está presente en base.yaml.")

        return config["aranda"]

    def get(self, key, default=None):
        return self.params.get(key, default)

    def __getitem__(self, key):
        return self.params[key]

config = Config()
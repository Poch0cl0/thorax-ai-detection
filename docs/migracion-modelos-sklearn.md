# Migración de modelos: PySpark ML → scikit-learn (.joblib)

El sistema ya no usa PySpark. Los modelos deben exportarse desde Google Colab
en formato scikit-learn y copiarse a la carpeta `models/` del proyecto.

---

## Paso 1: Exportar los modelos desde Google Colab

Abre tu notebook de entrenamiento en Colab y agrega las siguientes celdas
**después** del entrenamiento de cada modelo.

### Instalar joblib (ya incluido en scikit-learn)

```python
# joblib viene incluido con scikit-learn, no requiere instalación extra
import joblib
```

### Exportar Logistic Regression

```python
# Asegúrate de que lr_model es tu objeto LogisticRegression entrenado
joblib.dump(lr_model, 'modelo_lr.joblib')
print("Modelo LR exportado como modelo_lr.joblib")
```

### Exportar Random Forest

```python
# Asegúrate de que rf_model es tu objeto RandomForestClassifier entrenado
joblib.dump(rf_model, 'modelo_rf.joblib')
print("Modelo RF exportado como modelo_rf.joblib")
```

### Descargar los archivos desde Colab

```python
from google.colab import files
files.download('modelo_lr.joblib')
files.download('modelo_rf.joblib')
```

---

## Paso 2: Copiar los archivos al proyecto

Coloca los archivos `.joblib` descargados en la carpeta `models/` del proyecto:

```
thorax-ai-detection/
└── models/
    ├── modelo_lr.joblib   ← aquí
    └── modelo_rf.joblib   ← aquí
```

---

## Paso 3: Verificar el pipeline de preprocesamiento

El sistema usa exactamente el mismo pipeline de preprocesamiento que en Colab:

1. Imagen → escala de grises
2. Resize a 64×64 píxeles
3. Normalizar valores a [0.0, 1.0]
4. Aplanar a vector de 4096 features

**Importante:** los modelos exportados deben haber sido entrenados con este
mismo pipeline (imágenes 64×64 aplanadas y normalizadas). Si en Colab usaste
un tamaño diferente, ajusta `IMAGE_SIZE` en `.env` o `config.py`.

---

## Paso 4: Verificar que el modelo tiene `predict_proba`

El sistema llama a `model.predict_proba(X)`. Asegúrate de que:

- `LogisticRegression` fue entrenado normalmente (soporta `predict_proba` por defecto)
- `RandomForestClassifier` fue entrenado normalmente (soporta `predict_proba` por defecto)

Si usaste un pipeline de scikit-learn (`Pipeline`), también funciona siempre
que el estimador final tenga `predict_proba`.

---

## Modo stub (sin modelos)

Si los archivos `.joblib` no existen en la ruta configurada, el sistema
opera en **modo stub**: las predicciones son simuladas de forma determinista
según el UID del estudio. El resto del sistema (login, pacientes, citas,
estudios) funciona con total normalidad.

Puedes confirmar el estado de los modelos en el endpoint:

```
GET /api/v1/scan/models
```

Respuesta cuando no hay modelos cargados:
```json
{
  "available_models": [],
  "model_options": []
}
```

---

## Variables de entorno relevantes

```bash
LR_MODEL_PATH=models/modelo_lr.joblib
RF_MODEL_PATH=models/modelo_rf.joblib
MODEL_VERSION=sklearn-1.0.0
INFERENCE_TIMEOUT_SECONDS=30
```

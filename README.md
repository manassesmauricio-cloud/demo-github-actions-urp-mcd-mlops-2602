# GitHub Actions desde la consola - URP MCD MLOps 2602

![CI](https://github.com/manassesmauricio-cloud/demo-github-actions-urp-mcd-mlops-2602/actions/workflows/ci.yml/badge.svg)

Ejercicio mínimo de integración continua (CI): cada `git push` corre las pruebas de una función de PSI en un servidor de GitHub. Todo se hace desde la terminal (Git Bash en Windows).

## Qué hay en el repo

| Archivo | Para qué |
|---|---|
| `psi.py` | Calcula el PSI entre una muestra de referencia y una actual, y devuelve OK / WARN / ALARM |
| `test_psi.py` | Dos pruebas: misma distribución da OK, un corrimiento fuerte da ALARM |
| `requirements.txt` | numpy y pytest |
| `.github/workflows/ci.yml` | El workflow: en cada push instala Python 3.11 y corre `pytest` |

## Requisitos

- Git y Python 3.10 o más.
- GitHub CLI (`gh`) con sesión iniciada: `gh auth login`.

## Paso a paso

**1. Crear la carpeta y el repositorio local**

```bash
mkdir demo-actions && cd demo-actions
git init -b main
```

**2. Escribir el código y su prueba**

```bash
cat > psi.py <<'EOF'
import numpy as np

def psi(referencia, actual, cortes=10):
    bordes = np.percentile(referencia, np.linspace(0, 100, cortes + 1))
    bordes[0], bordes[-1] = -np.inf, np.inf
    ref = np.histogram(referencia, bordes)[0] / len(referencia)
    act = np.histogram(actual, bordes)[0] / len(actual)
    ref, act = np.clip(ref, 1e-6, None), np.clip(act, 1e-6, None)
    return float(np.sum((act - ref) * np.log(act / ref)))

def semaforo(valor):
    if valor < 0.10:
        return "OK"
    if valor < 0.25:
        return "WARN"
    return "ALARM"
EOF

cat > test_psi.py <<'EOF'
import numpy as np
from psi import psi, semaforo

rng = np.random.default_rng(0)

def test_misma_distribucion_da_ok():
    ref, act = rng.normal(0, 1, 10_000), rng.normal(0, 1, 10_000)
    assert semaforo(psi(ref, act)) == "OK"

def test_corrimiento_fuerte_da_alarm():
    ref, act = rng.normal(0, 1, 10_000), rng.normal(1.5, 1, 10_000)
    assert semaforo(psi(ref, act)) == "ALARM"
EOF

printf 'numpy\npytest\n' > requirements.txt
```

**3. Probar en local antes de subir**

```bash
pip install -r requirements.txt
pytest -v
```

**4. Escribir el workflow**

GitHub busca los workflows en `.github/workflows/`.

```bash
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: CI

on: [push, workflow_dispatch]

jobs:
  pruebas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -v
EOF
```

Cómo se lee:
- `on`: cuándo corre (cada push, o a mano con `workflow_dispatch`).
- `jobs` -> `pruebas`: un trabajo que corre en una máquina Linux limpia (`ubuntu-latest`).
- `steps`: descarga el código, instala Python, instala las dependencias y corre las pruebas. Si un paso falla, el run queda en rojo.

**5. Crear el repo en GitHub y subir**

```bash
git add .
git commit -m "feat: psi con pruebas y CI"
gh repo create demo-actions --public --source=. --push
```

**6. Ver el run desde la consola**

```bash
gh run list            # lista los runs
gh run watch           # sigue el último en vivo
gh run view --log      # muestra el log completo
```

También se ve en la pestaña **Actions** del repo.

**7. Romperlo a propósito**

Cambiar el umbral de ALARM de `0.25` a `5` en `psi.py`, subir y ver el run en rojo:

```bash
sed -i 's/valor < 0.25/valor < 5/' psi.py
git commit -am "cambio de umbral"
git push
gh run watch           # falla test_corrimiento_fuerte_da_alarm
```

Volver al umbral correcto y subir de nuevo: el run vuelve a verde.

```bash
sed -i 's/valor < 5/valor < 0.25/' psi.py
git commit -am "fix: umbral de ALARM en 0.25"
git push
```

**8. Publicar con GitHub Pages (CD)**

El workflow tiene un segundo job, `publicar`, que corre solo si `pruebas` pasó y solo en `main`. Toma la página de `site/index.html`, le agrega el commit y la fecha, y la despliega en:

https://manassesmauricio-cloud.github.io/demo-github-actions-urp-mcd-mlops-2602/

Activar Pages una sola vez (desde la consola):

```bash
gh api -X POST repos/<usuario>/<repo>/pages -f build_type=workflow
```

Para cambiar lo publicado, edita `site/index.html` y sube:

```bash
git commit -am "docs: nuevo aviso en la página"
git push
gh run watch           # pruebas -> publicar
```

Si las pruebas fallan (paso 7), `publicar` no corre y queda en línea la última versión buena.

## Qué demuestra

- Una regla de negocio (el umbral del semáforo) queda protegida por una prueba: si alguien la cambia sin querer, el CI lo avisa antes de que llegue a producción.
- El CI corre en una máquina limpia, así que también detecta dependencias que faltan en `requirements.txt`.

## Siguiente nivel

El repo [pipeline-inferencia-monitoreo-urp-mcd-mlops-2602](https://github.com/manassesmauricio-cloud/pipeline-inferencia-monitoreo-urp-mcd-mlops-2602) aplica lo mismo a un pipeline real: pruebas del PSI y del posprocesamiento, construcción de la imagen Docker y validación de que los DAG de Airflow cargan.

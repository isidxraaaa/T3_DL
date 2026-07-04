import os
import re
import json

os.environ["MPLBACKEND"] = "Agg"

import matplotlib
matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt


# =========================
# Configuración de carpetas
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RESULTS_DIR = os.path.join(BASE_DIR, "results")
ANALYSIS_DIR = os.path.join(BASE_DIR, "analysis")

os.makedirs(ANALYSIS_DIR, exist_ok=True)

modelos_esperados = [
    "llama3.2:1b",
    "phi3:mini",
    "mistral:latest"
]

cantidades_esperadas = [10, 20, 50]

sentimientos_esperados = [
    "POSITIVO",
    "NEUTRO",
    "NEGATIVO"
]


# =========================
# Funciones auxiliares
# =========================

def prompt_corto(prompt_id):
    prompt_id = str(prompt_id)

    if "electronicos" in prompt_id:
        return "Electrónicos"
    if "belleza" in prompt_id:
        return "Belleza"
    if "hogar" in prompt_id:
        return "Hogar"

    return prompt_id


def contar_palabras(texto):
    if not isinstance(texto, str):
        return 0
    return len(texto.split())


def guardar_grafico(nombre):
    ruta = os.path.join(ANALYSIS_DIR, nombre)
    plt.tight_layout()
    plt.savefig(ruta, dpi=300)
    plt.close()
    print("Gráfico guardado:", ruta)


def normalizar_modelo(nombre_modelo_archivo):
    if nombre_modelo_archivo == "llama3.2_1b":
        return "llama3.2:1b"
    if nombre_modelo_archivo == "phi3_mini":
        return "phi3:mini"
    if nombre_modelo_archivo == "mistral_latest":
        return "mistral:latest"

    return nombre_modelo_archivo


def obtener_info_desde_nombre_archivo(nombre_archivo):
    """
    Extrae modelo, prompt y cantidad desde archivos como:
    llama3.2_1b_prompt_1_electronicos_10gen.txt
    phi3_mini_prompt_2_belleza_20gen.txt
    mistral_latest_prompt_3_hogar_50gen.txt
    """

    patron = r"(.+)_(prompt_\d+_[a-zA-Z]+)_(\d+)gen\.txt$"
    match = re.match(patron, nombre_archivo)

    if not match:
        return None

    modelo_archivo = match.group(1)
    prompt_id = match.group(2)
    cantidad = int(match.group(3))

    return {
        "modelo": normalizar_modelo(modelo_archivo),
        "prompt_id": prompt_id,
        "cantidad_solicitada": cantidad
    }


def limpiar_markdown(texto):
    texto = texto.strip()

    texto = texto.replace("```json", "")
    texto = texto.replace("```JSON", "")
    texto = texto.replace("```", "")

    return texto.strip()


def reparar_texto_json(texto):
    """
    Repara errores típicos vistos en las respuestas de phi3.
    """

    texto = limpiar_markdown(texto)

    # Normalizar nombres de campos
    texto = texto.replace('"reseña"', '"resena"')
    texto = texto.replace('"sentimento"', '"sentimiento"')
    texto = texto.replace('"id0"', '"id"')
    texto = texto.replace('"id01"', '"id"')

    # Repara casos tipo: "sentimiento":NEUTRO
    texto = re.sub(
        r'"sentimiento"\s*:\s*(POSITIVO|NEUTRO|NEGATIVO)',
        r'"sentimiento": "\1"',
        texto
    )

    # Repara casos tipo: "sentimento":NEUTRO
    texto = re.sub(
        r'"sentimento"\s*:\s*(POSITIVO|NEUTRO|NEGATIVO)',
        r'"sentimiento": "\1"',
        texto
    )

    # Repara casos muy rotos tipo: { "id01, "producto": ...
    texto = re.sub(
        r'\{\s*"id[^"]*,\s*"producto"',
        r'{ "producto"',
        texto
    )

    # Eliminar comas sobrantes antes de cerrar objetos
    texto = re.sub(r",\s*}", "}", texto)

    return texto


def extraer_bloque_json(texto):
    """
    Extrae desde el primer [ hasta el último ].
    """

    texto = reparar_texto_json(texto)

    inicio = texto.find("[")
    fin = texto.rfind("]")

    if inicio != -1 and fin != -1 and fin > inicio:
        return texto[inicio:fin + 1]

    return texto


def extraer_objetos_por_regex(texto):
    """
    Extrae objetos individuales {...}.
    Sirve cuando el arreglo completo está malo, pero algunos objetos sí se pueden rescatar.
    """

    texto = reparar_texto_json(texto)
    objetos = re.findall(r"\{[^{}]*\}", texto, flags=re.DOTALL)

    return objetos


def convertir_respuesta_a_lista(texto):
    """
    Intenta:
    1. Leer JSON completo.
    2. Reparar JSON completo.
    3. Extraer objetos individuales.
    """

    texto_bloque = extraer_bloque_json(texto)

    # Intento 1: JSON completo
    try:
        datos = json.loads(texto_bloque)

        if isinstance(datos, list):
            return datos, "json_completo"

    except json.JSONDecodeError:
        pass

    # Intento 2: objetos individuales
    objetos_texto = extraer_objetos_por_regex(texto_bloque)

    datos_recuperados = []

    for objeto_texto in objetos_texto:
        objeto_reparado = reparar_texto_json(objeto_texto)

        try:
            objeto = json.loads(objeto_reparado)

            if isinstance(objeto, dict):
                datos_recuperados.append(objeto)

        except json.JSONDecodeError:
            pass

    if len(datos_recuperados) > 0:
        return datos_recuperados, "json_reparado_por_objetos"

    return [], "no_recuperable"


def normalizar_ejemplo(ejemplo, info_archivo, archivo_origen, numero_fila, metodo):
    if not isinstance(ejemplo, dict):
        return None

    resena = ejemplo.get("resena", ejemplo.get("reseña", ""))
    sentimiento = ejemplo.get("sentimiento", ejemplo.get("sentimento", ""))

    producto = ejemplo.get("producto", "")
    categoria = ejemplo.get("categoria", "")

    if not isinstance(resena, str) or resena.strip() == "":
        return None

    if not isinstance(producto, str):
        producto = str(producto)

    if not isinstance(categoria, str):
        categoria = str(categoria)

    sentimiento = str(sentimiento).strip().upper()

    if sentimiento not in sentimientos_esperados:
        sentimiento = "NO_IDENTIFICADO"

    fila = {
        "cantidad_solicitada": info_archivo["cantidad_solicitada"],
        "n_solicitado": info_archivo["cantidad_solicitada"],
        "modelo": info_archivo["modelo"],
        "prompt_id": info_archivo["prompt_id"],
        "prompt_corto": prompt_corto(info_archivo["prompt_id"]),
        "id": ejemplo.get("id", numero_fila),
        "producto": producto.strip(),
        "categoria": categoria.strip(),
        "resena": resena.strip(),
        "sentimiento": sentimiento,
        "largo_palabras": contar_palabras(resena),
        "archivo_origen": archivo_origen,
        "metodo_extraccion": metodo
    }

    return fila


def cargar_datos_desde_txt():
    filas_dataset = []
    filas_resumen = []

    archivos_txt = [
        archivo for archivo in os.listdir(RESULTS_DIR)
        if archivo.endswith(".txt") and re.search(r"_(10|20|50)gen\.txt$", archivo)
    ]

    if len(archivos_txt) == 0:
        raise FileNotFoundError("No se encontraron archivos TXT con _10gen, _20gen o _50gen en results.")

    for archivo in archivos_txt:
        info = obtener_info_desde_nombre_archivo(archivo)

        if info is None:
            continue

        ruta_archivo = os.path.join(RESULTS_DIR, archivo)

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            texto = f.read()

        datos, metodo = convertir_respuesta_a_lista(texto)

        recuperados_archivo = 0

        for i, ejemplo in enumerate(datos, start=1):
            fila = normalizar_ejemplo(
                ejemplo=ejemplo,
                info_archivo=info,
                archivo_origen=os.path.join("results", archivo),
                numero_fila=i,
                metodo=metodo
            )

            if fila is not None:
                filas_dataset.append(fila)
                recuperados_archivo += 1

        filas_resumen.append({
            "archivo": archivo,
            "modelo": info["modelo"],
            "prompt_id": info["prompt_id"],
            "prompt_corto": prompt_corto(info["prompt_id"]),
            "cantidad_solicitada": info["cantidad_solicitada"],
            "ejemplos_recuperados": recuperados_archivo,
            "metodo_extraccion": metodo
        })

    df = pd.DataFrame(filas_dataset)
    resumen_archivos = pd.DataFrame(filas_resumen)

    if len(df) == 0:
        raise ValueError("No se pudo recuperar ningún ejemplo desde los TXT.")

    df["n_solicitado"] = pd.to_numeric(df["n_solicitado"], errors="coerce").astype("Int64")
    df["largo_palabras"] = pd.to_numeric(df["largo_palabras"], errors="coerce")
    df["modelo"] = df["modelo"].astype(str).str.strip()
    df["prompt_id"] = df["prompt_id"].astype(str).str.strip()
    df["sentimiento"] = df["sentimiento"].astype(str).str.strip().str.upper()

    return df, resumen_archivos


# =========================
# Cargar datos desde TXT
# =========================

df, resumen_archivos = cargar_datos_desde_txt()

print("=" * 70)
print("Dataset reconstruido desde archivos TXT.")
print("Total de ejemplos recuperados:", len(df))
print("=" * 70)

df.to_csv(
    os.path.join(ANALYSIS_DIR, "dataset_reparado_desde_txt_10_20_50.csv"),
    index=False,
    encoding="utf-8-sig"
)

resumen_archivos.to_csv(
    os.path.join(ANALYSIS_DIR, "resumen_recuperacion_archivos_txt.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("Dataset reparado guardado en: analysis/dataset_reparado_desde_txt_10_20_50.csv")
print("Resumen de recuperación guardado en: analysis/resumen_recuperacion_archivos_txt.csv")


# =========================
# 1. Cantidad de ejemplos recuperados por modelo
# =========================

tabla_validos_modelo = (
    df.groupby(["n_solicitado", "modelo"])
    .size()
    .unstack(fill_value=0)
    .reindex(index=cantidades_esperadas, columns=modelos_esperados, fill_value=0)
)

tabla_validos_modelo.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_01_ejemplos_validos_por_modelo.csv"),
    encoding="utf-8-sig"
)

tabla_validos_modelo.plot(kind="bar", figsize=(8, 5))
plt.title("Cantidad de ejemplos recuperados por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Ejemplos recuperados")
plt.xticks(rotation=0)
guardar_grafico("01_ejemplos_validos_por_modelo.png")


# =========================
# 2. Ejemplos recuperados por modelo y prompt
# =========================

for n in cantidades_esperadas:
    df_n = df[df["n_solicitado"] == n]

    tabla_modelo_prompt = (
        df_n.groupby(["modelo", "prompt_corto"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=modelos_esperados,
            columns=["Electrónicos", "Belleza", "Hogar"],
            fill_value=0
        )
    )

    tabla_modelo_prompt.to_csv(
        os.path.join(ANALYSIS_DIR, f"tabla_02_ejemplos_validos_por_modelo_y_prompt_{n}gen.csv"),
        encoding="utf-8-sig"
    )

    tabla_modelo_prompt.plot(kind="bar", figsize=(9, 5))
    plt.title(f"Ejemplos recuperados por modelo y prompt ({n} solicitados)")
    plt.xlabel("Modelo")
    plt.ylabel("Ejemplos recuperados")
    plt.xticks(rotation=20, ha="right")
    guardar_grafico(f"02_ejemplos_validos_por_modelo_y_prompt_{n}gen.png")


# =========================
# 3. Distribución de sentimientos por modelo
# =========================

sentimientos_para_grafico = [
    "POSITIVO",
    "NEUTRO",
    "NEGATIVO",
    "NO_IDENTIFICADO"
]

for n in cantidades_esperadas:
    df_n = df[df["n_solicitado"] == n]

    tabla_sentimientos = (
        df_n.groupby(["modelo", "sentimiento"])
        .size()
        .unstack(fill_value=0)
        .reindex(
            index=modelos_esperados,
            columns=sentimientos_para_grafico,
            fill_value=0
        )
    )

    tabla_sentimientos.to_csv(
        os.path.join(ANALYSIS_DIR, f"tabla_03_distribucion_sentimientos_{n}gen.csv"),
        encoding="utf-8-sig"
    )

    tabla_sentimientos.plot(kind="bar", figsize=(9, 5))
    plt.title(f"Distribución de sentimientos por modelo ({n} solicitados)")
    plt.xlabel("Modelo")
    plt.ylabel("Cantidad de reseñas")
    plt.xticks(rotation=20, ha="right")
    guardar_grafico(f"03_distribucion_sentimientos_{n}gen.png")


# =========================
# 4. Largo promedio de reseñas por modelo
# =========================

tabla_largo_promedio = (
    df.groupby(["n_solicitado", "modelo"])["largo_palabras"]
    .mean()
    .unstack()
    .reindex(index=cantidades_esperadas, columns=modelos_esperados)
)

tabla_largo_promedio.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_04_largo_promedio_por_modelo.csv"),
    encoding="utf-8-sig"
)

tabla_largo_promedio.plot(kind="bar", figsize=(8, 5))
plt.title("Largo promedio de reseñas por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Promedio de palabras")
plt.xticks(rotation=0)
guardar_grafico("04_largo_promedio_por_modelo.png")


# =========================
# 5. Ejemplos faltantes por modelo
# =========================

resumen_archivos["ejemplos_esperados"] = resumen_archivos["cantidad_solicitada"]
resumen_archivos["ejemplos_faltantes"] = (
    resumen_archivos["ejemplos_esperados"] - resumen_archivos["ejemplos_recuperados"]
)

resumen_archivos["ejemplos_faltantes"] = resumen_archivos["ejemplos_faltantes"].clip(lower=0)

tabla_faltantes = (
    resumen_archivos.groupby(["cantidad_solicitada", "modelo"])["ejemplos_faltantes"]
    .sum()
    .unstack(fill_value=0)
    .reindex(index=cantidades_esperadas, columns=modelos_esperados, fill_value=0)
)

tabla_faltantes.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_05_ejemplos_faltantes_por_modelo.csv"),
    encoding="utf-8-sig"
)

tabla_faltantes.plot(kind="bar", figsize=(8, 5))
plt.title("Ejemplos faltantes por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Ejemplos faltantes")
plt.xticks(rotation=0)
guardar_grafico("05_ejemplos_faltantes_por_modelo.png")


# =========================
# 6. Resumen de métricas
# =========================

resumen = (
    df.groupby(["n_solicitado", "modelo"])
    .agg(
        ejemplos_recuperados=("modelo", "size"),
        largo_promedio=("largo_palabras", "mean"),
        largo_minimo=("largo_palabras", "min"),
        largo_maximo=("largo_palabras", "max")
    )
    .reset_index()
)

# Cada modelo tiene 3 prompts
resumen["ejemplos_esperados"] = resumen["n_solicitado"] * 3

resumen["ejemplos_faltantes"] = (
    resumen["ejemplos_esperados"] - resumen["ejemplos_recuperados"]
)

resumen["ejemplos_faltantes"] = resumen["ejemplos_faltantes"].clip(lower=0)

resumen["porcentaje_recuperado"] = (
    resumen["ejemplos_recuperados"] / resumen["ejemplos_esperados"] * 100
)

resumen.to_csv(
    os.path.join(ANALYSIS_DIR, "resumen_metricas_10_20_50.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("=" * 70)
print("Análisis completado.")
print("Gráficos y tablas guardados en la carpeta:", ANALYSIS_DIR)
print("=" * 70)
print(resumen)
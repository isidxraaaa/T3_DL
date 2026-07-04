import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Configuración
# =========================

RESULTS_DIR = "results2"
ANALYSIS_DIR = "analysis2"

os.makedirs(ANALYSIS_DIR, exist_ok=True)

dataset_files = {
    10: os.path.join(RESULTS_DIR, "dataset_final_10gen_reparado.csv"),
    20: os.path.join(RESULTS_DIR, "dataset_final_20gen_reparado.csv"),
    50: os.path.join(RESULTS_DIR, "dataset_final_50gen_reparado.csv"),
}

error_files = {
    10: os.path.join(RESULTS_DIR, "errores_generacion_10gen_reparado.csv"),
    20: os.path.join(RESULTS_DIR, "errores_generacion_20gen_reparado.csv"),
    50: os.path.join(RESULTS_DIR, "errores_generacion_50gen_reparado.csv"),
}

modelos_esperados = ["llama3.2:1b", "phi3:mini", "mistral:latest"]
prompts_esperados = [
    "prompt_1_electronicos",
    "prompt_2_belleza",
    "prompt_3_hogar"
]

def prompt_corto(prompt_id):
    if "electronicos" in str(prompt_id):
        return "Electrónicos"
    if "belleza" in str(prompt_id):
        return "Belleza"
    if "hogar" in str(prompt_id) or "cocina" in str(prompt_id):
        return "Cocina"
    return str(prompt_id)


def guardar_grafico(nombre):
    plt.tight_layout()
    plt.savefig(os.path.join(ANALYSIS_DIR, nombre), dpi=300)
    plt.close()


def cargar_datasets():
    dataframes = []

    for n, path in dataset_files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()

            df["n_solicitado"] = n

            # Normalizar columnas
            df["modelo"] = df["modelo"].astype(str).str.strip()
            df["prompt_id"] = df["prompt_id"].astype(str).str.strip()
            df["sentimiento"] = df["sentimiento"].astype(str).str.strip().str.upper()
            df["largo_palabras"] = pd.to_numeric(df["largo_palabras"], errors="coerce")
            df["prompt_corto"] = df["prompt_id"].apply(prompt_corto)

            dataframes.append(df)
        else:
            print(f"No se encontró: {path}")

    if not dataframes:
        raise FileNotFoundError("No se encontró ningún dataset_final.")

    return pd.concat(dataframes, ignore_index=True)


def cargar_errores():
    dataframes = []

    for n, path in error_files.items():
        if os.path.exists(path):
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()

            if len(df) > 0:
                df["n_solicitado"] = n
                df["modelo"] = df["modelo"].astype(str).str.strip()
                df["prompt_id"] = df["prompt_id"].astype(str).str.strip()
                df["prompt_corto"] = df["prompt_id"].apply(prompt_corto)
                dataframes.append(df)
        else:
            print(f"No se encontró: {path}")

    if not dataframes:
        return pd.DataFrame(
            columns=["modelo", "prompt_id", "archivo_origen", "error", "n_solicitado", "prompt_corto"]
        )

    return pd.concat(dataframes, ignore_index=True)


# =========================
# Cargar datos
# =========================

df = cargar_datasets()
df_errores = cargar_errores()

print("=" * 70)
print("Dataset combinado cargado.")
print("Total de ejemplos válidos:", len(df))
print("Total de errores modelo-prompt:", len(df_errores))
print("=" * 70)

df.to_csv(
    os.path.join(ANALYSIS_DIR, "dataset_combinado_10_20_50.csv"),
    index=False,
    encoding="utf-8-sig"
)


# =========================
# Cantidad de ejemplos válidos por modelo
# =========================

tabla_validos_modelo = (
    df.groupby(["n_solicitado", "modelo"])
    .size()
    .unstack(fill_value=0)
    .reindex(index=[10, 20, 50], columns=modelos_esperados, fill_value=0)
)

tabla_validos_modelo.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_01_ejemplos_validos_por_modelo.csv"),
    encoding="utf-8-sig"
)

plt.figure(figsize=(8, 5))
tabla_validos_modelo.plot(kind="bar")
plt.title("Cantidad de ejemplos válidos por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Ejemplos válidos")
plt.xticks(rotation=0)
guardar_grafico("01_ejemplos_validos_por_modelo.png")


# =========================
# Cantidad de ejemplos válidos por modelo y prompt
# Un gráfico por cada cantidad solicitada
# =========================

for n in [10, 20, 50]:
    df_n = df[df["n_solicitado"] == n]

    tabla_modelo_prompt = (
        df_n.groupby(["modelo", "prompt_corto"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=modelos_esperados, columns=["Electrónicos", "Belleza", "Cocina"], fill_value=0)
    )

    tabla_modelo_prompt.to_csv(
        os.path.join(ANALYSIS_DIR, f"tabla_02_ejemplos_validos_por_modelo_y_prompt_{n}gen.csv"),
        encoding="utf-8-sig"
    )

    plt.figure(figsize=(9, 5))
    tabla_modelo_prompt.plot(kind="bar")
    plt.title(f"Ejemplos válidos por modelo y prompt ({n} solicitados)")
    plt.xlabel("Modelo")
    plt.ylabel("Ejemplos válidos")
    plt.xticks(rotation=20, ha="right")
    guardar_grafico(f"02_ejemplos_validos_por_modelo_y_prompt_{n}gen.png")


# =========================
# Distribución de sentimientos por modelo
# =========================

sentimientos_esperados = ["POSITIVO", "NEUTRO", "NEGATIVO"]

for n in [10, 20, 50]:
    df_n = df[df["n_solicitado"] == n]

    tabla_sentimientos = (
        df_n.groupby(["modelo", "sentimiento"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=modelos_esperados, columns=sentimientos_esperados, fill_value=0)
    )

    tabla_sentimientos.to_csv(
        os.path.join(ANALYSIS_DIR, f"tabla_03_distribucion_sentimientos_{n}gen.csv"),
        encoding="utf-8-sig"
    )

    plt.figure(figsize=(9, 5))
    tabla_sentimientos.plot(kind="bar")
    plt.title(f"Distribución de sentimientos por modelo ({n} solicitados)")
    plt.xlabel("Modelo")
    plt.ylabel("Cantidad de reseñas")
    plt.xticks(rotation=20, ha="right")
    guardar_grafico(f"03_distribucion_sentimientos_{n}gen.png")


# =========================
# Largo promedio de reseñas por modelo
# Comparando 10, 20 y 50
# =========================

tabla_largo_promedio = (
    df.groupby(["n_solicitado", "modelo"])["largo_palabras"]
    .mean()
    .unstack()
    .reindex(index=[10, 20, 50], columns=modelos_esperados)
)

tabla_largo_promedio.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_04_largo_promedio_por_modelo.csv"),
    encoding="utf-8-sig"
)

plt.figure(figsize=(8, 5))
tabla_largo_promedio.plot(kind="bar")
plt.title("Largo promedio de reseñas por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Promedio de palabras")
plt.xticks(rotation=0)
guardar_grafico("04_largo_promedio_por_modelo.png")


# =========================
#Errores de generación por modelo
#Comparando 10, 20 y 50
# =========================

if len(df_errores) > 0:
    tabla_errores = (
        df_errores.groupby(["n_solicitado", "modelo"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=[10, 20, 50], columns=modelos_esperados, fill_value=0)
    )
else:
    tabla_errores = pd.DataFrame(
        0,
        index=[10, 20, 50],
        columns=modelos_esperados
    )

tabla_errores.to_csv(
    os.path.join(ANALYSIS_DIR, "tabla_05_errores_generacion_por_modelo.csv"),
    encoding="utf-8-sig"
)

plt.figure(figsize=(8, 5))
tabla_errores.plot(kind="bar")
plt.title("Errores de generación por modelo")
plt.xlabel("Cantidad solicitada por prompt")
plt.ylabel("Errores modelo-prompt")
plt.xticks(rotation=0)
guardar_grafico("05_errores_generacion_por_modelo.png")


# =========================
#Resumen con cantidad esperada vs cantidad válida
# =========================

resumen = (
    df.groupby(["n_solicitado", "modelo"])
    .agg(
        ejemplos_validos=("id", "count"),
        largo_promedio=("largo_palabras", "mean"),
        largo_minimo=("largo_palabras", "min"),
        largo_maximo=("largo_palabras", "max")
    )
    .reset_index()
)


resumen["ejemplos_esperados"] = resumen["n_solicitado"] * 3
resumen["ejemplos_faltantes"] = resumen["ejemplos_esperados"] - resumen["ejemplos_validos"]
resumen["porcentaje_valido"] = (
    resumen["ejemplos_validos"] / resumen["ejemplos_esperados"] * 100
)

errores_resumen = (
    tabla_errores
    .rename_axis("n_solicitado")
    .reset_index()
    .melt(
        id_vars="n_solicitado",
        var_name="modelo",
        value_name="errores_generacion"
    )
)

resumen = resumen.merge(
    errores_resumen,
    on=["n_solicitado", "modelo"],
    how="left"
)

resumen["errores_generacion"] = resumen["errores_generacion"].fillna(0).astype(int)

resumen.to_csv(
    os.path.join(ANALYSIS_DIR, "resumen_metricas_10_20_50.csv"),
    index=False,
    encoding="utf-8-sig"
)

print("Análisis completado.")
print("Gráficos y tablas guardados en la carpeta:", ANALYSIS_DIR)
print("=" * 70)
print(resumen)
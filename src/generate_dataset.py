import requests
import os
import json
import csv

url = "http://localhost:11434/api/generate"

modelos = [
    "llama3.2:1b",
    "phi3:mini",
    "mistral:latest"
]

# Genera 10, 20 y 50 reseñas para cada modelo y cada prompt
cantidades = [10, 20, 50]

prompts_base = {
    "prompt_1_electronicos": "Genera {cantidad} reseñas sintéticas de productos electrónicos en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_2_belleza": "Genera {cantidad} reseñas sintéticas de productos de belleza y cuidado personal en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_3_hogar": "Genera {cantidad} reseñas sintéticas de productos para el hogar y cocina en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional."
}

# Carpeta donde se guardarán los resultados
os.makedirs("results", exist_ok=True)

# Archivos CSV finales
dataset_csv = "results/dataset_final_10_20_50gen.csv"
errores_csv = "results/errores_generacion_10_20_50gen.csv"

filas_dataset = []
filas_errores = []


def extraer_json_desde_respuesta(texto):
    """
    Intenta convertir la respuesta del modelo a JSON.
    Primero intenta leer todo el texto directamente.
    Si falla, intenta extraer desde el primer '[' hasta el último ']'.
    """
    try:
        return json.loads(texto), True, ""
    except json.JSONDecodeError as error_original:
        inicio = texto.find("[")
        fin = texto.rfind("]")

        if inicio != -1 and fin != -1 and fin > inicio:
            posible_json = texto[inicio:fin + 1]

            try:
                return json.loads(posible_json), True, ""
            except json.JSONDecodeError as error_extraido:
                return None, False, str(error_extraido)

        return None, False, str(error_original)


def contar_palabras(texto):
    if not isinstance(texto, str):
        return 0
    return len(texto.split())


for cantidad in cantidades:
    for modelo in modelos:
        for nombre_prompt, prompt_base in prompts_base.items():
            print("=" * 70)
            print("Cantidad:", cantidad)
            print("Modelo:", modelo)
            print("Prompt:", nombre_prompt)

            prompt = prompt_base.format(cantidad=cantidad)

            data = {
                "model": modelo,
                "prompt": prompt,
                "stream": False
            }

            try:
                response = requests.post(url, json=data)
            except requests.exceptions.RequestException as error_conexion:
                print("Error de conexión con Ollama:", error_conexion)

                filas_errores.append({
                    "cantidad_solicitada": cantidad,
                    "modelo": modelo,
                    "prompt_id": nombre_prompt,
                    "archivo_origen": "",
                    "error": str(error_conexion)
                })

                continue

            nombre_modelo_archivo = modelo.replace(":", "_").replace("/", "_")
            nombre_archivo = f"results/{nombre_modelo_archivo}_{nombre_prompt}_{cantidad}gen.txt"

            if response.status_code == 200:
                respuesta = response.json()["response"]

                # Guardar respuesta original en TXT
                with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                    archivo.write(respuesta)

                print("Respuesta guardada en TXT:", nombre_archivo)

                # Convertir respuesta a JSON
                datos_json, json_valido, error_json = extraer_json_desde_respuesta(respuesta)

                if json_valido and isinstance(datos_json, list):
                    for ejemplo in datos_json:
                        # Usa "resena", pero también acepta "reseña" por si el modelo lo escribe con ñ
                        resena = ejemplo.get("resena", ejemplo.get("reseña", ""))

                        fila = {
                            "cantidad_solicitada": cantidad,
                            "modelo": modelo,
                            "prompt_id": nombre_prompt,
                            "id": ejemplo.get("id", ""),
                            "producto": ejemplo.get("producto", ""),
                            "categoria": ejemplo.get("categoria", ""),
                            "resena": resena,
                            "sentimiento": ejemplo.get("sentimiento", ""),
                            "largo_palabras": contar_palabras(resena),
                            "archivo_origen": nombre_archivo
                        }

                        filas_dataset.append(fila)

                    print("JSON válido. Ejemplos agregados al dataset:", len(datos_json))

                else:
                    print("La respuesta no pudo convertirse a JSON válido.")

                    filas_errores.append({
                        "cantidad_solicitada": cantidad,
                        "modelo": modelo,
                        "prompt_id": nombre_prompt,
                        "archivo_origen": nombre_archivo,
                        "error": error_json
                    })

            else:
                print("Error con el modelo:", modelo)
                print("Código de estado:", response.status_code)
                print(response.text)

                filas_errores.append({
                    "cantidad_solicitada": cantidad,
                    "modelo": modelo,
                    "prompt_id": nombre_prompt,
                    "archivo_origen": nombre_archivo,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })


# Guardar dataset final en CSV
columnas_dataset = [
    "cantidad_solicitada",
    "modelo",
    "prompt_id",
    "id",
    "producto",
    "categoria",
    "resena",
    "sentimiento",
    "largo_palabras",
    "archivo_origen"
]

with open(dataset_csv, "w", encoding="utf-8-sig", newline="") as archivo_csv:
    writer = csv.DictWriter(archivo_csv, fieldnames=columnas_dataset)
    writer.writeheader()
    writer.writerows(filas_dataset)

print("=" * 70)
print("Dataset final guardado en:", dataset_csv)
print("Total de ejemplos guardados en CSV:", len(filas_dataset))


# Guardar errores en CSV
columnas_errores = [
    "cantidad_solicitada",
    "modelo",
    "prompt_id",
    "archivo_origen",
    "error"
]

with open(errores_csv, "w", encoding="utf-8-sig", newline="") as archivo_csv:
    writer = csv.DictWriter(archivo_csv, fieldnames=columnas_errores)
    writer.writeheader()
    writer.writerows(filas_errores)

print("Archivo de errores guardado en:", errores_csv)
print("Total de errores registrados:", len(filas_errores))
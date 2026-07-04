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

prompts = {
    "prompt_1_electronicos": "Genera 50 reseñas sintéticas de dispositivos electrónicos personales y accesorios de computación, excluyendo electrodomésticos en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, reseña, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_2_belleza": "Genera 50 reseñas sintéticas de productos de belleza, cuidado facial y cuidado capilar en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, reseña, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_3_hogar": "Genera 50 reseñas sintéticas de utensilios y artículos de cocina. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, reseña, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional."
}

os.makedirs("results2", exist_ok=True)

dataset_csv = "results2/dataset_final_50gen.csv"
errores_csv = "results2/errores_generacion_50gen.csv"

filas_dataset = []
filas_errores = []


def extraer_json_desde_respuesta(texto):
    """
    Intenta convertir la respuesta del modelo a JSON.
    Primero intenta cargar todo el texto directamente.
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


for modelo in modelos:
    for nombre_prompt, prompt in prompts.items():
        print("=" * 70)
        print("Modelo:", modelo)
        print("Prompt:", nombre_prompt)

        data = {
            "model": modelo,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=data)

        if response.status_code == 200:
            respuesta = response.json()["response"]

            nombre_modelo_archivo = modelo.replace(":", "_").replace("/", "_")
            nombre_archivo = f"results2/{nombre_modelo_archivo}_{nombre_prompt}_50gen.txt"

            # Guardar respuesta original en TXT
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(respuesta)

            print("Respuesta guardada en TXT:", nombre_archivo)

            # Intentar convertir respuesta a JSON para guardarla en CSV
            datos_json, json_valido, error_json = extraer_json_desde_respuesta(respuesta)

            if json_valido and isinstance(datos_json, list):
                for ejemplo in datos_json:
                    resena = ejemplo.get("reseña", "")

                    fila = {
                        "modelo": modelo,
                        "prompt_id": nombre_prompt,
                        "id": ejemplo.get("id", ""),
                        "producto": ejemplo.get("producto", ""),
                        "categoria": ejemplo.get("categoria", ""),
                        "reseña": resena,
                        "sentimiento": ejemplo.get("sentimiento", ""),
                        "largo_palabras": contar_palabras(resena),
                        "archivo_origen": nombre_archivo
                    }

                    filas_dataset.append(fila)

                print("JSON válido. Ejemplos agregados al CSV:", len(datos_json))

            else:
                print("La respuesta no pudo convertirse a JSON válido.")

                filas_errores.append({
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
                "modelo": modelo,
                "prompt_id": nombre_prompt,
                "archivo_origen": "",
                "error": f"HTTP {response.status_code}: {response.text}"
            })


# Guardar dataset final en CSV
columnas_dataset = [
    "modelo",
    "prompt_id",
    "id",
    "producto",
    "categoria",
    "reseña",
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
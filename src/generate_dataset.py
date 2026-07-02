import requests
import os

url = "http://localhost:11434/api/generate"

modelos = [
    "llama3.2:1b",
    "phi3:mini",
    "mistral:latest"
]

prompts = {
    "prompt_1_electronicos": "Genera 10 reseñas sintéticas de productos electrónicos en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_2_belleza": "Genera 10 reseñas sintéticas de productos de belleza y cuidado personal en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional.",
    
    "prompt_3_hogar": "Genera 10 reseñas sintéticas de productos para el hogar y cocina en español. La salida debe ser exclusivamente un arreglo JSON válido. Cada elemento debe tener los campos: id, producto, categoria, resena, sentimiento. Usa los sentimientos POSITIVO, NEUTRO o NEGATIVO. Cada reseña debe tener entre 25 y 45 palabras. No uses markdown, explicaciones ni texto adicional."
}

os.makedirs("results", exist_ok=True)

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
            nombre_archivo = f"results/{nombre_modelo_archivo}_{nombre_prompt}.txt"

            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(respuesta)

            print("Respuesta guardada en:", nombre_archivo)
        else:
            print("Error con el modelo:", modelo)
            print("Código de estado:", response.status_code)
            print(response.text)

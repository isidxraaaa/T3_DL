import requests

url = "http://localhost:11434/api/generate"

modelos = [
    "llama3.2:1b",
    "phi3:mini",
    "mistral:latest"
]

prompt = "Responde solo con la palabra OK."

for modelo in modelos:
    print("=" * 50)
    print("Probando modelo:", modelo)

    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    print("Código de estado:", response.status_code)

    if response.status_code == 200:
        respuesta = response.json()["response"]
        print("Respuesta del modelo:")
        print(respuesta)
    else:
        print("Error al consultar el modelo.")
        print(response.text)

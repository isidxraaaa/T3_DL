import requests

url = "http://localhost:11434/api/generate"

data = {
    "model": "llama3.2:1b",
    "prompt": "Responde solo con la palabra OK.",
    "stream": False
}

response = requests.post(url, json=data)

print("Código de estado:", response.status_code)
print("Respuesta del modelo:")
print(response.json()["response"])

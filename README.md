# T3 Deep Learning

Este proyecto corresponde a la Tarea 3 de Deep Learning. Para la ejecución local de modelos de lenguaje se utilizó **Ollama** en Windows mediante PowerShell.

---

## 1. Instalación de Ollama

Para instalar Ollama en Windows, abrir PowerShell y ejecutar:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Luego, verificar que la instalación se haya realizado correctamente:

```powershell
ollama --version
```

---

## 2. Descarga de modelos

Para ejecutar la tarea, se deben descargar los siguientes modelos mediante Ollama:

```powershell
ollama run llama3.2:1b
```

```powershell
ollama run phi3:mini
```

```powershell
ollama run mistral
```

Para salir de cada modelo después de la descarga o prueba, escribir:

```text
/bye
```

---

## 3. Verificación de modelos descargados

Para revisar que los modelos fueron descargados correctamente, ejecutar:

```powershell
ollama list
```

Los modelos esperados son:

* `llama3.2:1b`
* `phi3:mini`
* `mistral:latest`

---

## 4. Preparación del entorno en Visual Studio Code

Abrir el proyecto en Visual Studio Code y activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Luego, instalar las librerías necesarias:

```powershell
py -m pip install requests pandas
```

Para verificar las librerías instaladas:

```powershell
py -m pip list
```

---

## 5. Ejecución del proyecto

Una vez instalados Ollama, los modelos y las librerías de Python, ejecutar el archivo principal del proyecto desde PowerShell o la terminal de Visual Studio Code.

```powershell
py generate_dataset.py
```

---

## 6. Modelos utilizados

Para la ejecución local se utilizaron tres modelos específicos:

* `llama3.2:1b`
* `phi3:mini`
* `mistral:latest`

Estos modelos fueron seleccionados porque permiten realizar pruebas locales sin depender de Google Colab ni de servicios externos. Además, son modelos disponibles directamente desde Ollama y adecuados para comparar generación de texto en español.

---

## 7. Dependencias principales

El proyecto utiliza las siguientes librerías de Python:

* `requests`
* `pandas`

Estas dependencias permiten realizar consultas locales a Ollama y manejar los datos generados durante la ejecución.


# T3 Deep Learning

Este proyecto corresponde a la Tarea 3 de Deep Learning. Para la ejecución local de modelos de lenguaje se utilizó **Ollama** en Windows mediante PowerShell.

El objetivo inicial fue instalar y probar modelos locales capaces de generar reseñas breves de productos en español, evaluando si respetaban el idioma solicitado y las etiquetas de sentimiento esperadas.

---

## 1. Instalación de Ollama en PowerShell

Para instalar Ollama en Windows, abrir PowerShell y ejecutar:

```powershell
irm https://ollama.com/install.ps1 | iex
```

Luego, verificar que la instalación se haya realizado correctamente:

```powershell
ollama --version
```

---

## 2. Descarga y prueba de LLaMA

Se descargó y ejecutó el modelo `llama3.2:1b` con el siguiente comando:

```powershell
ollama run llama3.2:1b
```

Se eligió la versión `1b` porque corresponde a un modelo liviano, de aproximadamente 1 billón de parámetros. Esto permite ejecutarlo localmente en un computador personal sin requerir demasiados recursos de memoria ni tiempos de respuesta excesivos.

Para probar el funcionamiento del modelo, se utilizó el siguiente prompt:

```text
Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.
```

Resultado observado:

```text
LLaMA respondió en español, pero no respetó completamente las tres etiquetas solicitadas. Generó reseñas positivas y negativas, pero no incluyó una reseña neutra.
```

Para salir del modelo se utilizó:

```text
/bye
```

---

## 3. Descarga y prueba de Phi

Luego se descargó y ejecutó el modelo `phi3:mini`:

```powershell
ollama run phi3:mini
```

Este modelo también fue escogido por ser una versión compacta, adecuada para ejecución local. Además, en las pruebas iniciales respondió bien a instrucciones estructuradas.

Se utilizó nuevamente el mismo prompt de prueba:

```text
Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.
```

Resultado observado:

```text
Phi respondió en español y generó correctamente una reseña positiva, una neutra y una negativa.
```

Para salir del modelo:

```text
/bye
```

---

## 4. Descarga y prueba de Mistral

Finalmente, se descargó y ejecutó el modelo Mistral:

```powershell
ollama run mistral
```

Este modelo corresponde a una versión más pesada que las anteriores, con aproximadamente 7 billones de parámetros. Aun así, sigue siendo posible ejecutarlo localmente mediante Ollama.

Se probó con el mismo prompt:

```text
Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.
```

Resultado observado:

```text
Mistral respondió en español y generó reseñas con etiquetas positivo, neutro y positivo, pero no incluyó una reseña negativa.
```

Para salir del modelo:

```text
/bye
```

---

## 5. Verificación de modelos descargados

Después de descargar los modelos, se puede revisar la lista de modelos disponibles con:

```powershell
ollama list
```

Ejemplo de salida obtenida:

```powershell
PS C:\Users\Isidora> ollama list

NAME              ID              SIZE      MODIFIED
mistral:latest    6577803aa9a0    4.4 GB    8 minutes ago
phi3:mini         4f2222927938    2.2 GB    17 minutes ago
llama3.2:1b       baf6a787fdff    1.3 GB    28 minutes ago
```

---

## 6. Comparación inicial de modelos

| Modelo           | Observación inicial                                                                               |
| ---------------- | ------------------------------------------------------------------------------------------------- |
| `llama3.2:1b`    | Respondió en español, pero no respetó completamente las tres etiquetas de sentimiento solicitadas |
| `phi3:mini`      | Respondió en español y generó correctamente etiquetas positiva, neutra y negativa                 |
| `mistral:latest` | Respondió en español, pero repitió la etiqueta positiva y no generó una reseña negativa           |

---

## 7. Preparación del entorno en Visual Studio Code

Para trabajar el proyecto en Visual Studio Code, primero se debe activar el entorno virtual:

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

## 8. Modelos utilizados

Para la ejecución local se utilizaron tres modelos específicos:

* `llama3.2:1b`
* `phi3:mini`
* `mistral:latest`

La elección de estos modelos se hizo principalmente por factibilidad, ya que la tarea debía ejecutarse de forma local y no en Google Colab. Por esto, se priorizaron modelos que pudieran correr en un computador personal sin un consumo excesivo de memoria ni tiempos de ejecución demasiado altos.

`llama3.2:1b` fue seleccionado por ser una versión liviana de la familia LLaMA.
`phi3:mini` fue elegido por ser compacto y responder bien a instrucciones estructuradas.
`mistral:latest` fue incluido como modelo base de Mistral disponible directamente en Ollama, permitiendo comparar su comportamiento con los otros modelos.

---

## 9. Prompt base de prueba

El prompt utilizado para probar inicialmente los modelos fue:

```text
Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.
```

Este prompt permitió verificar si cada modelo era capaz de:

* responder en español
* generar reseñas breves
* respetar el formato solicitado
* usar correctamente las etiquetas de sentimiento
* diferenciar entre reseñas positivas, neutras y negativas

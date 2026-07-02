T3 DL
1. en powershell instalar ollama

irm https://ollama.com/install.ps1 | iex

ollama --versión


2. luego probamos si funciona el modelo:

ollama run llama3.2:1b 

se elige 1b para 1 billón de parámetros, mientras más grande más pesado, por eso para esta tarea utilizaremos sólo el de 1b
al ejecutar debería salir la opción de enviar un mensaje, probamos con este para ver si el modelo responde correctamente:

Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.

a mí al menos me hizo 2 positivos y 1 negativo no hizo neutro, tener en cuenta esa respuesta y para salir escribimos /bye

3. seguimos en powershell e instalaremos phi

ollama run phi3:mini

4. volvemos a probar si funciona el modelo:

Genera 3 reseñas breves de productos en español. Cada reseña debe tener una etiqueta de sentimiento: positivo, neutro o negativo.

sí me hizo uno de cada uno

al salir del modelo con /bye podemos usar ollama list para ver los modelos descargados 

5. descargamos modelo mistral ahora que tiene 7 billones de parámetros:

ollama run mistral

probamosel mismo prompt  y me dio positivo neutro positivo y luego puse bye y puse el ollama list:

PS C:\Users\Isidora> ollama list
NAME              ID              SIZE      MODIFIED
mistral:latest    6577803aa9a0    4.4 GB    8 minutes ago
phi3:mini         4f2222927938    2.2 GB    17 minutes ago
llama3.2:1b       baf6a787fdff    1.3 GB    28 minutes ago

LLaMA: respondió en español, pero no respetó completamente las 3 etiquetas pedidas.
Phi: respondió en español y sí usó positivo, neutro y negativo.
Mistral: respondió en español, usó positivo/neutro/positivo, pero no generó negativo.

6. en VS abrir:
.\.venv\Scripts\Activate.ps1
py -m pip install requests pandas
py -m pip list

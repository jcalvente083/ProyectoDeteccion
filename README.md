# 👁️‍🗨️ Proyecto: Introducción a la Visión Artificial con YOLO
**Crea tu propio detector de intrusos inteligente desde cero**

Bienvenido a este proyecto introductorio. Este repositorio está diseñado para acercar el apasionante mundo de la **Visión por Computador** y la **Inteligencia Artificial** a personas sin conocimientos previos. 

A través de un enfoque totalmente práctico, aprenderemos a utilizar **YOLO (You Only Look Once)**, uno de los modelos de detección de objetos en tiempo real más rápidos y populares del mundo. ¡Pasaremos de encender la cámara web a tener un sistema de alarma conectado a tu móvil!

---

## 🚀 ¿Qué vas a lograr con este proyecto?

Al finalizar estas prácticas, habrás construido un sistema capaz de **"ver", "entender" y "avisar"**. El aprendizaje se divide en dos fases progresivas:

### 🟢 Fase 1: Primeros Pasos (`script1.ipynb`)
En esta fase interactiva en un Jupyter Notebook, entenderemos la magia detrás de la IA paso a paso:
* **Conexión de la cámara:** Aprenderás a capturar video en tiempo real usando tu webcam a través de **OpenCV**.
* **Carga del modelo:** Cargaremos el modelo ligero `yolov8n.pt` (Nano), ideal para ejecutar en la CPU de cualquier portátil.
* **Filtros personalizados:** Configuraremos la IA para detectar clases específicas (como `"person"`) con un umbral de confianza mínimo de `0.5` para evitar falsos positivos.
* **Visualización:** Verás cómo la IA procesa cada fotograma, dibuja rectángulos (*bounding boxes*) sobre los objetos y muestra etiquetas dinámicas con su porcentaje de acierto.

### 🔴 Fase 2: Sistema de Seguridad Domótico (`Script2.py`)
Llevaremos lo aprendido al siguiente nivel creando un script autónomo de producción integrado con un **Bot de Telegram**:
* **Alertas en tiempo real:** Si la cámara detecta un objeto de interés (`'person'`, `'car'` o `'cell phone'`), el sistema capturará un fotograma, lo guardará localmente con la fecha y hora, y te lo enviará instantáneamente a tu móvil.
* **Control Remoto por Comandos:** Podrás interactuar de forma bidireccional con tu IA mediante mensajes de Telegram:
    * `/start`: Saludo e inicio de interacción con la IA de seguridad.
    * `/activar` y `/desactivar`: Permite a los usuarios añadidos activar o pausar el envío de notificaciones.
    * `/encender` y `/apagar`: Detiene o reanuda por completo el motor de inferencia visual (hilo de IA).
    * `/umbral`: Consulta el valor de confianza actual. Si eres el Administrador, podrás modificarlo en tiempo real (ej. `/umbral 0.6`).
* **Seguridad y Permisos:** Cuenta con un filtro estricto por `ADMIN_ID` para que solo el propietario pueda encender/apagar el sistema, cambiar el umbral o gestionar accesos mediante los comandos `/anadirusuario <ID>` y `/eliminarusuario <ID>`.

---

## 🛠️ Tecnologías Utilizadas

Este proyecto utiliza el stack tecnológico más moderno y demandado en el sector de la IA:
* **Python:** Lenguaje base del proyecto.
* **OpenCV (`cv2`):** Tratamiento, manipulación y renderizado de imágenes/video en tiempo real.
* **Ultralytics (YOLO):** Arquitectura de red neuronal convolucional para la detección de objetos.
* **Python Telegram Bot:** API asíncrona para la creación y gestión del bot de mensajería.
* **Concurrency (`threading` y `asyncio`):** Uso de hilos independientes para lograr que la IA procese la cámara continuamente en segundo plano mientras el bot de Telegram atiende comandos de forma asíncrona.
* **Uv:** El gestor de paquetes de Python ultra rápido para la configuración del entorno.

---

## 📦 Instalación y Requisitos Previos

Este proyecto está optimizado para utilizar **uv**, el instalador de paquetes más rápido del ecosistema Python.

1. **Clona el repositorio** o descarga los archivos en una carpeta local.
2. **Crea y activa tu entorno virtual** con `uv`:
   ```bash
   # Crear el entorno virtual
   uv venv
   
   # Activar el entorno (Linux/macOS)
   source .venv/bin/activate
   
   # Activar el entorno (Windows - PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. **Instala las dependencias** necesarias en un solo comando:

   ```bash
   uv sync
   ```

---

## 📂 Estructura del Proyecto

Tu espacio de trabajo debe estar organizado de la siguiente manera:

```text
📂 BotDeteccion/
├── 📁 .soluciones           
|    ├── 📄 script1_solucion.ipynb  # Cuaderno interactivo solucionado (Fase 1)
|    └── 📄 script2_solucion.py  # Script del sistema de seguridad solucionado (Fase 2)
|
├── 📄 .env                         # Archivo oculto de configuración (¡No lo compartas!)
├── 📄 .python-version              # Archivo oculto con la versión recomendada de Python
├── 📄 pyproject.toml               # Archivo de configuración del proyecto y dependencias
├── 📄 README.MD                    # Archivo descriptivo del proyecto
├── 📄 script1.ipynb                # Cuaderno interactivo (Fase 1)
├── 📄 Script2.py                   # Script del sistema de seguridad (Fase 2)
└── 📁 avisos/                      # Carpeta autogenerada donde se almacenan las capturas de intrusos

```

---

## ⚙️ Configuración del Entorno (`.env`)

Antes de arrancar, necesitas crear un archivo llamado `.env` en la raíz del proyecto para almacenar tus credenciales secretas de forma segura:

```env
# Token de tu bot obtenido mediante @BotFather en Telegram
TELEGRAM_TOKEN="TU_TOKEN_SECRETO_AQUI"

# Tu ID de usuario de Telegram (puedes obtenerlo con @userinfobot)
ADMIN_ID="123456789"

# Índice de la cámara fuente (0 suele ser la webcam integrada)
CAMARA_FUENTE="0"
```

---

## 🏃‍♂️ ¿Cómo ejecutar el proyecto?

### Ejecución de la Fase 1
Abre tu editor favorito (como Visual Studio Code con la extensión de Jupyter o Jupyter Lab), abre `script1.ipynb` y ejecuta las celdas en orden secuencial. Pulsa la tecla **'q'** con la ventana del video activa para cerrar la cámara de forma segura.

### Ejecución de la Fase 2
Para lanzar tu sistema de seguridad permanente con el Bot de Telegram, ejecuta el script principal desde tu terminal con el entorno virtual activo:
```bash
uv run Script2.py
```
Una vez que veas en la terminal el mensaje `✅ Bot funcionando`, ve a tu chat de Telegram y envía el comando `/activar` para empezar a recibir alertas con fotos de los intrusos detectados.

---

## 💡 ¿Por qué este proyecto?

La Inteligencia Artificial no tiene por qué ser una caja negra inaccesible. Con este proyecto demostramos cómo, combinando unas pocas librerías potentes y estructurando el código de forma limpia (con hilos y concurrencia asíncrona), cualquier persona puede crear una herramienta domótica de vanguardia útil, divertida y aplicable al mundo real.

¡Disfruta dándole ojos a tu ordenador! 🚀
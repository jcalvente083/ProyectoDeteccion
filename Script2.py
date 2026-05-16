## En este script montaremos nuestro propio detector de intrusos con avisos vía Telegram incluidos.

# IMPORTACIÓN DE LIBRERIAS  
import cv2                                                                      # OpenCV. Visión por Computador.
import time                                                                     # Time. Esperas.    
from ultralytics import YOLO                                                    # Ultralytics. YOLO.
from datetime import datetime                                                   # DateTime. Obtener la hora.
import asyncio                                                                  # Necesaria Consultas a la API.    
from telegram import Bot, Update                                                # Telegram API. Creación y Actualización del Bot.
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes   # Telegram API. Crear comandos.
import threading                                                                # Threading. Creación de hilos.
import os                                                                       # OS. Llamadas al sistema.
from dotenv import load_dotenv                                                  # .ENV. Uso de Enviroments

# CARGA DEL ENVIROMENT Y OBTENCIÓN DE VARIABLES GLOBALES.
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
cam_env = os.getenv("CAMARA_FUENTE", "0")
camara_fuente = int(cam_env) if cam_env.isdigit() else cam_env

# =========================================================================
# CONFIGURA TU INTELIGENCIA ARTIFICIAL.
# =========================================================================
target_classes = [  ]       # TODO: Seleccionar las clases que detectaremos.
UMBRAL =                    # TODO: Umbral para la detección y avisos.

cooldown = 30               # TODO:  Elegir los segundos que espera el bot para no inundarte a mensajes                    

carpetaAvisos = 'avisos/'
alertas_activadas = True

# Solución a la espera activa: Usar un threading.Event en lugar de un booleano simple
ENCENDIDO = threading.Event()
ENCENDIDO.set()             # Inicializamos el evento como "Activado"
usuarios_activos = set()

def deteccion():
    '''
    Función principal de la detección. En esta función se realiza al principio la carga del modelo que vamos a usar.
    Para luego
    '''
    global alertas_activadas, UMBRAL
    
    print("Cargando modelo YOLOv8...")
    # TODO: Carga el modelo
    model = 
    
    while True:
        ENCENDIDO.wait()

        cap = cv2.VideoCapture(camara_fuente)
        last_detection_time = 0 

        box_color = (0, 255, 0)
        text_color = (0, 0, 0)

        while ENCENDIDO.is_set():
            ret, frame = cap.read()
            if not ret:
                time.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(camara_fuente)
                continue

            current_time = time.time()
            
            # =========================================================================
            # INFERENCIA Y FILTRADO
            # =========================================================================
            # TODO: Pasa el frame por el modelo
            results = 

            clase_objetivo_encontrada = False
            clases_detectadas = set()

            # TODO: Itera sobre las cajas (.boxes) detectadas en tus resultados
            for result in             :
                cls_id = int(result.cls)
                conf = float(result.conf)
                label = model.names[cls_id]

                # TODO: Condición de detección
                if                     : 
                    clase_objetivo_encontrada = True
                    clases_detectadas.add(f"{label} ({conf:.2f})")
                    
                    x1, y1, x2, y2 = map(int, result.xyxy[0])
                
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 4)
                    
                    text = f"{label} {conf:.2f}"
                    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                    cv2.rectangle(frame, (x1, y1), (x1 + tw, y1 - th - baseline), box_color, cv2.FILLED)
                    cv2.putText(frame, text, (x1, y1 - baseline), cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 2)

            # =========================================================================
            # ALERTA DE TELEGRAM
            # =========================================================================
            if clase_objetivo_encontrada and alertas_activadas:
                if current_time - last_detection_time > cooldown:
                    timestamp = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
                    clases_str = "_".join(clases_detectadas)
                    os.makedirs(carpetaAvisos, exist_ok=True)
                    filename = f'{carpetaAvisos}/{timestamp}-{clases_str}.jpg'
                    
                    cv2.imwrite(filename, frame)
                    print(f"\n📸 ¡Intruso detectado! Foto guardada.")

                    # TODO: Personaliza el mensaje de aviso que te llegara a Telegram. 
                    # Usa las variables clases_str y timestamp
                    caption = f"🚨 " 
                    
                    enviar_aviso_async(filename, caption)
                    last_detection_time = current_time

            cv2.imshow("Fase 2: Sistema de Seguridad Activo", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# =========================================================================
# ⚙️ EL MOTOR: TELEGRAM Y CONCURRENCIA (NO TOCAR)
# =========================================================================

def enviar_aviso_async(foto_path, caption):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(avisoTelegram(foto_path, caption))
        else:
            asyncio.run(avisoTelegram(foto_path, caption))
    except RuntimeError:
        asyncio.run(avisoTelegram(foto_path, caption))

async def avisoTelegram(foto_path, caption_):
    bot = Bot(token=TOKEN)
    for user_id in usuarios_activos:
        try:
            with open(foto_path, "rb") as photo:
                await bot.send_photo(chat_id=user_id, photo=photo, caption=caption_)
            print(f"✅ Notificación enviada a Telegram ({user_id})")
        except Exception as e:
            print(f"⚠️ Error enviando a {user_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Soy tu IA de seguridad. Usa /activar para empezar a recibir alertas.")

async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuarios_activos.add(update.effective_chat.id)
    await update.message.reply_text("✅ Alertas ACTIVADAS. Te avisaré si detecto algo.")

async def desactivar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuarios_activos.discard(update.effective_chat.id)
    await update.message.reply_text("🛑 Alertas DESACTIVADAS.")

async def anadirusuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Solo ADMIN
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando denegado. Solo el ADMIN puede añadir usuarios.")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Debes proporcionar un identificador. Uso: /anadirusuario <ID>")
        return
        
    try:
        nuevo_usuario = int(context.args[0])
        usuarios_activos.add(nuevo_usuario)
        await update.message.reply_text(f"✅ Usuario {nuevo_usuario} añadido. Ahora tiene acceso a las notificaciones.")
    except ValueError:
        await update.message.reply_text("⚠️ Error: El ID de usuario debe ser un número.")

async def eliminarusuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Solo ADMIN
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando denegado. Solo el ADMIN puede eliminar usuarios.")
        return
        
    if not context.args:
        await update.message.reply_text("⚠️ Debes proporcionar un identificador. Uso: /eliminarusuario <ID>")
        return
        
    try:
        usuario_a_eliminar = int(context.args[0])
        if usuario_a_eliminar in usuarios_activos:
            usuarios_activos.discard(usuario_a_eliminar)
            await update.message.reply_text(f"🗑️ Usuario {usuario_a_eliminar} eliminado. Ya no recibirá notificaciones.")
        else:
            await update.message.reply_text("⚠️ El usuario indicado no está en la lista de notificaciones.")
    except ValueError:
        await update.message.reply_text("⚠️ Error: El ID de usuario debe ser un número.")

async def encender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ENCENDIDO
    # Solo ADMIN
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando denegado. Solo el ADMIN puede encender el sistema.")
        return
        
    ENCENDIDO = True
    await update.message.reply_text("🟢 Sistema de detecciones y avisos REANUDADO.")

async def apagar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ENCENDIDO
    # Solo ADMIN
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando denegado. Solo el ADMIN puede apagar el sistema.")
        return
        
    ENCENDIDO = False
    await update.message.reply_text("🔴 Sistema de detecciones y avisos DETENIDO.")

async def umbral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global UMBRAL
    
    # Sin parámetros: Cualquiera puede consultarlo
    if not context.args:
        await update.message.reply_text(f"📊 El valor de detección (UMBRAL) actual es: {UMBRAL}")
        return
        
    # Con parámetros: Solo ADMIN puede modificarlo
    if update.effective_chat.id != ADMIN_ID:
        await update.message.reply_text("⛔ Comando denegado. Solo el ADMIN puede modificar el umbral.")
        return
        
    try:
        # TODO: Crea toda la lógica para actualizar el UMBRAL. Recuerda que:
        # - El umbral debe de ser mayor o igual a 0 y menor o igual a 1.
        # - La forma de enviar mensajes es:  await update.message.reply_text("mensaje_a_enviar").

    except ValueError:
        await update.message.reply_text("⚠️ Error: El parámetro debe ser un número decimal.")

def iniciar_bot():
    print("🚀 Iniciando conexión con Telegram...")
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("activar", activar))
    app.add_handler(CommandHandler("desactivar", desactivar))
    app.add_handler(CommandHandler("anadirusuario", anadirusuario))
    app.add_handler(CommandHandler("eliminarusuario", eliminarusuario))
    app.add_handler(CommandHandler("encender", encender))
    app.add_handler(CommandHandler("apagar", apagar))
    app.add_handler(CommandHandler("umbral", umbral))
    
    print("✅ Bot funcionando. Ve a Telegram y manda /activar")
    app.run_polling()

if __name__ == "__main__":
    if not TOKEN or ADMIN_ID == 0:
        print("❌ ERROR: No se ha encontrado el TOKEN o ADMIN_ID en el archivo .env.")
        exit()
        
    hilo_ia = threading.Thread(target=deteccion, daemon=True)
    hilo_ia.start()
    
    iniciar_bot()
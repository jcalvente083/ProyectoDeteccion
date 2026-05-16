# fase2_domotica.py
import cv2
import time
from ultralytics import YOLO
from datetime import datetime
import asyncio
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading
import os
from dotenv import load_dotenv

# =========================================================================
# 🎓 ZONA DE CONFIGURACIÓN Y CREDENCIALES (Cargadas desde .env)
# =========================================================================

# Cargamos el archivo .env
load_dotenv()

# Extraemos las credenciales de forma segura
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Extraemos la cámara
cam_env = os.getenv("CAMARA_FUENTE", "0")
camara_fuente = int(cam_env) if cam_env.isdigit() else cam_env

target_classes = ['person', 'car', 'cell phone'] 
UMBRAL = 0.5 
cooldown = 30                        

carpetaAvisos = 'avisos/'
alertas_activadas = True
ENCENDIDO = True
usuarios_activos = set()

# =========================================================================
# 🧠 EL CEREBRO: DETECCIÓN CONTINUA E INFERENCIA
# =========================================================================

def deteccion():
    global alertas_activadas, ENCENDIDO, UMBRAL
    
    print("Cargando modelo YOLOv8...")
    model = YOLO('yolov8n.pt')
    
    while True:
        if not ENCENDIDO:
            time.sleep(1)
            continue

        cap = cv2.VideoCapture(camara_fuente)
        last_detection_time = 0 

        line_thickness = 4
        font_scale = 1.0
        font_thickness = 2
        text_color = (0, 0, 0)
        box_color = (0, 255, 0)

        while ENCENDIDO:
            ret, frame = cap.read()
            if not ret:
                time.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(camara_fuente)
                continue

            current_time = time.time()
            results = model(frame)[0]

            clase_objetivo_encontrada = False
            clases_detectadas = set()

            for result in results.boxes:
                cls_id = int(result.cls)
                conf = float(result.conf)
                label = model.names[cls_id]

                if label in target_classes and conf >= UMBRAL:
                    clase_objetivo_encontrada = True
                    clases_detectadas.add(f"{label} ({conf:.2f})")
                    
                    x1, y1, x2, y2 = map(int, result.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, line_thickness)
                    
                    text = f"{label} {conf:.2f}"
                    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
                    cv2.rectangle(frame, (x1, y1), (x1 + tw, y1 - th - baseline), box_color, cv2.FILLED)
                    cv2.putText(frame, text, (x1, y1 - baseline), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness)

            if clase_objetivo_encontrada and alertas_activadas:
                if current_time - last_detection_time > cooldown:
                    timestamp = datetime.now().strftime('%d-%m-%y_%H-%M-%S')
                    clases_str = "_".join(clases_detectadas)
                    os.makedirs(carpetaAvisos, exist_ok=True)
                    filename = f'{carpetaAvisos}/{timestamp}-{clases_str}.jpg'
                    
                    cv2.imwrite(filename, frame)
                    print(f"\n📸 ¡Intruso detectado! Foto guardada: {filename}")

                    caption = f"🚨 ¡ALERTA DE INTRUSO!\nSe ha detectado: {clases_str} a las {timestamp}"
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
        nuevo_umbral = float(context.args[0])
        if 0.0 <= nuevo_umbral <= 1.0:
            UMBRAL = nuevo_umbral
            await update.message.reply_text(f"⚙️ UMBRAL actualizado correctamente a: {UMBRAL}")
        else:
            await update.message.reply_text("⚠️ El UMBRAL debe ser un número entre 0.0 y 1.0 (ej. 0.6)")
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
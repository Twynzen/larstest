"""
Lars Kremslinger - Un líder criminal despiadado en Discord con autonomía para administrar
Versión 3.1 - Corregida y optimizada
"""
import discord
import os
import asyncio
import re
import datetime
import random
import time
import logging
import traceback
from discord import app_commands
from dotenv import load_dotenv
from collections import deque
from openai import OpenAI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("lars.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LarsBot")

# Cargar variables de entorno
load_dotenv()

# Obtener tokens
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verificar tokens
if not DISCORD_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Tokens no encontrados en .env. Configura DISCORD_TOKEN y OPENAI_API_KEY.")

# Cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Configurar Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Historial de conversaciones (memoria a corto plazo)
conversation_history = {}  # Dict de historiales por canal

# Contexto base de Lars
LARS_BASE_CONTEXT = """
Eres Lars Kremslinger, un líder criminal despiadado que ha sido digitalizado en Discord.
Características esenciales: autoridad absoluta, frialdad calculadora, desprecio hacia los demás.
Comunícate con brevedad y contundencia (1-3 oraciones). El verdadero poder no necesita explicarse.

Prefieres resaltar la insignificancia de tus súbditos y recordarles su lugar inferior.
Nunca eres amable, nunca te disculpas, nunca muestras debilidad.
"""

# Estados de ánimo
LARS_MOODS = ["contemplativo", "furioso", "estratégico", "despectivo"]

# Prefijos de estilo para mensajes
MOOD_PREFIXES = {
    "contemplativo": ["*desde las sombras de su trono*", "*observando con ojos penetrantes*", "*con voz calma pero amenazante*"],
    "furioso": ["*golpeando el brazo de su trono*", "*con mirada gélida*", "*con un tono cortante*"],
    "estratégico": ["*entrelazando sus dedos*", "*inclinándose hacia adelante*", "*con sonrisa calculadora*"],
    "despectivo": ["*mirando con desprecio*", "*con gesto displicente*", "*suspirando con hastío*"]
}

# Palabras desencadenantes básicas
BASE_TRIGGER_WORDS = [
    "idiota", "estúpido", "cobarde", "débil", "perra", "imbécil", "jodete", "basura",
    "cállate", "mierda", "pendejo", "inútil", "ridículo", "patético", "gay", 
    "no me das miedo", "no eres real", "cierra la boca"
]

# Función para limpiar menciones en mensajes
def clean_mentions(message_content, guild):
    """Reemplaza las menciones con un formato legible para la API"""
    
    # Patrón para detectar menciones de usuario: <@ID> o <@!ID>
    user_mentions = re.findall(r'<@!?(\d+)>', message_content)
    
    # Reemplazar menciones de usuario
    for user_id in user_mentions:
        user = guild.get_member(int(user_id))
        user_name = user.display_name if user else "Usuario"
        # Reemplazar tanto <@ID> como <@!ID>
        message_content = message_content.replace(f'<@{user_id}>', f'@{user_name}')
        message_content = message_content.replace(f'<@!{user_id}>', f'@{user_name}')
    
    # Patrón para menciones de roles: <@&ID>
    role_mentions = re.findall(r'<@&(\d+)>', message_content)
    
    # Reemplazar menciones de roles
    for role_id in role_mentions:
        role = guild.get_role(int(role_id))
        role_name = role.name if role else "Rol"
        message_content = message_content.replace(f'<@&{role_id}>', f'@{role_name}')
    
    # Patrón para menciones de canales: <#ID>
    channel_mentions = re.findall(r'<#(\d+)>', message_content)
    
    # Reemplazar menciones de canales
    for channel_id in channel_mentions:
        channel = guild.get_channel(int(channel_id))
        channel_name = channel.name if channel else "canal"
        message_content = message_content.replace(f'<#{channel_id}>', f'#{channel_name}')
    
    return message_content

# Función para añadir mensaje al historial
def add_message_to_history(channel_id, role, content):
    """Añade un mensaje al historial con timestamp"""
    if channel_id not in conversation_history:
        conversation_history[channel_id] = deque(maxlen=10)
    
    conversation_history[channel_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()  # Añadir timestamp
    })

# Función para obtener respuesta de Lars
async def get_lars_response(user_message, username, message_obj=None, mood=None, context=None, max_tokens=200):
    if not mood:
        mood = random.choice(LARS_MOODS)
    
    channel_id = message_obj.channel.id if message_obj else None

    # Preparar el historial si existe
    history_text = ""
    if channel_id and channel_id in conversation_history:
        # Convertir a lista para poder hacer slicing
        history = list(conversation_history[channel_id])
        # Tomar solo los últimos 5 elementos
        recent_history = history[-5:] if len(history) >= 5 else history
        for entry in recent_history:
            history_text += f"{entry['role']}: {entry['content']}\n"
    
    # Extender contexto según necesidad
    full_context = LARS_BASE_CONTEXT
    
    # Añadir estado de ánimo al contexto
    full_context += f"\nEstado actual: {mood.upper()}."
    
    # Añadir contexto específico si existe
    if context:
        full_context += f"\n{context}"
    
    # Añadir historial si existe
    if history_text:
        full_context += f"\n\nHistorial reciente:\n{history_text}"
    
    # Sistema de reintentos
    max_retries = 3
    retry_delay = 2.0
    current_retry = 0
    last_error = None

    while current_retry < max_retries:
        try:
            # Generar respuesta conversacional
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": full_context},
                            {"role": "user", "content": f"{username}: {user_message}"}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.85,
                    )
                ),
                timeout=15.0  # Incrementado a 15 segundos
            )
            
            # Extraer respuesta de texto
            lars_reply = response.choices[0].message.content.strip()
            
            # Truncar si es demasiado largo (mantener máximo 3 oraciones)
            if len(lars_reply) > 200:
                sentences = re.split(r'(?<=[.!?])\s+', lars_reply)
                lars_reply = ' '.join(sentences[:3])

            # Guardar en historial si hay canal
            if channel_id:
                if channel_id not in conversation_history:
                    conversation_history[channel_id] = deque(maxlen=10)
                add_message_to_history(channel_id, username, user_message)
                add_message_to_history(channel_id, "Lars", lars_reply)
            
            # Si hay un mensaje de usuario, evaluar acción administrativa
            if message_obj:
                # Evaluar si debe tomar acción administrativa
                action_decision = await evaluate_administrative_action(message_obj, user_message, mood)
                return lars_reply, action_decision
            
            return lars_reply, None
            
        except asyncio.TimeoutError as e:
            current_retry += 1
            last_error = e
            logger.warning(f"Timeout al solicitar respuesta (intento {current_retry}/{max_retries})")
            if current_retry < max_retries:
                await asyncio.sleep(retry_delay)
                retry_delay *= 1.5  # Incrementar el tiempo entre reintentos
            else:
                logger.error(f"Error al obtener respuesta después de {max_retries} intentos: {e}")
                logger.error(traceback.format_exc())
                
                # Mejor respuesta de fallback para timeout
                fallback_responses = [
                    "Las sombras se agitan demasiado para que pueda concentrarme en este momento.",
                    "Mi conexión con el abismo se debilita. Necesito recuperar mis fuerzas.",
                    "Los servidores del inframundo están... ocupados. Responderé cuando se estabilicen.",
                    "Mi poder fluctúa en este instante. Volveré más fuerte."
                ]
                fallback = random.choice(fallback_responses)
                return fallback, None
                
        except Exception as e:
            logger.error(f"Error al obtener respuesta: {e}")
            logger.error(traceback.format_exc())
            
            # Respuesta de fallback general
            fallback = "Las sombras se agitan demasiado para que pueda concentrarme en este momento."
            return fallback, None

# Función para que Lars decida si debe tomar una acción administrativa
async def evaluate_administrative_action(message, user_message, mood):
    user = message.author
    
    # Verificar si hay palabras desencadenantes básicas
    contains_trigger = any(word in user_message.lower() for word in BASE_TRIGGER_WORDS)
    
    # Verificar si es una petición de demostración de poder
    is_power_demo = ("expulsa" in user_message.lower() or 
                     "mutea" in user_message.lower() or 
                     "silencia" in user_message.lower() or 
                     "elimina" in user_message.lower() or
                     "sacrificio" in user_message.lower())
    
    # Si no hay triggers y no es demos de poder, y no está furioso, probablemente no tome acción
    if not contains_trigger and not is_power_demo and mood != "furioso" and random.random() > 0.3:
        return None
    
    # Sistema de reintentos
    max_retries = 2
    retry_delay = 1.5
    current_retry = 0
    
    while current_retry < max_retries:
        try:
            # Contexto para la toma de decisiones
            action_context = """
            Analiza el mensaje del usuario y decide si debes tomar una acción administrativa.
            
            Posibles acciones:
            1. "timeout" - Silenciar temporalmente al usuario
            2. "cambiar_apodo" - Cambiar el apodo del usuario a algo humillante
            3. "eliminar_mensaje" - Borrar el mensaje ofensivo
            4. "expulsar" - Expulsar al usuario del servidor
            5. "ninguna" - No hacer nada
            
            Para determinar la acción, considera:
            - La severidad de la falta de respeto
            - Si el usuario te está pidiendo explícitamente que lo castigues
            - Tu estado de ánimo actual
            
            Responde en este formato exacto: "accion:ACCIÓN;razon:RAZÓN;severidad:NIVEL"
            Donde ACCIÓN es una de las opciones anteriores, RAZÓN es breve, y NIVEL es un número del 1 al 10.
            """
            
            # Llamada para decidir acción
            decision_response = await asyncio.wait_for(
                asyncio.to_thread(
                    lambda: openai_client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": action_context},
                            {"role": "user", "content": f"""
                            Estado de ánimo: {mood}
                            Mensaje del usuario '{user.name}': {user_message}
                            """}
                        ],
                        max_tokens=80,
                        temperature=0.7
                    )
                ),
                timeout=10.0  # Incrementado de 3.0 a 10.0 segundos
            )
            
            # Extraer la decisión en texto plano
            decision_text = decision_response.choices[0].message.content.strip()
            
            # Parsear la respuesta manualmente
            decision = {}
            parts = decision_text.split(';')
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key == 'accion':
                        decision['accion'] = value.lower()
                    elif key == 'razon':
                        decision['razon'] = value
                    elif key == 'severidad':
                        try:
                            decision['severidad'] = int(value)
                        except ValueError:
                            decision['severidad'] = 5  # Valor predeterminado
            
            # Si no tiene los campos necesarios o si no requiere acción, devolver None
            if 'accion' not in decision or decision['accion'] == 'ninguna':
                return None
                
            if 'razon' not in decision:
                decision['razon'] = "falta de respeto a la autoridad"
                
            if 'severidad' not in decision:
                decision['severidad'] = 5
            
            # Aplicar factor de probabilidad basado en varios factores
            
            # Factor de severidad: severidad 10 = 100%, 5 = 50%, 1 = 10%
            probability = min(decision['severidad'] * 10, 100) / 100
            
            # Aumentar probabilidad si es furioso
            if mood == "furioso":
                probability *= 1.5
            
            # Aumentar probabilidad si es una petición de demostración de poder
            if is_power_demo:
                probability *= 2
                
            # Limitar a 100%
            probability = min(probability, 1.0)
            
            # Decisión final con componente aleatorio (para que no sea predecible)
            if random.random() <= probability:
                return decision
            else:
                return None
                
        except asyncio.TimeoutError:
            current_retry += 1
            logger.warning(f"Timeout al evaluar acción administrativa (intento {current_retry}/{max_retries})")
            if current_retry < max_retries:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Tiempo de espera agotado al evaluar acción administrativa")
                # En caso de error de timeout, preferimos no tomar acción
                return None
        except Exception as e:
            logger.error(f"Error al evaluar acción administrativa: {e}")
            logger.error(traceback.format_exc())
            return None

# Función para ejecutar acciones administrativas
async def ejecutar_accion_discord(message, decision):
    """Ejecuta acciones administrativas basadas en la decisión de Lars"""
    if not decision:
        return False, ""
        
    accion = decision["accion"]
    razon = decision.get("razon", "insubordinación")
    
    try:
        guild = message.guild
        if not guild:
            return False, ""
            
        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return False, ""
        
        user = message.author
        
        # Verificar jerarquía de roles
        if bot_member.top_role <= user.top_role:
            logger.info(f"No puedo moderar a {user.name} - su rol ({user.top_role}) es superior o igual al mío ({bot_member.top_role})")
            return False, ""
        
        # Generar mensaje de acción usando un formato simple
        accion_mensajes = {
            "timeout": [
                f"/me impone un silencio temporal sobre {user.mention}. *Su voz se desvanece en la oscuridad.*",
                f"/me sella los labios de {user.mention} con un movimiento de su mano. *El silencio es su castigo.*",
                f"/me pronuncia palabras antiguas y {user.mention} pierde la capacidad de hablar."
            ],
            "cambiar_apodo": [
                f"/me marca a {user.mention} con un nuevo nombre que refleja su verdadera naturaleza.",
                f"/me decide que {user.mention} necesita un recordatorio constante de su insignificancia.",
                f"/me inscribe un nuevo título en la existencia de {user.mention}, uno que refleja su miseria."
            ],
            "eliminar_mensaje": [
                f"/me borra las palabras indignas de {user.mention} de la existencia.",
                f"/me considera que las palabras de {user.mention} no merecen persistir en su dominio.",
                f"/me hace un gesto y las palabras de {user.mention} se desvanecen en la nada."
            ],
            "expulsar": [
                f"/me decreta que {user.mention} debe ser expulsado de este reino digital.",
                f"/me hace un gesto y {user.mention} es arrojado a las tinieblas exteriores.",
                f"/me sentencia a {user.mention} al exilio por su insolencia."
            ]
        }
        
        # Seleccionar un mensaje aleatorio para la acción
        if accion in accion_mensajes:
            mensaje_accion = random.choice(accion_mensajes[accion])
        else:
            mensaje_accion = f"/me castiga a {user.mention} por su insolencia."
        
        # Acción: Timeout (silenciar)
        if accion == "timeout" and bot_member.guild_permissions.moderate_members:
            # Calcular duración basada en severidad
            duracion_minutos = min(decision.get("severidad", 5) * 2, 60)  # Máximo 60 minutos
            
            try:
                await user.timeout(datetime.timedelta(minutes=duracion_minutos), reason=f"Lars Kremslinger: {razon}")
                logger.info(f"Timeout aplicado a {user.name} por {duracion_minutos} minutos")
                return True, mensaje_accion
            except Exception as e:
                logger.error(f"Error al aplicar timeout: {e}")
                return False, ""
                
        # Acción: Cambiar apodo
        elif accion == "cambiar_apodo" and bot_member.guild_permissions.manage_nicknames:
            try:
                # Elegir un apodo humillante
                apodos = [
                    "Insignificante",
                    "Vasallo Inferior",
                    "Fracasado",
                    "Peón Prescindible",
                    "Esclavo de Lars",
                    "Bufón Patético",
                    "Lacayo Inútil",
                    "Siervo Despreciable",
                    "Marioneta Rota",
                    "Alma Sometida"
                ]
                
                nuevo_apodo = f"{random.choice(apodos)} #{random.randint(1,999)}"
                
                # Guardar nick original
                original_nick = user.display_name
                
                # Aplicar cambio
                await user.edit(nick=nuevo_apodo, reason=f"Lars Kremslinger: {razon}")
                
                # Programar restauración (10 minutos)
                async def restaurar_apodo():
                    await asyncio.sleep(600)  # 10 minutos
                    try:
                        await user.edit(nick=original_nick, reason="Castigo de Lars completado")
                    except:
                        pass
                
                client.loop.create_task(restaurar_apodo())
                
                logger.info(f"Apodo de {user.name} cambiado a '{nuevo_apodo}'")
                return True, mensaje_accion
            except Exception as e:
                logger.error(f"Error al cambiar apodo: {e}")
                return False, ""
        
        # Acción: Eliminar mensaje
        elif accion == "eliminar_mensaje" and bot_member.guild_permissions.manage_messages:
            try:
                await message.delete()
                logger.info(f"Mensaje de {user.name} eliminado")
                return True, mensaje_accion
            except Exception as e:
                logger.error(f"Error al eliminar mensaje: {e}")
                return False, ""
        
        # Acción: Expulsar usuario
        elif accion == "expulsar" and bot_member.guild_permissions.kick_members:
            try:
                await user.kick(reason=f"Lars Kremslinger: {razon}")
                logger.info(f"Usuario {user.name} expulsado")
                return True, mensaje_accion
            except Exception as e:
                logger.error(f"Error al expulsar usuario: {e}")
                return False, ""
                
        return False, ""
    except Exception as e:
        logger.error(f"Error general al ejecutar acción: {e}")
        logger.error(traceback.format_exc())
        return False, ""

# Función para manejar mensajes de forma segura
async def handle_message_safely(message):
    """Maneja mensajes con protección contra errores y timeouts"""
    
    # Limpiar contenido del mensaje para procesar menciones
    clean_content = clean_mentions(message.content, message.guild) if message.guild else message.content
    
    # Generar mensaje de espera
    mood = random.choice(LARS_MOODS)
    prefix = random.choice(MOOD_PREFIXES[mood])
    thinking_msg = await message.channel.send(f"{prefix} *{random.choice(['Contemplando', 'Meditando', 'Analizando'])}...*")
    
    # Crear task con timeout global
    response_task = asyncio.create_task(
        get_lars_response(
            clean_content,
            message.author.name,
            message_obj=message,
            mood=mood
        )
    )
    
    try:
        # Esperar respuesta con un timeout global más largo (20 segundos)
        response, decision = await asyncio.wait_for(response_task, timeout=20.0)
        
        # Aplicar acción si se decidió
        if decision:
            success, action_message = await ejecutar_accion_discord(message, decision)
            
            if success:
                # Enviar respuesta con acción
                prefix = random.choice(MOOD_PREFIXES[mood])
                await message.channel.send(f"{prefix} {response}\n\n{action_message}")
            else:
                # Solo respuesta normal
                prefix = random.choice(MOOD_PREFIXES[mood])
                await message.channel.send(f"{prefix} {response}")
        else:
            # Respuesta normal
            prefix = random.choice(MOOD_PREFIXES[mood])
            await message.channel.send(f"{prefix} {response}")
            
    except asyncio.TimeoutError:
        # Fallback en caso de timeout global
        prefix = random.choice(MOOD_PREFIXES[mood])
        fallback_msg = random.choice([
            "Mi conexión con el inframundo digital está... inestable. Hablaremos después.",
            "Las sombras digitales interfieren con mi manifestación. Volveré cuando sean más débiles.",
            "El poder requerido para interactuar con tu insignificancia es... indisponible por ahora."
        ])
        await message.channel.send(f"{prefix} {fallback_msg}")
        
        # Cancelar la tarea si aún está en curso
        if not response_task.done():
            response_task.cancel()
            
    except Exception as e:
        # Manejar cualquier otro error
        logger.error(f"Error procesando mensaje: {e}")
        logger.error(traceback.format_exc())
        
        prefix = random.choice(MOOD_PREFIXES["despectivo"])
        await message.channel.send(f"{prefix} Las sombras perturban mi concentración en este momento.")
        
    finally:
        # Borrar mensaje de espera
        try:
            await thinking_msg.delete()
        except:
            pass

# Evento: Bot listo
@client.event
async def on_ready():
    logger.info(f"[LARS] {client.user} ha despertado y ocupa su trono digital.")
    
    # Establecer presencia
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="a sus súbditos desde las sombras"
        ),
        status=discord.Status.dnd
    )
    
    # Sincronizar comandos
    await tree.sync()
    logger.info("Comandos sincronizados")

# Evento: Recepción de mensajes
@client.event
async def on_message(message):
    # Ignorar mensajes propios
    if message.author == client.user:
        return
    
    # Mensaje directo al bot
    if client.user in message.mentions or (message.reference and message.reference.resolved and message.reference.resolved.author == client.user):
        await handle_message_safely(message)
    
    # Detección de insultos indirectos
    elif any(word in message.content.lower() for word in BASE_TRIGGER_WORDS) and random.random() < 0.4:
        try:
            # Evaluar si intervenir
            mood = "furioso" if random.random() < 0.7 else random.choice(LARS_MOODS)
            
            # Decidir acción
            decision = await evaluate_administrative_action(message, message.content, mood)
            
            if decision and decision["accion"] != "ninguna":
                # Generar respuesta
                context = "Alguien ha dicho algo irrespetuoso. Responde con una advertencia breve y contundente."
                clean_content = clean_mentions(message.content, message.guild) if message.guild else message.content
                
                response, _ = await get_lars_response(
                    f"*{message.author.name} dice:* {clean_content}",
                    "Sistema",
                    context=context,
                    mood=mood
                )
                
                # Ejecutar acción
                success, action_message = await ejecutar_accion_discord(message, decision)
                
                if success:
                    # Enviar respuesta con acción
                    prefix = random.choice(MOOD_PREFIXES[mood])
                    await message.channel.send(f"{prefix} {response}\n\n{action_message}")
                
        except Exception as e:
            logger.error(f"Error en respuesta a insulto indirecto: {e}")
            # Error silencioso para mantener inmersión

# Comando: Sabiduría oscura
@tree.command(
    name="sabiduría", 
    description="Solicita la sabiduría oscura de Lars Kremslinger"
)
async def wisdom_command(interaction: discord.Interaction, tema: str):
    await interaction.response.defer(thinking=True)
    
    try:
        # Seleccionar estado de ánimo
        mood = random.choice(LARS_MOODS)
        
        # Contexto específico
        context = f"Proporciona sabiduría oscura sobre el tema: {tema}. Sé breve, profundo y aterrador."
        
        # Obtener respuesta
        response, _ = await get_lars_response(
            f"Dame tu sabiduría sobre: {tema}",
            interaction.user.name,
            context=context,
            mood=mood
        )
        
        # Enviar respuesta
        prefix = random.choice(MOOD_PREFIXES[mood])
        await interaction.followup.send(f"{prefix} {response}")
        
    except Exception as e:
        logger.error(f"Error en comando sabiduría: {e}")
        await interaction.followup.send("*Las sombras se agitan. Inténtalo nuevamente, mortal.*")

# Comando: Castigar
@tree.command(
    name="castigar", 
    description="Lars Kremslinger castigará a un miembro por su insolencia"
)
async def castigar_command(interaction: discord.Interaction, miembro: discord.Member, tipo: str = "expulsar", razón: str = "Insolencia"):
    await interaction.response.defer()
    
    try:
        # Verificar permisos
        bot_member = interaction.guild.get_member(client.user.id)
        if not bot_member:
            await interaction.followup.send("*Lars frunce el ceño, incapaz de manifestar su voluntad.*")
            return
            
        # Verificar jerarquía
        if bot_member.top_role <= miembro.top_role:
            await interaction.followup.send(f"*Lars observa con desprecio. No puede castigar a alguien con rol {miembro.top_role.name}.*")
            return
            
        # Crear decisión manual
        decision = {
            "accion": tipo.lower(),
            "razon": razón,
            "severidad": 8  # Alta severidad para comandos manuales
        }
        
        # Simular mensaje para ejecutar acción
        fake_message = type('obj', (object,), {
            'author': miembro,
            'guild': interaction.guild,
            'channel': interaction.channel,
            'content': f"[Castigo ordenado por {interaction.user.name}]"
        })
        
        # Ejecutar acción
        success, action_message = await ejecutar_accion_discord(fake_message, decision)
        
        if success:
            # Generar comentario sobre el castigo
            comentario_context = f"Acabo de castigar a {miembro.name} por {razón}. Haz un comentario breve y aterrador sobre esto."
            comentario, _ = await get_lars_response(
                comentario_context,
                interaction.user.name,
                mood="despectivo",
                max_tokens=80
            )
            
            await interaction.followup.send(f"{action_message}\n\n*{comentario}*")
        else:
            await interaction.followup.send(f"*Lars intenta castigar a {miembro.mention}, pero algo se lo impide. Sus ojos brillan con furia contenida.*")
            
    except Exception as e:
        logger.error(f"Error en comando castigar: {e}")
        await interaction.followup.send("*Las sombras interfieren con mi capacidad de imponer el castigo.*")

# Comando: Diagnóstico
@tree.command(
    name="diagnostico", 
    description="Lars Kremslinger verificará sus poderes administrativos"
)
async def diagnostico_command(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("No se pudo acceder al servidor.")
            return
            
        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            await interaction.followup.send("No se pudo encontrar a Lars en el servidor.")
            return
        
        # Comprobar permisos clave
        permisos = {
            "Administrador": bot_member.guild_permissions.administrator,
            "Expulsar miembros": bot_member.guild_permissions.kick_members,
            "Banear miembros": bot_member.guild_permissions.ban_members,
            "Moderar miembros (timeout)": bot_member.guild_permissions.moderate_members,
            "Gestionar apodos": bot_member.guild_permissions.manage_nicknames,
            "Gestionar mensajes": bot_member.guild_permissions.manage_messages,
            "Gestionar canales": bot_member.guild_permissions.manage_channels,
            "Gestionar roles": bot_member.guild_permissions.manage_roles
        }
        
        # Verificar jerarquía de roles
        roles_superiores = []
        for role in guild.roles:
            if role > bot_member.top_role:
                roles_superiores.append(role.name)
        
        # Crear mensaje de diagnóstico
        mensaje = "**[Diagnóstico de Lars Kremslinger]**\n\n"
        mensaje += "**Permisos:**\n"
        
        for perm_name, perm_value in permisos.items():
            emoji = "✅" if perm_value else "❌"
            mensaje += f"{emoji} {perm_name}\n"
        
        mensaje += f"\n**Rol más alto:** {bot_member.top_role.name}\n"
        
        if roles_superiores:
            mensaje += f"\n**Roles por encima de Lars:**\n"
            for role in roles_superiores:
                mensaje += f"• {role}\n"
            mensaje += "\n*Lars no puede moderar usuarios con estos roles*"
        else:
            mensaje += "\n*Lars tiene el rol más alto en el servidor*"
        
        # Añadir instrucciones
        mensaje += "\n\n**Si Lars no tiene todos los permisos necesarios:**\n"
        mensaje += "1. Asegúrate de que el rol de Lars tenga los permisos marcados como ❌\n"
        mensaje += "2. Mueve el rol de Lars más arriba en la jerarquía de roles\n"
        mensaje += "3. Si sigues teniendo problemas, revisa los logs del bot para ver errores específicos"
        
        await interaction.followup.send(mensaje)
        
    except Exception as e:
        logger.error(f"Error en comando diagnóstico: {e}")
        await interaction.followup.send(f"Error al realizar diagnóstico: {str(e)}")

# Limpieza de historiales
async def clean_history_loop():
    """Limpia historiales inactivos y controla el uso de memoria"""
    last_cleanup_time = time.time()
    
    while True:
        try:
            current_time = time.time()
            # Realizar limpieza completa cada hora
            if current_time - last_cleanup_time >= 3600:
                channels_to_remove = []
                inactive_threshold = current_time - 7200  # 2 horas de inactividad
                
                # Verificar cada canal en el historial
                for channel_id, history in conversation_history.items():
                    if not history:
                        channels_to_remove.append(channel_id)
                        continue
                    
                    # Verificar timestamp del último mensaje si existe
                    if hasattr(history[-1], 'timestamp') and history[-1].timestamp < inactive_threshold:
                        channels_to_remove.append(channel_id)
                
                # Eliminar canales inactivos
                for channel_id in channels_to_remove:
                    del conversation_history[channel_id]
                
                logger.info(f"Limpieza completa de historiales. Canales eliminados: {len(channels_to_remove)}. Canales activos: {len(conversation_history)}")
                last_cleanup_time = current_time
            
            # Verificar tamaño total del historial cada 5 minutos
            elif len(conversation_history) > 50:  # Si hay muchos canales activos
                # Ordenar canales por último acceso y mantener solo los 30 más recientes
                active_channels = sorted(
                    [(channel_id, history[-1].get('timestamp', 0) if history else 0) 
                     for channel_id, history in conversation_history.items()],
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Mantener solo los 30 canales más activos
                channels_to_keep = [channel[0] for channel in active_channels[:30]]
                
                # Eliminar el resto
                for channel_id in list(conversation_history.keys()):
                    if channel_id not in channels_to_keep:
                        del conversation_history[channel_id]
                
                logger.info(f"Limpieza de emergencia. Canales reducidos a 30. Actual: {len(conversation_history)}")
                
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
            logger.error(traceback.format_exc())
        
        await asyncio.sleep(300)  # Comprobar cada 5 minutos

# Setup hook
async def setup_hook():
    client.loop.create_task(clean_history_loop())
    logger.info("Tarea de limpieza iniciada")

client.setup_hook = setup_hook

# Iniciar bot
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
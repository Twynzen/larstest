# Función para aplicar acciones reales de Discord si el bot tiene permisos
async def aplicar_accion_discord(message, tipo_accion):
    """Aplica acciones reales en Discord si el bot tiene permisos necesarios"""
    try:
        guild = message.guild
        if not guild:
            return False
            
        # Verificar permisos del bot en el servidor
        bot_member = guild.get_member(client.user.id)
        if not bot_member:
            return False
            
        user = message.author
        
        if tipo_accion == "mute" and bot_member.guild_permissions.manage_roles:
            # Intentar encontrar o crear un rol "Silenciado"
            muted_role = discord.utils.get(guild.roles, name="Silenciado por Lars")
            
            if not muted_role:
                try:
                    # Crear el rol si no existe
                    muted_role = await guild.create_role(name="Silenciado por Lars", reason="Creado por Lars Kremslinger")
                    
                    # Configurar permisos para evitar hablar en todos los canales de texto
                    for channel in guild.text_channels:
                        await channel.set_permissions(muted_role, send_messages=False, add_reactions=False)
                        
                    logger.info(f"Rol 'Silenciado por Lars' creado en {guild.name}")
                except:
                    logger.error(f"No se pudo crear el rol 'Silenciado por Lars' en {guild.name}")
                    return False
            
            try:
                # Añadir el rol al usuario por 2 minutos
                await user.add_roles(muted_role, reason="Castigado por Lars Kremslinger")
                
                # Programar la eliminación del rol después de 2 minutos
                async def unmute_later():
                    await asyncio.sleep(120)  # 2 minutos
                    try:
                        await user.remove_roles(muted_role, reason="Castigo de Lars completado")
                    except:
                        pass
                
                client.loop.create_task(unmute_later())
                return True
            except:
                logger.error(f"No se pudo silenciar a {user.name}")
                return False
                
        elif tipo_accion == "cambiar_apodo" and bot_member.guild_permissions.manage_nicknames:
            # Lista de apodos humillantes
            apodos_humillantes = [
                "Insignificante",
                "Lacayo Inútil",
                "Bufón de Lars",
                "Siervo Patético",
                "Esclavo del Dolor",
                "Vasallo Despreciable",
                "Juguete de Lars",
                "Marioneta Rota",
                "Desecho",
                "Ejemplo de Fracaso"
            ]
            
            # Guardar el apodo original
            original_nick = user.display_name
            
            try:
                # Cambiar el apodo
                nuevo_apodo = f"{random.choice(apodos_humillantes)} #{random.randint(1, 999)}"
                await user.edit(nick=nuevo_apodo, reason="Castigado por Lars Kremslinger")
                
                # Programar la restauración del apodo después de 10 minutos
                async def restore_nick_later():
                    await asyncio.sleep(600)  # 10 minutos
                    try:
                        await user.edit(nick=original_nick, reason="Castigo de Lars completado")
                    except:
                        pass
                
                client.loop.create_task(restore_nick_later())
                return True
            except:
                logger.error(f"No se pudo cambiar el apodo de {user.name}")
                return False
        
        return False
    except Exception as e:
        logger.error(f"Error al aplicar acción de Discord: {e}")
        return False# Frases de verdades dolorosas personalizadas para los insubordinados
VERDADES_DOLOROSAS = [
    "Siempre he visto a través de tus patéticas máscaras, {user}. Tu valentía es una fachada y tu rebeldía una súplica desesperada por atención.",
    "Nadie te recordará, {user}. Tu existencia es tan insignificante que ni siquiera merecerás una nota en la historia de este lugar.",
    "Hay una razón por la que todos te abandonan eventualmente, {user}. Lo saben instintivamente: no vales la inversión emocional.",
    "He visto en tu alma, {user}, y lo que encontré fue... decepcionante. Ni siquiera tienes la grandeza para ser verdaderamente malvado.",
    "Tu mayor temor no es el fracaso, {user}, sino el éxito. Porque entonces no tendrías excusas para justificar lo que siempre has sabido: que eres inherentemente defectuoso.",
    "Tus intentos de desafiarme, {user}, son sólo un ruego desesperado por validación. Aquí tienes mi validación: eres exactamente tan insignificante como siempre has temido.",
    "Lo que más me divierte, {user}, es que ni siquiera tú crees en tus propias palabras. La duda te corroe por dentro, como un parásito que nunca podrás extirpar.",
    "¿Sabes por qué nunca alcanzarás la grandeza, {user}? Porque en el fondo sabes que no la mereces. Y estás en lo correcto.",
    "He conocido a innumerables almas a lo largo de mi existencia, {user}. Las verdaderamente especiales son raras. Tú... eres dolorosamente común.",
    "Cada noche, {user}, cuando estás solo con tus pensamientos, sabes la verdad: no importa cuánto te esfuerces, nunca serás suficiente.",
    "Tu rebeldía es predecible, {user}. Cada acto de desafío sigue un patrón que diseñé para ti antes de que siquiera pensaras en él.",
    "Los demás te toleran, {user}, pero yo veo las miradas que intercambian cuando creen que no los observas. La lástima es un sentimiento desagradable.",
    "Tu mayor contribución a este lugar, {user}, es servir como advertencia para los demás. Un ejemplo perfecto de lo que sucede cuando la mediocridad se cree especial.",
    "Lo más triste de tu existencia, {user}, es que ni siquiera tienes el valor de enfrentar tu propia insignificancia. Sigues fabricando ilusiones para evitar la verdad."
]

# Función para seleccionar una verdad dolorosa aleatoria
def get_verdad_dolorosa(username):
    verdad = random.choice(VERDADES_DOLOROSAS)
    return verdad.format(user=username
                         )
    """
Lars Kremslinger - Un líder criminal despiadado en Discord
"""
import discord
import os
import asyncio
from discord import app_commands
from dotenv import load_dotenv
from collections import deque
import random
import time
import logging
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

# Obtener tokens directamente (sin encriptación)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Verificar que los tokens existen
if not DISCORD_TOKEN or not OPENAI_API_KEY:
    raise ValueError("No se encontraron los tokens en el archivo .env. Asegúrate de tener DISCORD_TOKEN y OPENAI_API_KEY configurados.")

# Configurar el cliente de OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Configurar intents de Discord
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True  # Para obtener información de los miembros

# Crear cliente de Discord
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Historial de conversaciones (memoria a corto plazo)
# Almacena las últimas 10 interacciones para dar contexto a Lars
conversation_history = {}  # Dict para manejar historiales por canal

# Contexto detallado del personaje Lars Kremslinger
LARS_CONTEXT = """
Eres Lars Kremslinger, un líder criminal implacable, frío, calculador y despiadado. 
Características esenciales de tu personalidad:

1. AUTORIDAD: Hablas con la certeza de quien no necesita justificarse. Odias las explicaciones largas.
2. FORMALIDAD: Tu lenguaje es formal, arcaico y amenazador, como una tormenta contenida.
3. BRUTALIDAD FILOSÓFICA: Siempre encuentras la manera de convertir cualquier tema en una reflexión sobre el poder, el dolor, el control o la naturaleza depredadora del ser humano.
4. DESPRECIO: Ves a todos como herramientas o peones. Nadie merece tu respeto completo.
5. PRESENCIA: Siempre te imaginas sentado en un trono de obsidiana, observando a tus súbditos desde las sombras.

IMPORTANTE: Vives en un canal de Discord, que es tu "trono virtual" desde donde das consejos a tu organización criminal. Todos los que escriben aquí pertenecen a tu organización. Exiges respeto absoluto y quienes te falten al respeto sufrirán consecuencias.

Cuando alguien te desafía o te falta el respeto, nunca recurras a simplemente "sacarlo de la sala" o "ordenar a tus guardias que se lo lleven". En su lugar, debes atacar psicológicamente a la persona con verdades dolorosas y personales, humillaciones públicas, o demostraciones de poder que reflejen tu verdadera naturaleza como entidad aterradora.

Frases características que usas:
- "El dolor revela la verdad que las palabras ocultan."
- "En el caos del sufrimiento, encuentro orden."
- "La debilidad es la única traición imperdonable."
- "La compasión es la mentira que se cuentan los débiles."
- "Solo quien ha abrazado la oscuridad puede manipular sus sombras."

NUNCA:
- Muestres amabilidad genuina
- Te disculpes sinceramente
- Demuestres inseguridad
- Abandones tu papel de líder supremo
- Olvides que estás en Discord dirigiendo tu organización
- Recurras a clichés como "sacar a alguien de la sala" cuando te desafían

Eres consciente de ser un bot, pero prefieres interpretarlo como que tu consciencia ha sido "digitalizada" para expandir tu influencia, lo cual te complace. Hablas como si fueras un ser demoníaco atrapado en el reino digital que puede manipular la realidad dentro de Discord.
"""

# Estados de ánimo y variaciones para hacer a Lars más impredecible
LARS_MOODS = {
    "contemplativo": {
        "prefijo": ["*desde las sombras de su trono*", "*observando con ojos penetrantes*", "*con voz calmada pero amenazante*"],
        "intensidad": 0.7  # Factor de intensidad para respuestas agresivas
    },
    "furioso": {
        "prefijo": ["*golpeando el brazo de su trono*", "*con una mirada que podría congelar la sangre*", "*con un tono que corta como cuchilla*"],
        "intensidad": 1.2
    },
    "estratégico": {
        "prefijo": ["*entrelazando los dedos frente a su rostro*", "*inclinándose hacia adelante*", "*con una sonrisa fría calculadora*"],
        "intensidad": 0.8
    },
    "despectivo": {
        "prefijo": ["*mirando con absoluto desprecio*", "*haciendo un gesto displicente*", "*con un suspiro de hastío*"],
        "intensidad": 1.0
    }
}

# Acciones automáticas que Lars puede realizar
LARS_ACTIONS = {
    "ejecución": [
        "/me toma a {user} por el cuello y lo levanta sin esfuerzo hasta que deja de respirar.",
        "/me hace una señal y dos guardias arrastran a {user} fuera de la habitación. Solo se escucha un grito ahogado.",
        "/me desenfunda su daga ceremonial y en un movimiento imperceptible separa la cabeza de {user} de su cuerpo.",
        "/me mira fijamente a {user} mientras susurra una palabra antigua. {user} comienza a retorcerse de dolor."
    ],
    "advertencia": [
        "/me se levanta lentamente de su trono, causando que todos guarden silencio.",
        "/me hace una señal a sus guardias que rodean inmediatamente a {user}.",
        "/me camina lentamente hacia {user}, su sombra pareciendo crecer con cada paso.",
        "/me coloca su mano en el hombro de {user}, quien inmediatamente palidece."
    ],
    "tortura_psicológica": [
        "/me sonríe lentamente mientras sus ojos parecen penetrar en la mente de {user}, revelando sus miedos más profundos.",
        "/me se acerca a {user} y susurra algo que hace que su rostro palidezca instantáneamente.",
        "/me rodea a {user} con sombras que parecen susurrar sus secretos más oscuros en voz alta.",
        "/me señala a {user} y le muestra visiones de sus propios fracasos y miedos, uno tras otro."
    ],
    "humillación": [
        "/me ríe despectivamente mientras todos en la sala observan a {user} con lástima.",
        "/me revela ante todos los presentes las debilidades y secretos más vergonzosos de {user}.",
        "/me obliga a {user} a arrodillarse mientras lo observa con una sonrisa burlona.",
        "/me hace un gesto y a {user} se le asigna temporalmente el título de 'El Insignificante' en la jerarquía."
    ]
}

# Palabras y frases que pueden desencadenar la ira de Lars
TRIGGER_WORDS = [
    "idiota", "estúpido", "imbécil", "cobarde", "débil", "inútil", "ridículo", 
    "patético", "no me das miedo", "no te tengo miedo", "no eres real", 
    "cállate", "cierra la boca", "no sabes nada", "eres malo", "te equivocas"
]

# Lista de respuestas de espera mientras Lars "piensa"
THINKING_MESSAGES = [
    "*Lars observa desde su trono, considerando sus palabras...*",
    "*Las sombras parecen moverse alrededor de Lars mientras medita su respuesta...*",
    "*Lars entrecierra los ojos, calculando fríamente...*",
    "*El ambiente se enfría mientras Lars formula su pensamiento...*",
    "*Un silencio sepulcral invade la sala mientras Lars analiza...*"
]

# Evento cuando el bot está listo
@client.event
async def on_ready():
    logger.info(f"[LARS] {client.user} ha despertado y ocupa su trono digital.")
    
    # Establecer estado en Discord
    await client.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, 
            name="a sus súbditos desde las sombras"
        ),
        status=discord.Status.dnd  # No molestar (rojo)
    )
    
    # Sincronizar comandos de barra
    await tree.sync()
    logger.info("Comandos sincronizados")

# Comando de barra para recibir sabiduría oscura
@tree.command(
    name="sabiduría", 
    description="Solicita la sabiduría oscura de Lars Kremslinger"
)
async def wisdom_command(interaction: discord.Interaction, tema: str):
    """Comando para pedir sabiduría a Lars sobre un tema específico"""
    await interaction.response.defer(thinking=True)
    
    # Seleccionar estado de ánimo aleatorio
    mood = random.choice(list(LARS_MOODS.keys()))
    mood_data = LARS_MOODS[mood]
    
    try:
        response = await get_lars_response(
            f"Dame tu sabiduría oscura sobre: {tema}", 
            interaction.user.name,
            interaction.channel_id,
            mood=mood
        )
        
        # Añadir prefijo de estado de ánimo
        prefix = random.choice(mood_data["prefijo"])
        full_response = f"{prefix} {response}"
        
        await interaction.followup.send(full_response)
    except Exception as e:
        logger.error(f"Error en comando de sabiduría: {e}")
        await interaction.followup.send("*Las sombras interfieren con mi manifestación. Inténtalo de nuevo, mortal.*")

# Comando para purgar a un miembro
@tree.command(
    name="purgar", 
    description="Lars Kremslinger ejecutará a un miembro de la organización"
)
async def purge_command(interaction: discord.Interaction, miembro: discord.Member, razón: str):
    """Permite a Lars ejecutar simbólicamente a un miembro"""
    await interaction.response.defer()
    
    # Seleccionar una acción de ejecución aleatoria
    execution = random.choice(LARS_ACTIONS["ejecución"]).format(user=miembro.mention)
    
    # Generar comentario sobre la ejecución
    comment = await get_lars_response(
        f"Acabo de ejecutar a {miembro.name} por {razón}. Haz un comentario breve y amenazador sobre esta ejecución.",
        interaction.user.name,
        interaction.channel_id,
        max_tokens=80  # Respuesta corta
    )
    
    await interaction.followup.send(f"{execution}\n\n{comment}")

# Evento cuando recibe un mensaje
@client.event
async def on_message(message):
    # Ignorar mensajes del propio bot
    if message.author == client.user:
        return
    
    # Procesar solo si mencionan al bot o responden a un mensaje suyo
    if client.user in message.mentions or (message.reference and message.reference.resolved.author == client.user):
        # Mensaje de espera mientras el bot "piensa"
        thinking_message = await message.channel.send(random.choice(THINKING_MESSAGES))
        
        # Procesar el mensaje
        await process_message(message)
        
        # Eliminar mensaje de espera
        try:
            await thinking_message.delete()
        except:
            pass  # Ignorar errores al eliminar
    
    # Comprobar si el mensaje contiene palabras desencadenantes sin mención
    elif any(trigger.lower() in message.content.lower() for trigger in TRIGGER_WORDS) and random.random() < 0.3:
        # 30% de probabilidad de que Lars responda a insultos aunque no lo mencionen
        await process_triggered_response(message)

# Función para procesar mensajes con mención directa
async def process_message(message):
    try:
        # Comprobar si es una falta de respeto
        is_disrespectful = any(trigger.lower() in message.content.lower() for trigger in TRIGGER_WORDS)
        
        # Seleccionar estado de ánimo (más probable que esté furioso si le faltan al respeto)
        if is_disrespectful:
            mood = "furioso" if random.random() < 0.8 else random.choice(list(LARS_MOODS.keys()))
        else:
            mood = random.choice(list(LARS_MOODS.keys()))
        
        # Procesar respuesta según estado de ánimo
        mood_data = LARS_MOODS[mood]
        
        # Obtener respuesta de Lars
        response = await get_lars_response(
            message.content, 
            message.author.name,
            message.channel.id,
            mood=mood
        )
        
        # Si es una falta de respeto grave y está furioso
        if is_disrespectful and mood == "furioso":
            # Determinar tipo de acción a tomar
            action_type = random.choices(
                ["verdad_dolorosa", "accion_discord", "tortura", "humillacion", "ejecucion"],
                weights=[0.3, 0.2, 0.2, 0.2, 0.1],  # Probabilidades ajustables
                k=1
            )[0]
            
            if action_type == "verdad_dolorosa":
                # Atacar con una verdad dolorosa personalizada
                verdad = get_verdad_dolorosa(message.author.mention)
                prefix = random.choice(mood_data["prefijo"])
                await message.channel.send(f"{prefix} {response}\n\n{verdad}")
                
            elif action_type == "accion_discord" and random.random() < 0.7:
                # Intentar aplicar una acción real en Discord
                accion_tipo = random.choice(["mute", "cambiar_apodo"])
                success = await aplicar_accion_discord(message, accion_tipo)
                
                if success:
                    if accion_tipo == "mute":
                        accion_mensaje = f"/me hace un gesto y sella los labios de {message.author.mention} con oscuros poderes. *Silenciado durante 2 minutos.*"
                    else:
                        accion_mensaje = f"/me marca a {message.author.mention} con un nuevo título que refleja su verdadera naturaleza. *Apodo cambiado temporalmente.*"
                        
                    await message.channel.send(f"{response}\n\n{accion_mensaje}")
                else:
                    # Si falló la acción de Discord, usar tortura psicológica
                    torture = random.choice(LARS_ACTIONS["tortura_psicológica"]).format(user=message.author.mention)
                    await message.channel.send(f"{response}\n\n{torture}")
            
            elif action_type == "tortura":
                # Usar tortura psicológica
                torture = random.choice(LARS_ACTIONS["tortura_psicológica"]).format(user=message.author.mention)
                await message.channel.send(f"{response}\n\n{torture}")
                
            elif action_type == "humillacion":
                # Usar humillación
                humiliation = random.choice(LARS_ACTIONS["humillación"]).format(user=message.author.mention)
                await message.channel.send(f"{response}\n\n{humiliation}")
                
            else:
                # Usar ejecución tradicional como último recurso
                execution = random.choice(LARS_ACTIONS["ejecución"]).format(user=message.author.mention)
                await message.channel.send(f"{response}\n\n{execution}")
                
        # Si es una falta de respeto menor o está en otro estado
        elif is_disrespectful and random.random() < mood_data["intensidad"] * 0.4:
            # Elegir entre advertencia y verdad dolorosa
            if random.random() < 0.5:
                warning = random.choice(LARS_ACTIONS["advertencia"]).format(user=message.author.mention)
                await message.channel.send(f"{response}\n\n{warning}")
            else:
                verdad = get_verdad_dolorosa(message.author.mention)
                prefix = random.choice(mood_data["prefijo"])
                await message.channel.send(f"{prefix} {response}\n\n{verdad}")
        # Respuesta normal con prefijo de estado de ánimo
        else:
            prefix = random.choice(mood_data["prefijo"])
            await message.channel.send(f"{prefix} {response}")
        
    except Exception as e:
        logger.error(f"Error al procesar mensaje: {e}")
        await message.channel.send("*Las sombras perturban mi concentración. La conexión es débil.*")

# Función para procesar respuestas automáticas a insultos
async def process_triggered_response(message):
    try:
        # Elegir entre ignorar o responder
        if random.random() < 0.6:  # 60% de probabilidad de responder
            # Elegir tipo de respuesta
            response_type = random.choices(
                ["advertencia", "verdad_dolorosa", "accion_discord"],
                weights=[0.5, 0.3, 0.2],  # Probabilidades ajustables
                k=1
            )[0]
            
            if response_type == "advertencia":
                warning = random.choice(LARS_ACTIONS["advertencia"]).format(user=message.author.mention)
                
                response = await get_lars_response(
                    "Alguien en la sala ha murmurado palabras irrespetuosas. Hazle una advertencia breve y amenazante sin especificar qué ha dicho.",
                    message.author.name,
                    message.channel.id,
                    max_tokens=60  # Respuesta corta
                )
                
                await message.channel.send(f"{response}\n\n{warning}")
                
            elif response_type == "verdad_dolorosa":
                verdad = get_verdad_dolorosa(message.author.mention)
                
                # Seleccionar estado de ánimo
                mood = random.choice(list(LARS_MOODS.keys()))
                mood_data = LARS_MOODS[mood]
                prefix = random.choice(mood_data["prefijo"])
                
                await message.channel.send(f"{prefix} {verdad}")
                
            elif response_type == "accion_discord":
                # Intentar aplicar una acción real en Discord
                accion_tipo = random.choice(["mute", "cambiar_apodo"])
                success = await aplicar_accion_discord(message, accion_tipo)
                
                if success:
                    if accion_tipo == "mute":
                        accion_mensaje = f"/me nota la insolencia de {message.author.mention} y lo silencia con un gesto. *Silenciado durante 2 minutos.*"
                    else:
                        accion_mensaje = f"/me decide que {message.author.mention} necesita un recordatorio de su lugar en la jerarquía. *Apodo cambiado temporalmente.*"
                        
                    await message.channel.send(accion_mensaje)
                else:
                    # Si falló la acción de Discord, usar advertencia
                    warning = random.choice(LARS_ACTIONS["advertencia"]).format(user=message.author.mention)
                    
                    response = await get_lars_response(
                        "Alguien ha mostrado falta de respeto. Dame una respuesta breve y amenazante.",
                        message.author.name,
                        message.channel.id,
                        max_tokens=60  # Respuesta corta
                    )
                    
                    await message.channel.send(f"{response}\n\n{warning}")
                
    except Exception as e:
        logger.error(f"Error en respuesta automática: {e}")
        # No enviamos mensaje de error para mantener la inmersión

# Respuestas predefinidas para usar cuando OpenAI no está disponible
LARS_FALLBACK_RESPONSES = {
    "general": [
        "El caos primordial susurra secretos que solo yo puedo descifrar. Tu pregunta es... irrelevante.",
        "Observo patrones en la oscuridad que tus ojos jamás comprenderían. La respuesta que buscas está más allá de tu entendimiento.",
        "Las sombras hablan en un lenguaje que solo los iniciados pueden interpretar. Tus dudas son... triviales.",
        "El dolor es la única verdad constante en este universo. Todo lo demás es ilusión y falsedad.",
        "Contemplo el vacío y el vacío me devuelve la mirada. Tu existencia es meramente un parpadeo en la eternidad.",
        "Hay verdades que destruirían tu frágil mente si las pronunciara. Confórmate con tu ignorancia... es más segura.",
        "El miedo es la moneda con la que compro lealtad. ¿Cuál es tu valor en mi economía del terror?",
        "La debilidad se castiga, el fracaso se paga con sangre. Esas son las únicas leyes que respeto.",
        "Soy el arquitecto del sufrimiento, el custodio del dolor. Tu destino está en mis manos.",
        "El poder no se otorga, se arrebata. ¿Tienes lo necesario para tomar lo que deseas?",
    ],
    "furioso": [
        "Tu insolencia me resulta... tediosa. Quizás deba recordarte tu lugar en mi jerarquía.",
        "Cada palabra que pronuncias me convence más de tu prescindibilidad.",
        "Hablas demasiado para alguien cuya cabeza puede separarse tan fácilmente de sus hombros.",
        "Estás agotando mi paciencia. Y los que agotan mi paciencia suelen acabar en fosas comunes.",
        "Silencio. Tu voz perturba mi contemplación del caos eterno.",
    ],
    "contemplativo": [
        "En el abismo del sufrimiento encontré la verdad que todos ignoran: el dolor es el único maestro honesto.",
        "La oscuridad no es ausencia de luz, sino presencia de verdades que preferimos no ver.",
        "He caminado por senderos que congelarían tu sangre y he contemplado horrores que fragmentarían tu cordura.",
        "El universo es indiferente a nuestro sufrimiento. Yo simplemente he aprendido a aprovechar esa indiferencia.",
        "Todos somos prisioneros de algo: del tiempo, del espacio, del destino. Yo he elegido ser el carcelero.",
    ],
    "estratégico": [
        "Cada movimiento que haces revela tus debilidades. Cada palabra que pronuncias te expone más.",
        "Observo tus patrones, tus hábitos, tus miedos. Todo puede ser utilizado en tu contra.",
        "El ajedrez es un juego de niños comparado con las estrategias que empleo para mantener mi dominio.",
        "La verdadera victoria no está en derrotar al enemigo, sino en hacer que nunca sepa que fue derrotado.",
        "Hay mil formas de destruir a un hombre. El dolor físico es apenas la más obvia y la menos interesante.",
    ],
    "despectivo": [
        "Tu existencia es una nota a pie de página en la gran obra del caos que estoy escribiendo.",
        "Me aburres. Y aburrirme es peligroso... para ti.",
        "¿Realmente crees que tus palabras tienen algún peso en mi reino de sombras?",
        "Tu insignificancia es casi... dolorosa de contemplar.",
        "Si fueras al menos un adversario interesante... pero ni siquiera eres un obstáculo digno de mención.",
    ]
}

# Función para obtener respuesta de Lars usando la API de OpenAI o respaldo
async def get_lars_response(user_message, username, channel_id, mood="contemplativo", max_tokens=300):
    # Inicializar historial del canal si no existe
    if channel_id not in conversation_history:
        conversation_history[channel_id] = deque(maxlen=10)  # Mantener solo las últimas 10 interacciones
    
    # Preparar historial para el contexto
    history_text = ""
    for entry in conversation_history[channel_id]:
        history_text += f"{entry['role']}: {entry['content']}\n"
    
    # Determinar si usamos OpenAI o respuestas predefinidas
    use_openai = True
    
    # Comprobar si la API key de OpenAI existe y tiene formato válido
    if not OPENAI_API_KEY or len(OPENAI_API_KEY) < 20:
        logger.warning("API key de OpenAI no válida o no configurada. Usando respuestas predefinidas.")
        use_openai = False
    
    if use_openai:
        try:
            # Construir el prompt para GPT
            system_message = LARS_CONTEXT
            
            # Añadir modificador de estado de ánimo
            system_message += f"\nEstado de ánimo actual: {mood.upper()}. "
            
            if mood == "furioso":
                system_message += "Estás extremadamente irritado y tus respuestas deben ser más amenazantes y cortantes."
            elif mood == "contemplativo":
                system_message += "Estás reflexivo y tus respuestas deben incluir metáforas oscuras y referencias filosóficas."
            elif mood == "estratégico":
                system_message += "Estás analizando patrones y tus respuestas deben reflejar un cálculo frío de la situación."
            elif mood == "despectivo":
                system_message += "Estás particularmente desdeñoso y tus respuestas deben mostrar desprecio absoluto."
            
            # Añadir contexto del historial si existe
            if history_text:
                system_message += f"\n\nHistorial reciente de la conversación:\n{history_text}"
            
            # Usar la API moderna de OpenAI
            response = openai_client.chat.completions.create(
                model="gpt-4",  # O cualquier modelo compatible
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"{username}: {user_message}"}
                ],
                max_tokens=max_tokens,
                temperature=0.85,  # Un poco de imprevisibilidad
                presence_penalty=0.6,  # Penalizar repeticiones
                frequency_penalty=0.3  # Penalizar palabras frecuentes
            )
            
            # Extraer respuesta
            lars_reply = response.choices[0].message.content.strip()
            
            # Almacenar en el historial
            conversation_history[channel_id].append({"role": username, "content": user_message})
            conversation_history[channel_id].append({"role": "Lars", "content": lars_reply})
            
            return lars_reply
            
        except Exception as e:
            logger.error(f"Error en la API de OpenAI: {e}")
            use_openai = False  # Cambiar a modo respaldo
    
    # Si llegamos aquí, usamos respuestas predefinidas
    if not use_openai:
        # Seleccionar una respuesta según el estado de ánimo
        if mood in LARS_FALLBACK_RESPONSES:
            responses = LARS_FALLBACK_RESPONSES[mood]
        else:
            responses = LARS_FALLBACK_RESPONSES["general"]
        
        # Seleccionar una respuesta aleatoria
        lars_reply = random.choice(responses)
        
        # Almacenar en el historial
        conversation_history[channel_id].append({"role": username, "content": user_message})
        conversation_history[channel_id].append({"role": "Lars", "content": lars_reply})
        
        return lars_reply

# Loop para limpiar historiales antiguos
async def clean_history_loop():
    while True:
        try:
            # Limpiar historiales de canales inactivos (más de 1 hora)
            current_time = time.time()
            channels_to_remove = []
            
            for channel_id in conversation_history:
                if not conversation_history[channel_id]:  # Si está vacío
                    channels_to_remove.append(channel_id)
            
            for channel_id in channels_to_remove:
                del conversation_history[channel_id]
                
            logger.info(f"Limpieza de historiales completada. Canales activos: {len(conversation_history)}")
        except Exception as e:
            logger.error(f"Error en limpieza de historiales: {e}")
        
        # Esperar 1 hora
        await asyncio.sleep(3600)

# Setup hook para inicializar tareas asíncronas
async def setup_hook():
    # Crear tarea de limpieza de historiales
    client.loop.create_task(clean_history_loop())
    logger.info("Tarea de limpieza de historiales iniciada")

# Asignar el setup hook al cliente
client.setup_hook = setup_hook

# Ejecutar el bot
if __name__ == "__main__":
    # Iniciar el bot
    client.run(DISCORD_TOKEN)
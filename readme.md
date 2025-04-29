# Lars Kremslinger - Bot de Discord

Un bot de Discord que interpreta a Lars Kremslinger, un líder criminal despiadado que administra su organización desde su trono digital.

## Características

- Personalidad oscura y amenazante
- Respuestas breves y contundentes usando GPT-4
- Capacidades reales de administración
- Diferentes estados de ánimo y respuestas variadas
- Memoria de conversaciones por canal

## Capacidades administrativas

El bot puede ejecutar acciones reales en Discord si tiene los permisos necesarios:

- **Timeout**: Silenciar temporalmente usuarios
- **Cambiar apodos**: Asignar temporalmente apodos humillantes
- **Eliminar mensajes**: Borrar mensajes irrespetuosos
- **Expulsar usuarios**: Echar a alguien del servidor
- **Silenciar canales**: Impedir temporalmente que todos hablen en un canal

## Instalación

1. Clona este repositorio o descarga `lars.py`
2. Instala las dependencias:
   ```
   pip install discord.py python-dotenv openai
   ```
3. Crea un archivo `.env` con tus tokens (ver `.env.example`)
4. Ejecuta el bot:
   ```
   python lars.py
   ```

## Configuración

Debes crear un archivo `.env` con el siguiente contenido:

```
# Token de Discord (crea uno en https://discord.com/developers/applications)
DISCORD_TOKEN=tu_token_de_discord_aquí

# API Key de OpenAI (obténla en https://platform.openai.com/api-keys)
OPENAI_API_KEY=tu_api_key_de_openai_aquí
```

## Uso

### Comandos básicos

- **@Lars Kremslinger [mensaje]**: Interactúa directamente con Lars
- **/sabiduría [tema]**: Solicita la sabiduría oscura de Lars sobre un tema
- **/castigar [usuario] [tipo] [razón]**: Castiga a un usuario (requiere permisos)
- **/silencio [minutos] [razón]**: Silencia temporalmente el canal (requiere permisos)

### Tipos de castigo

Al usar el comando `/castigar`, puedes especificar el tipo:
- `expulsar`: Expulsa al usuario del servidor
- `timeout`: Silencia temporalmente al usuario (10 minutos)
- `apodo`: Cambia el apodo del usuario temporalmente (10 minutos)

## Ejemplo

```
Usuario: @Lars Kremslinger, ¿qué piensas de la lealtad?

Lars: *con voz calmada pero amenazante* La lealtad es una cadena que los débiles desean y los fuertes manipulan. En mi reino, solo exige lealtad quien teme ser traicionado.
```

## Permisos requeridos

Para que todas las funcionalidades administrativas funcionen, Lars necesita estos permisos:

- Gestionar roles
- Expulsar miembros
- Gestionar apodos
- Gestionar mensajes
- Gestionar canales
- Temporizador de miembros

## Consejos

- Lars responde mejor cuando se le habla con respeto
- Cada falta de respeto aumenta las posibilidades de un castigo
- Si Lars no puede ejecutar acciones administrativas, responderá con mensajes intimidantes
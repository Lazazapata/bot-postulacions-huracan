# Bot de Postulaciones — Mafia Club Atlético Huracán

Bot de Discord con:

- `/postular` → abre un formulario (Nombre IC, Edad OOC, Horas diarias, motivo, experiencia).
- `/panel-postulacion` → publica un mensaje fijo con un botón **"Postularme"** que abre el mismo formulario (para no depender de que la gente sepa el comando).
- Al enviar el formulario, se postea la ficha en el canal de staff, mencionando el rol encargado, con botones **Postulación Aprobada** / **Rechazar**.
- Solo el rol de staff puede aprobar/rechazar. Al resolver, se le manda un DM al postulante y (opcional) se le asigna un rol si fue aprobado.

---

## 1. Crear la aplicación del bot

1. Entrá a https://discord.com/developers/applications
2. **New Application** → ponele un nombre (ej. "Bot Huracán") → **Create**.
3. En el menú de la izquierda, andá a **Bot**.
4. Activá estos dos toggles (son obligatorios para que el bot funcione bien):
   - **Server Members Intent**
5. Click en **Reset Token** → **Copy**. Guardá ese token, lo vas a pegar en el `.env` (paso 4). **No lo compartas con nadie**, quien lo tenga puede controlar tu bot.

## 2. Invitar el bot a tu servidor

1. En el menú izquierdo, andá a **OAuth2 → URL Generator**.
2. En **Scopes**, marcá: `bot` y `applications.commands`.
3. En **Bot Permissions**, marcá al menos:
   - Send Messages
   - Embed Links
   - Read Message History
   - Manage Roles *(solo si vas a usar la asignación automática de rol al aprobar)*
4. Copiá la URL que se genera abajo, pegala en el navegador, elegí tu servidor y **Autorizar**.

## 3. Conseguir los IDs que pide el `.env`

1. En Discord: **Configuración de Usuario → Avanzado → Modo Desarrollador** (activalo).
2. Clic derecho sobre el ícono de tu servidor → **Copiar ID** → es tu `GUILD_ID`.
3. Clic derecho sobre el canal donde quer�s que lleguen las postulaciones → **Copiar ID** → es tu `STAFF_CHANNEL_ID`.
4. Clic derecho sobre el rol de staff/encargados (en Configuración del servidor → Roles, o sobre un miembro que lo tenga) → **Copiar ID** → es tu `STAFF_ROLE_ID`.
5. (Opcional) Si querés que al aprobar se asigne un rol automáticamente, copiá el ID de ese rol → `APPROVED_ROLE_ID`.

> Importante si usás `APPROVED_ROLE_ID`: en **Configuración del servidor → Roles**, el rol del bot tiene que estar **por arriba** del rol que le vas a pedir que asigne. Si no, Discord no lo deja.

## 4. Instalar y configurar

Necesitás [Python 3.10 o superior](https://www.python.org/downloads/) instalado.

```bash
cd bot_mafia
pip install -r requirements.txt
cp .env.example .env
```

Abrí el archivo `.env` y completá `DISCORD_TOKEN`, `GUILD_ID`, `STAFF_CHANNEL_ID`, `STAFF_ROLE_ID` (y `APPROVED_ROLE_ID` si querés usarlo).

## 5. Correr el bot

```bash
python bot.py
```

Si todo salió bien, en la consola vas a ver:

```
Conectado como Bot Huracán#0000 (ID: ...)
Comandos sincronizados.
```

## 6. Usarlo en Discord

- Andá al canal donde querés el botón fijo y escribí `/panel-postulacion` (solo lo ven/usan quienes tengan el rol de staff o sean admins). Esto deja publicado el mensaje con el botón **"Postularme"**.
- Cualquier usuario también puede escribir directamente `/postular`.
- Cuando alguien completa el formulario, la ficha aparece en el canal de staff (`STAFF_CHANNEL_ID`) con los botones de **Aprobar/Rechazar**.

## Personalización rápida

Todo lo que es texto, colores y nombres está al principio de `bot.py`, en la sección **"Textos / branding"**: podés cambiar el nombre de la facción, los colores del embed y los mensajes de DM sin tocar el resto del código.

Las 5 preguntas del formulario están en la clase `PostulacionModal` — se puede agregar, sacar o renombrar campos ahí (Discord permite máximo 5 campos por formulario).

## Notas

- El bot tiene que quedar corriendo (`python bot.py`) todo el tiempo para que funcione; si cerrás la consola, se desconecta. Para tenerlo online 24/7 hace falta alojarlo en un servidor/VPS (o una PC que quede siempre prendida) — si querés, te ayudo a configurar eso después.
- Si reiniciás el bot, el botón "Postularme" de mensajes ya publicados sigue funcionando. Los botones de Aprobar/Rechazar de postulaciones que quedaron pendientes **antes** de un reinicio del bot dejan de responder (limitación de esta versión simple); lo normal es revisarlas apenas llegan.

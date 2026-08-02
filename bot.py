# -*- coding: utf-8 -*-
"""
Bot de Discord - Postulaciones
Mafia Club Atlético Huracán / El Bajo Roleplay

Qué hace:
- Comando /postular  -> abre un formulario (modal) con 5 preguntas.
- Comando /panel-postulacion -> publica un mensaje fijo con un botón "Postularme"
  (hace lo mismo que /postular pero sin necesidad de escribir el comando).
- Al enviar el formulario, se postea una ficha (embed) en el canal de staff,
  mencionando el rol encargado, con botones "Postulación Aprobada" / "Rechazar".
- Solo miembros con el rol de staff (STAFF_ROLE_ID) pueden aprobar/rechazar.
- Al aprobar o rechazar: se edita la ficha, se le manda un DM al postulante,
  y (opcional) se le asigna un rol si fue aprobado.

Toda la configuración se hace en el archivo .env (ver .env.example).
"""

import os
import datetime

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # opcional, para que los comandos aparezcan al instante
STAFF_CHANNEL_ID = int(os.getenv("STAFF_CHANNEL_ID", "0"))
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID", "0"))
APPROVED_ROLE_ID = int(os.getenv("APPROVED_ROLE_ID", "0"))  # opcional

# ------------------------------------------------------------------
# Textos / branding — cambiá esto a gusto
# ------------------------------------------------------------------
NOMBRE_FACCION = "MAFIA CLUB ATLÉTICO HURACÁN"
COLOR_EMBED = discord.Color.from_str("#C8101E")   # rojo Huracán
COLOR_APROBADA = discord.Color.from_str("#2ECC71")  # verde
COLOR_RECHAZADA = discord.Color.from_str("#E74C3C")  # rojo error

TITULO_FORM = f"Nueva Postulación - {NOMBRE_FACCION}"

MENSAJE_CONFIRMACION = (
    "¡Tu postulación fue enviada! Te vamos a avisar por DM cuando la revisemos."
)
MENSAJE_APROBADA_DM = (
    f"🎉 ¡Felicitaciones! Tu postulación a **{NOMBRE_FACCION}** fue **APROBADA**.\n"
    "En breve un miembro del staff se va a contactar con vos para los siguientes pasos."
)
MENSAJE_RECHAZADA_DM = (
    f"❌ Tu postulación a **{NOMBRE_FACCION}** fue **RECHAZADA** en esta ocasión.\n"
    "Podés volver a postularte más adelante."
)

# ------------------------------------------------------------------
# Setup del bot
# ------------------------------------------------------------------
intents = discord.Intents.default()
intents.members = True  # necesario para asignar roles / buscar miembros

bot = commands.Bot(command_prefix="!", intents=intents)


# ------------------------------------------------------------------
# Formulario (Modal)
# ------------------------------------------------------------------
class PostulacionModal(discord.ui.Modal, title=TITULO_FORM[:45]):
    nombre_ic = discord.ui.TextInput(
        label="Nombre IC",
        placeholder="Nombre y apellido del personaje",
        style=discord.TextStyle.short,
        max_length=100,
        required=True,
    )
    edad_ooc = discord.ui.TextInput(
        label="Edad (OOC)",
        placeholder="Tu edad real",
        style=discord.TextStyle.short,
        max_length=3,
        required=True,
    )
    horas = discord.ui.TextInput(
        label="Horas diarias dedicadas",
        placeholder="Ej: 3 a 4",
        style=discord.TextStyle.short,
        max_length=50,
        required=True,
    )
    motivo = discord.ui.TextInput(
        label="¿Por qué entrar a la mafia?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
    )
    experiencia = discord.ui.TextInput(
        label="¿Ya fuiste de la mafia alguna vez?",
        style=discord.TextStyle.short,
        max_length=200,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        staff_channel = interaction.client.get_channel(STAFF_CHANNEL_ID)
        if staff_channel is None:
            await interaction.response.send_message(
                "⚠️ No se encontró el canal de staff. Avisá a un administrador "
                "(revisar STAFF_CHANNEL_ID en el .env).",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="Nueva Postulación",
            description=f"El usuario {interaction.user.mention} ha enviado una nueva postulación.",
            color=COLOR_EMBED,
            timestamp=datetime.datetime.now(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Nombre IC", value=str(self.nombre_ic), inline=True)
        embed.add_field(name="Edad (OOC)", value=str(self.edad_ooc), inline=True)
        embed.add_field(name="Horas diarias dedicadas", value=str(self.horas), inline=True)
        embed.add_field(name="¿Por qué entrar a la mafia?", value=str(self.motivo), inline=False)
        embed.add_field(
            name="¿Ya fuiste de la mafia alguna vez?", value=str(self.experiencia), inline=False
        )
        embed.set_footer(text=f"Sistema de Postulaciones • {NOMBRE_FACCION}")

        mention = f"<@&{STAFF_ROLE_ID}>" if STAFF_ROLE_ID else None
        view = RevisionView(applicant_id=interaction.user.id)
        await staff_channel.send(content=mention, embed=embed, view=view)

        await interaction.response.send_message(MENSAJE_CONFIRMACION, ephemeral=True)


# ------------------------------------------------------------------
# Botones de Aprobar / Rechazar (en el canal de staff)
# ------------------------------------------------------------------
class RevisionView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    async def _es_staff(self, interaction: discord.Interaction) -> bool:
        if STAFF_ROLE_ID == 0:
            return True
        member = interaction.user
        if isinstance(member, discord.Member):
            if member.guild_permissions.administrator:
                return True
            return any(r.id == STAFF_ROLE_ID for r in member.roles)
        return False

    async def _resolver(
        self,
        interaction: discord.Interaction,
        aprobada: bool,
        boton_click: discord.ui.Button,
    ):
        if not await self._es_staff(interaction):
            await interaction.response.send_message(
                "No tenés permiso para revisar postulaciones.", ephemeral=True
            )
            return

        guild = interaction.guild
        applicant = guild.get_member(self.applicant_id) if guild else None

        # Editar el embed original
        embed = interaction.message.embeds[0]
        estado = "✅ Aprobada" if aprobada else "❌ Rechazada"
        embed.color = COLOR_APROBADA if aprobada else COLOR_RECHAZADA
        embed.set_footer(
            text=f"{estado} por {interaction.user.display_name} • "
            f"{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        # Rol automático si fue aprobada
        if aprobada and applicant and APPROVED_ROLE_ID:
            role = guild.get_role(APPROVED_ROLE_ID)
            if role:
                try:
                    await applicant.add_roles(role, reason="Postulación aprobada")
                except discord.Forbidden:
                    await interaction.followup.send(
                        "⚠️ No pude asignar el rol (falta permiso o el rol del bot "
                        "está por debajo del rol a asignar).",
                        ephemeral=True,
                    )

        # DM al postulante
        if applicant:
            try:
                await applicant.send(
                    MENSAJE_APROBADA_DM if aprobada else MENSAJE_RECHAZADA_DM
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "⚠️ No se le pudo enviar el DM al postulante (los tiene cerrados).",
                    ephemeral=True,
                )

    @discord.ui.button(label="Postulación Aprobada", style=discord.ButtonStyle.success)
    async def aprobar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._resolver(interaction, True, button)

    @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.danger)
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._resolver(interaction, False, button)


# ------------------------------------------------------------------
# Botón fijo "Postularme" (para pegar en un canal público)
# ------------------------------------------------------------------
class PanelPostulacionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Postularme",
        style=discord.ButtonStyle.primary,
        emoji="📋",
        custom_id="mafia_panel_postularme",
    )
    async def postularme(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PostulacionModal())


# ------------------------------------------------------------------
# Comandos slash
# ------------------------------------------------------------------
@bot.tree.command(name="postular", description="Enviar una postulación a la mafia")
async def postular(interaction: discord.Interaction):
    await interaction.response.send_modal(PostulacionModal())


@bot.tree.command(
    name="panel-postulacion",
    description="(Staff) Publica el mensaje fijo con el botón de postulación en este canal",
)
async def panel_postulacion(interaction: discord.Interaction):
    if not isinstance(interaction.user, discord.Member) or not (
        interaction.user.guild_permissions.administrator
        or any(r.id == STAFF_ROLE_ID for r in interaction.user.roles)
    ):
        await interaction.response.send_message(
            "No tenés permiso para usar este comando.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"Postulaciones - {NOMBRE_FACCION}",
        description=(
            "Si querés sumarte a la mafia, presioná el botón de abajo y completá "
            "el formulario. Contestá con seriedad, un staff va a revisar tu postulación."
        ),
        color=COLOR_EMBED,
    )
    await interaction.channel.send(embed=embed, view=PanelPostulacionView())
    await interaction.response.send_message("Panel publicado ✅", ephemeral=True)


# ------------------------------------------------------------------
# Arranque
# ------------------------------------------------------------------
@bot.event
async def on_ready():
    # Registrar la view del botón fijo como persistente (sobrevive reinicios del bot,
    # siempre que el mensaje ya exista)
    bot.add_view(PanelPostulacionView())

    if GUILD_ID:
        guild_obj = discord.Object(id=int(GUILD_ID))
        bot.tree.copy_global_to(guild=guild_obj)
        await bot.tree.sync(guild=guild_obj)
    else:
        await bot.tree.sync()

    print(f"Conectado como {bot.user} (ID: {bot.user.id})")
    print("Comandos sincronizados.")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(
            "Falta DISCORD_TOKEN en el archivo .env. Revisá el README para configurarlo."
        )
    bot.run(TOKEN)

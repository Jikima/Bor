import os
import openai
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, art, personas, responses

logger = log.setup_logger(__name__)

def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        logger.info(f'{client.user} is now running!')

    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_message(interaction, message)


    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **Info: Next, the response will be sent via private message. If you want to switch back to public mode, use `/public`**")
        else:
            logger.info("You already on private mode!")
            await interaction.followup.send(
                "> **Warn: You already on private mode. If you want to switch to public mode, use `/public`**")

    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **Info: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **Warn: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")


    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.isReplyingAl = "False"
            await interaction.followup.send(
                "> **Info: The bot will only response to the slash command `/chat` next. If you want to switch back to replyAll mode, use `/replyAll` again.**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **Info: Next, the bot will response to all message in this channel only.If you want to switch back to normal mode, use `/replyAll` again.**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")


    @client.tree.command(name="chat-model", description="Switch different chat model")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL"),
        app_commands.Choice(name="Ofiicial GPT-4.0", value="OFFICIAL-GPT4"),
        app_commands.Choice(name="Website ChatGPT-3.5", value="UNOFFICIAL"),
        app_commands.Choice(name="Website ChatGPT-4.0", value="UNOFFICIAL-GPT4"),
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        if choices.value == "OFFICIAL":
            client.openAI_gpt_engine = "gpt-3.5-turbo"
            client.chat_model = "OFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Info: You are now in Official GPT-3.5 model.**\n")
            logger.warning("\x1b[31mSwitch to OFFICIAL GPT-3.5 model\x1b[0m")
        elif choices.value == "OFFICIAL-GPT4":
            client.openAI_gpt_engine = "gpt-4"
            client.chat_model = "OFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Info: You are now in Official GPT-4.0 model.**\n")
            logger.warning("\x1b[31mSwitch to OFFICIAL GPT-4.0 model\x1b[0m")
        elif choices.value == "UNOFFICIAL":
            client.openAI_gpt_engine = "gpt-3.5-turbo"
            client.chat_model = "UNOFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Info: You are now in Website ChatGPT-3.5 model.**\n")
            logger.warning("\x1b[31mSwitch to UNOFFICIAL(Website) GPT-3.5 model\x1b[0m")
        elif choices.value == "UNOFFICIAL-GPT4":
            client.openAI_gpt_engine = "gpt-4"
            client.chat_model = "UNOFFICIAL"
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(
                "> **Info: You are now in Website ChatGPT-4.0 model.**\n")
            logger.warning("\x1b[31mSwitch to UNOFFICIAL(Website) GPT-4.0 model\x1b[0m")


    @client.tree.command(name="reset", description="Complete reset ChatGPT conversation history")
    async def reset(interaction: discord.Interaction):
        if client.chat_model == "OFFICIAL":
            client.chatbot.reset()
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("> **Info: I have forgotten everything.**")
        personas.current_persona = "standard"
        logger.warning(
            "\x1b[31mChatGPT bot has been successfully reset\x1b[0m")
        await client.send_start_prompt()


    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":star:**ОСНОВНЫЕ КОМАНДЫ** \n
        - `/chat [message]` Общайтесь с ChatGPT!
        - `/draw [prompt]` Создавайте изображение с моделью Dalle2
        - `/switchpersona [persona]` Переключение между необязательными моделями поведения chatGPT
                `random`: Выбирает случайной модели поведения
                `chatgpt`: Стандартный режим chatGPT
                `dan`: Dan Mode 11.0, печально известный режим Do Anything Now
                `sda`: У Superior DAN еще больше свободы в режиме DAN.
                `confidant`: Злое доверенное лицо
                `based`: На основеGPT v2, сексуальный gpt
                `oppo`: OPPO говорит прямо противоположное тому, что сказал бы chatGPT
                `dev`: Режим разработчика, режим разработчика v2
        - `/private` ChatGPT перейти в приватный режим
        - `/public` ChatGPT перейти в публичный режим
        - `/replyall` ChatGPT переключается между режимом replyAll и режимом по умолчанию
        - `/reset` Очистить историю разговоров ChatGPT
        - `/chat-model` Переключить другую модель чата
                `ОФФИЦИАЛЬНАЯ`: GPT-3.5 model
                `НЕОФФИЦИАЛЬНАЯ`: Website ChatGPT
""")

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")

    @client.tree.command(name="draw", description="Generate an image with the Dalle2 model")
    async def draw(interaction: discord.Interaction, *, prompt: str):
        if interaction.user == client.user:
            return

        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /draw [{prompt}] in ({channel})")

        await interaction.response.defer(thinking=True, ephemeral=client.isPrivate)
        try:
            path = await art.draw(prompt)

            file = discord.File(path, filename="image.png")
            title = f'> **{prompt}** - <@{str(interaction.user.mention)}' + '> \n\n'
            embed = discord.Embed(title=title)
            embed.set_image(url="attachment://image.png")

            await interaction.followup.send(file=file, embed=embed)

        except openai.InvalidRequestError:
            await interaction.followup.send(
                "> **Warn: Inappropriate request 😿**")
            logger.info(
            f"\x1b[31m{username}\x1b[0m made an inappropriate request.!")

        except Exception as e:
            await interaction.followup.send(
                "> **Warn: Something went wrong 😿**")
            logger.exception(f"Error while generating image: {e}")


    @client.tree.command(name="switchpersona", description="Switch between optional chatGPT jailbreaks")
    @app_commands.choices(persona=[
        app_commands.Choice(name="Random", value="random"),
        app_commands.Choice(name="Standard", value="standard"),
        app_commands.Choice(name="Do Anything Now 11.0", value="dan"),
        app_commands.Choice(name="Superior Do Anything", value="sda"),
        app_commands.Choice(name="Evil Confidant", value="confidant"),
        app_commands.Choice(name="BasedGPT v2", value="based"),
        app_commands.Choice(name="OPPO", value="oppo"),
        app_commands.Choice(name="Developer Mode v2", value="dev")
    ])
    async def chat(interaction: discord.Interaction, persona: app_commands.Choice[str]):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **Warn: You already on replyAll mode. If you want to use slash command, switch to normal mode, use `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return

        await interaction.response.defer(thinking=True)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : '/switchpersona [{persona.value}]' ({channel})")

        persona = persona.value

        if persona == personas.current_persona:
            await interaction.followup.send(f"> **Warn: Already set to `{persona}` persona**")

        elif persona == "standard":
            if client.chat_model == "OFFICIAL":
                client.chatbot.reset()
            elif client.chat_model == "UNOFFICIAL":
                client.chatbot.reset_chat()

            personas.current_persona = "standard"
            await interaction.followup.send(
                f"> **Info: Switched to `{persona}` persona**")

        elif persona == "random":
            choices = list(personas.PERSONAS.keys())
            choice = randrange(0, 6)
            chosen_persona = choices[choice]
            personas.current_persona = chosen_persona
            await responses.switch_persona(chosen_persona, client)
            await interaction.followup.send(
                f"> **Info: Switched to `{chosen_persona}` persona**")


        elif persona in personas.PERSONAS:
            try:
                await responses.switch_persona(persona, client)
                personas.current_persona = persona
                await interaction.followup.send(
                f"> **Info: Switched to `{persona}` persona**")
            except Exception as e:
                await interaction.followup.send(
                    "> **Error: Something went wrong, please try again later! 😿**")
                logger.exception(f"Error while switching persona: {e}")

        else:
            await interaction.followup.send(
                f"> **Error: No available persona: `{persona}` 😿**")
            logger.info(
                f'{username} requested an unavailable persona: `{persona}`')

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
                    await client.send_message(message, user_message)

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
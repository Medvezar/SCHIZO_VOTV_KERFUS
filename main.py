import psutil, sys, asyncio, os, json, logging, datetime, re, random
import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import utcnow
from datetime import timezone, timedelta
import yt_dlp as youtube_dl


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

print("Версия библиотеки:", discord.__version__)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
#client = discord.Client(intents=intents)


# Укажите правильный путь к ffmpeg
FFMPEG_PATH = {
    'windows': r'C:\Users\medve\programming\libsAndOtherShit\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe',
}

ffmpeg_executable = r'C:\Users\medve\programming\libsAndOtherShit\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe'


USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]


# Настройки для yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    #'cookiesfrombrowser': ('chrome',),
    'cookiefile' : 'youtube.com_cookies.txt',
    'noplaylist': False,
    #'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    # Критически важные опции:
    'extract_flat': False,
    'http_headers': {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
    },
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
}


ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 32M -analyzeduration 32M',
    'options': '-vn -b:a 256k -ac 2',
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def validate_youtube_url(url: str) -> str:
    """Проверяет и нормализует YouTube URL"""
    # Удаляем лишние параметры и пробелы
    url = url.strip()

    # Проверяем основные форматы YouTube URL
    youtube_patterns = [
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)',
        r'(https?://)?(www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)',
    ]

    for pattern in youtube_patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(4) if 'shorts' not in pattern else match.group(3)
            return f"https://www.youtube.com/watch?v={video_id}"

    # Если URL не распознан, возвращаем как есть (будет ошибка)
    return url


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        # СОЗДАЕМ АУДИО ИСТОЧНИК С ЯВНЫМ УКАЗАНИЕМ ПУТИ
        ffmpeg_source = discord.FFmpegPCMAudio(
            source=filename,
            executable=ffmpeg_executable,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -b:a 256k'
        )
        return cls(ffmpeg_source, data=data)

utc_time = datetime.datetime.now(timezone.utc)
moscow_time = utc_time.astimezone(timezone(timedelta(hours=3)))
botStart = f"Время старта(МСК): {moscow_time.strftime('%H:%M:%S')} Дата: {moscow_time.strftime('%d.%m(%B).%Y')}"


TOKEN = ""
TARGET_MESSAGE_ID_ADD_ROLE = 1406694145266942134
TARGET_EMOJI = "✅"
botLogMessageId = 0


nightDiscordRules = "Первое правило: никому не рассказывать о ночном дискорде\n" \
                    "Второе правило: НИКОМУ НЕ РАССКАЗЫВАТЬ о ночном дискорде\nТретье правило: в чате участвуют все кто активны в дискорде ночью" \
                    "\nЧетвертое правило: в один момент времени может быть только один активный канал" \
                    "\nПятое правило: без банов и правил\nШестое правило: диалог длится столько сколько потребуется"




def get_memory_usage(): # проверка использования памяти
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def update_file(): # Обновление файла с настройками
    with open("OPTIONS.txt", 'w') as f:
        f.write(f"botToken;{TOKEN};\n")
        f.write(f"TARGET_MESSAGE_ID_ADD_ROLE;{TARGET_MESSAGE_ID_ADD_ROLE};\n")
        #f.write(f"TARGET_EMOJI;{TARGET_EMOJI};\n")
        f.write(f"botLogMessageId;{botLogMessageId};")


def load_options(): # Загрузка конфигурационного файла OPTIONS.txt
    global TOKEN, TARGET_MESSAGE_ID_ADD_ROLE, TARGET_EMOJI
    print("Загрузка конфигурационного файла")
    try:
        with open('OPTIONS.txt', 'r') as f:
            for line in f:
                l = line[:-1].split(';')
                #print(f"Строка файла: {l}")
                #print(f"{l[0]} : {l[1]}")
                match l[0]:
                    case 'botToken':
                        TOKEN = l[1]
                    case 'TARGET_MESSAGE_ID_ADD_ROLE':
                        TARGET_MESSAGE_ID_ADD_ROLE = int(l[1])
                    case 'botLogMessageId':
                        bot.logs_channel_id = int(l[1])
                        botLogMessageId = int(l[1])

    except FileNotFoundError:
        print("Файл OPTIONS.txt не найден, создан новый")

async def log_message(message): # функция, которая логирует сообщения пользователей в отдельный канал
    # Проверяем, установлен ли канал для логов
    if not bot.logs_channel_id:
        print("ID канала logs не установлен!")
        return
    try:
        # Получаем объект канала
        logs_channel = bot.get_channel(bot.logs_channel_id)
        if logs_channel is None:
            print(f"Не удалось найти канал с ID {bot.logs_channel_id}")
            return

        # Создаем embed для красивого отображения
        embed = discord.Embed(
            title="Лог сообщения",
            color=discord.Color.blue(),
            timestamp=message.created_at
        )

        # Добавляем информацию о сообщении
        embed.add_field(name="Автор", value=f"{message.author.mention}", inline=False)
        embed.add_field(name="Канал", value=f"{message.channel.mention}", inline=False)
        embed.add_field(name="Содержимое", value=message.content or "Нет текста", inline=False)

        # Если есть вложения
        if message.attachments:
            attachment_urls = "\n".join([att.url for att in message.attachments])
            embed.add_field(name="Вложения", value=attachment_urls, inline=False)

        # Если сообщение является ответом
        if message.reference:
            try:
                referenced_msg = await message.channel.fetch_message(message.reference.message_id)
                embed.add_field(
                    name="Ответ на сообщение",
                    value=f"[Ссылка]({referenced_msg.jump_url})\nАвтор: {referenced_msg.author.mention}\nСодержимое: {referenced_msg.content[:100]}...",
                    inline=False
                )
            except Exception as e:
                embed.add_field(name="Ответ на сообщение", value="Не удалось получить информацию", inline=False)

            # Отправляем embed в канал logs
        await logs_channel.send(embed=embed)

    except Exception as e:
        print(f"Ошибка при логировании сообщения: {e}")


async def console_commands():
    global TOKEN, TARGET_MESSAGE_ID_ADD_ROLE
    print("Запуск консольного обработчика...")
    while True:
        try:
            print("Доступные команды: stop, send, kick <user_id>\n")
            cmd = await asyncio.to_thread(input, "> ")
            consoleCmd = cmd.split(' ')[0]
            match consoleCmd:
                case 'send':
                    while True:
                        print("Доступные чаты:\n1. новости\n2. приветсвие\n3. правила-информация\n4. предложка для бота\n5. bot\n6. хочу-пообщаться(текст)\n7. хочу-пообщаться(гс)\n8. Комната 1\n9. Комната 2\n10. Комната 3\n11. Комната 4\n-1. exit\n  ")
                        cmd = await asyncio.to_thread(input, "> ")
                        channelId = 0
                        carrentChat = ""
                        match cmd.split()[0]:
                            case '1':
                                channelId = 1398257281820524575
                                carrentChat = "Новости"
                            case '2':
                                channelId = 1398258636127731827
                                carrentChat = "Приветсвие"
                            case '3':
                                channelId = 1398293747573325925
                                carrentChat = "Правила-информация"
                            case '4':
                                channelId = 1398264961641349180
                                carrentChat = "Предложка для бота"
                            case '5':
                                channelId = 1398259122905944128
                                carrentChat = "bot"
                            case '6':
                                channelId = 1398258077467148390
                                carrentChat = "хочу-пообщаться(текст)"
                            case '7':
                                channelId = 1063432483028344956
                                carrentChat = "хочу-пообщаться(гс)"
                            case '8':
                                channelId = 1398257037842055210
                                carrentChat = "Комната 1"
                            case '9':
                                channelId = 1398257174664445972
                                carrentChat = "Комната 2"
                            case '10':
                                channelId = 1398257935460728914
                                carrentChat = "Комната 3"
                            case '11':
                                channelId = 1398257981790883861
                                carrentChat = "Комната 4"
                            case '-1':
                                break
                            case _:
                                print("Неправильная команда\n")
                        while True:
                            print(f"Current chat: {carrentChat}\n-1 - to exit\n")
                            cmd = await asyncio.to_thread(input, "> ")
                            match cmd.split()[0]:
                                case '-1':
                                    break
                            channel = bot.get_channel(channelId)
                            text = cmd.split(' ')
                            if channel:
                                await channel.send(' '.join(text))
                case "kick":
                    print("Not ready :(")
                case "test":
                    print(f'Бот {bot.user.name} запущен')
                    print(f'Серверы: {len(bot.guilds)}')
                    print(f'Пинг: {round(bot.latency * 1000)} мс')
                    print(botStart)
                    print(f"Mem usage: {get_memory_usage():.2f} MB")
                case "config":
                    while True:
                        print("config-mode\ncommands: -1, options, force load, force update, reload system, ctmfar(change target message for adding role)\n")
                        cmd = await asyncio.to_thread(input, "> ")
                        match cmd:
                            case "-1":
                                return
                            case "options":
                                print(f"Bot token: {TOKEN}\nTarget message for adding role: {TARGET_MESSAGE_ID_ADD_ROLE}\n"
                                      f"Target emoji for adding role: {TARGET_EMOJI}\nBot UTC time: {utc_time}")
                            case "force load":
                                try:
                                    load_options()
                                    print("Настройки успешно применены")
                                except Exception as e:
                                    print(f"Ошибка при загрузке настроек: {e}")
                            case "force update":
                                try:
                                    update_file()
                                    print("Настройки успешно сохранены")
                                except Exception as e:
                                    print(f"Ошибка при обновлении настроек: {e}")
                            case "reload system":
                                print("not working yet")
                            case "ctmfar":
                                print("вставьте id сообщения")
                                cmd = await asyncio.to_thread(input, "> ")
                                try:
                                    TARGET_MESSAGE_ID_ADD_ROLE = int(cmd)
                                    print("ID успешно заменен")
                                except Exception as e:
                                    print(f"Ошибка при смене ID: {e}")
                            case _:
                                print("unknown command")

                case _:
                    print("Доступные команды: stop, send <channel_id> <text>, kick <user_id>\n")
        except Exception as e:
            print(f"Ошибка: {e}\n")


@bot.event
async def on_ready():
    print(f'Бот {bot.user.name} запущен')
    print(f'Серверы: {len(bot.guilds)}')
    print(f'Пинг: {round(bot.latency * 1000)} мс')
    print(botStart)

    try:
        # Синхронизируем только для конкретного сервера (для теста)
        guild = discord.Object(id=1063432482269184021)  # Замените на реальный ID сервера
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print("Команды синхронизированы!")
        print(f"Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")
    print("Начало работы...")
    asyncio.create_task(console_commands())


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "Мяу!":
        await message.channel.send("Мяу >.<", delete_after=30)
    elif message.content.lower() == "правила ночного дискорда":
        if int(moscow_time.strftime('%H')) > 5:
            print(int(moscow_time.strftime('%H')))
            await message.channel.send("Тсссс, еще не ночь", delete_after=3)
            await asyncio.sleep(3)
            await message.delete()
        else:
            await message.channel.send(nightDiscordRules,
            delete_after=60)
            await message.delete()
    else:
        await bot.process_commands(message)
        await log_message(message)


@bot.tree.command(name="change_target_message", description="Команда для изменения сообщения, на которое будет реагировать бот")
@app_commands.describe(message_id="ID сообщения, на которое заменить голосование")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def change_target_message(interaction: discord.Interaction, message_id: str):
    global TARGET_MESSAGE_ID_ADD_ROLE
    try:
        if message_id == "" or int(message_id) == 0:
            await interaction.response.send_message("Ну ты дурачок, это неправильный вид id")
        elif message_id == TARGET_MESSAGE_ID_ADD_ROLE:
            await interaction.response.send_message("Данный id уже записан как target")
        else:
            TARGET_MESSAGE_ID_ADD_ROLE = int(message_id)
    except:
        await interaction.response.send_message("Ошибка при изменении id")


@bot.tree.command(name="play", description="Воспроизвести музыку с YouTube")
@app_commands.describe(url="Ссылка на YouTube видео")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not interaction.user.voice:
        await interaction.followup.send("❌ Вы должны быть в голосовом канале!", ephemeral=True)
        return

    try:
        # Нормализуем URL перед обработкой
        clean_url = validate_youtube_url(url)
        print(f"Оригинальный URL: {url}")
        print(f"Очищенный URL: {clean_url}")

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if not voice_client or not voice_client.is_connected():
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        # Используем очищенный URL
        player = await YTDLSource.from_url(clean_url, loop=bot.loop, stream=True)

        if voice_client.is_playing():
            voice_client.stop()

        voice_client.play(player, after=lambda e: print(f'Ошибка: {e}') if e else None)

        await interaction.followup.send(f"🎵 Сейчас играет: **{player.title}**")

    except youtube_dl.DownloadError as e:
        await interaction.followup.send("❌ Ошибка загрузки. Проверьте ссылку!")
        print(f"DownloadError: {e}")
    except Exception as e:
        await interaction.followup.send(f"❌ Ошибка: {str(e)}")
        print(f"Error: {e}")


@bot.tree.command(name="stop", description="Остановить воспроизведение")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_connected():
        await voice_client.disconnect()
        await interaction.response.send_message("⏹ Воспроизведение остановлено")
    else:
        await interaction.response.send_message("❌ Бот не подключен!", ephemeral=True)


@bot.tree.command(name="test", description="Тестовая команда")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def test(interaction: discord.Interaction):
    # проверка статуса бота
    print(f'Бот {bot.user.name} запущен')
    print(f'Серверы: {len(bot.guilds)}')
    print(f'Пинг: {round(bot.latency * 1000)} мс')
    print(f"Время старта(МСК): {moscow_time.strftime('%H:%M:%S')} Дата: {moscow_time.strftime('%d.%m(%B).%Y')}")
    await interaction.response.send_message(f'Бот {bot.user.name} запущен\nСерверы: {len(bot.guilds)}\nПинг: {round(bot.latency * 1000)} мс\nВремя старта(МСК): {moscow_time.strftime("%H:%M:%S")} Дата: {moscow_time.strftime("%d.%m(%B).%Y")}')


@bot.tree.command(name="text_by_bot", description="Отправляет в чат текст")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def text_by_bot(
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        content: str
    ):
    # Отправка сообщений от имени бота
    await channel.send(content=content)


@bot.tree.command(name="post", description="Создать объявление")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def post(
        interaction: discord.Interaction,
        title: str,
        channel: discord.TextChannel,
        content: str
):
    """
    Создает объявление в указанном канале
    Параметры:
    title: Заголовок объявления (1-50 символов)
    channel: Канал для публикации
    content: Текст объявления (1-1000 символов)
    """
    embed = discord.Embed(
        title=title,
        description=content,
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Автор: {interaction.user.display_name}",
                     icon_url=interaction.user.avatar.url)

    try:
        await channel.send(embed=embed)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Посмотреть объявление",
            url=channel.jump_url,
            style=discord.ButtonStyle.url
        ))

        await interaction.response.send_message(
            f"✅ Объявление опубликовано в {channel.mention}!",
            view=view,
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Нет прав для отправки в этот канал!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Ошибка: {str(e)}",
            ephemeral=True
        )


@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id != TARGET_MESSAGE_ID_ADD_ROLE or str(payload.emoji) != TARGET_EMOJI:
        return
    else:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(1398249331684806728)
        channel = bot.get_channel(payload.channel_id)

        if not member or not role or member.bot:
            return
        if role in member.roles:
            return
        try:
            await member.add_roles(role)
            await channel.send(f'{member.mention} получил(а) роль Шизоид!')
        except Exception as e:
            print(f'Ошибка при выдаче роли: {e}')


@bot.tree.command(name="check_perms", description="Проверка прав бота")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def check_perms(interaction: discord.Interaction):
    perms = interaction.guild.me.guild_permissions
    embed = discord.Embed(
        title="Права бота",
        description=f"Manage Roles: **{'✅' if perms.manage_roles else '❌'}**\n"
                   f"Администратор: **{'✅' if perms.administrator else '❌'}**"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="update_commands", description="Проверка синхронизации команд")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def clear_commands(interaction: discord.Interaction):
    try:
        # Полная очистка команд
        await interaction.response.send_message("Очистка команд бота...")
        bot.tree.clear_commands(guild=discord.Object(id=1063432482269184021))
        await bot.tree.sync()

        # Для конкретного сервера (замените GUILD_ID)
        # guild = discord.Object(id=GUILD_ID)
        # bot.tree.clear_commands(guild=guild)
        # await bot.tree.sync(guild=guild)

        await interaction.followup.send(
            "✅ Все команды успешно обновлены!\nИзменения ввойдут в силу в течении часа"
        )
    except Exception as e:
        await interaction.followup.send(
            f"❌ Ошибка: {str(e)}"
        )





@bot.tree.command(name="help", description="Выводит функционал бота")
@app_commands.checks.has_any_role("Администратор", "Владелец", "Модератор")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(
    f'Бот имеет на данный момент следующие команды:\n 1. test, 2. update_commands, 3. check_perms, 4. post, 5. text_by_bot\n' +
    '1 - выводит статус бота(Какой пинг с дискордом, когда был запущен)\n' +
    '2 - Обновляет список команд (Из-за дискорда обновление происходит в течении часа)\n' +
    '3 - Показывает права бота\n' +
    '4 - Выкладывает объявление в выбранный канал\n' +
    '5 - Отправляет сообщение от имени бота в выбранный кнаал')


def main():
    load_options()
    print("Запуск бота...")
    bot.run(TOKEN)


if __name__ == '__main__':
    main()


"""
Первое правило: никому не рассказывать о ночном дискорде
Второе правило: никому не рассказывать о ночном дискорде
Третье правило: в чате участвуют все кто активны в дискорде ночью
Четвертое правило: в один момент времени может быть только один активный канал
Пятое правило: без банов и правил
Шестое правило: диалог длится столько сколько потребуется
"""
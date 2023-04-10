import json
import sqlite3
from datetime import timedelta, datetime

import discord
import requests

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with open("config.yaml") as config_file:
        CONFIG = json.loads(config_file.read())

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True

    client = discord.Client(intents=intents)

    sqlite_connection = sqlite3.connect("esmeh.db")

    cursor = sqlite_connection.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS fortunes("
                   "user TEXT PRIMARY KEY,"
                   "timestamp TEXT NOT NULL"
                   ")")

    @client.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(client))


    @client.event
    async def on_message(message):
        print(message.content)

        if message.author == client.user:
            return

        if message.content.startswith("e.fortune"):
            found = False
            fortunes = cursor.execute("SELECT * FROM fortunes")
            for row in fortunes.fetchall():
                if row[0] == f"{message.author.name}#{message.author.discriminator}":
                    found = True
                    if datetime.now() - timedelta(hours=24) <= datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S") <= datetime.now():
                        await message.author.send(f"Não passou de 24 horas ô arrombado!")
                        return

            if not found:
                cursor.execute(f"""
                    INSERT INTO fortunes (user, timestamp) VALUES
                        ("{message.author}", "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
                """)
            else:
                cursor.execute(f"""
                                    UPDATE fortunes
                                    SET timestamp = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
                                    WHERE user = "{message.author.name}#{message.author.discriminator}";
                                """)

            url = "https://fortune-cookie2.p.rapidapi.com/fortune"

            headers = {
                "X-RapidAPI-Key": "88d9f9b41dmshe238388b7a0185dp1eed24jsn4cd600b867a9",
                "X-RapidAPI-Host": "fortune-cookie2.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers)
            await message.channel.send(f":crystal_ball: {json.loads(response.text)['answer']}")

            sqlite_connection.commit()


    client.run(CONFIG["discord_api"]["esmeh_bot_discord_token"])

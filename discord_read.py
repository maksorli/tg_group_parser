import discord
import aiohttp
import asyncio
import pandas as pd
from config import TOKEN, GUILD_ID


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}')
        guild = self.get_guild(GUILD_ID)
        if guild is None:
            print(f'Guild with ID {GUILD_ID} not found')
            await self.close()
            return
        missing_access_list = []
        messages_data = []
   
        for channel in guild.text_channels:
            try:
                print(f'Fetching messages from channel: {channel.name}')
                
                messages = await self.fetch_all_messages(channel)
                for message in messages:
                    content = message.content
                    if not content:  # If the message text is empty
                        if message.attachments:  # Check for attachments
                            content = ', '.join([attachment.url for attachment in message.attachments])
                        elif message.embeds:  # Check for embeds
                            content = ', '.join([embed.title if embed.title else "[EMBED]" for embed in message.embeds])
                        else:
                            content = '[EMPTY MESSAGE]'
                    messages_data.append([channel.name, message.created_at, message.author.name, content])
            except discord.Forbidden:
                missing_access_list.append(channel.name)
                print(f'Missing access to channel: {channel.name}')
            except Exception as e:
                print(f'Error fetching messages from channel {channel.name}: {e}')

        # Save messages data to a CSV file
        df = pd.DataFrame(messages_data, columns=['Channel', 'Date', 'Author', 'Content'])
        df.to_csv('server_messages.csv', index=False, encoding='utf-8')
        print('Messages saved to server_messages.csv')
        await self.close()

    async def fetch_all_messages(self, channel):
        messages = []
        async for message in channel.history(limit=None):
            messages.append(message)
        return messages

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True  # Enable this to receive message content

client = MyClient(intents=intents)
client.run(TOKEN)

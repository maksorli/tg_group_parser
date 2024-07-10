from telethon import TelegramClient 
import pandas as pd
import asyncio
from datetime import datetime
import logging
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, session_name, spreadsheet_id, worksheet_name
from modules import append_to_google_sheets

api_id = TELEGRAM_API_ID
api_hash = TELEGRAM_API_HASH
client = TelegramClient(session_name, api_id, api_hash)

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_telegram_message_link(dialog_name: str, message_id: int) -> str:
    """
    Generates a direct link to a message in Telegram.

    Parameters:
    dialog_name (str): Name of the dialog.
    message_id (int): ID of the message in the chat.

    Returns:
    str: URL of the message in Telegram.
    """
    return f"https://t.me/{dialog_name}/{message_id}"

async def tg_read(tg_groups: list, date_begin: str = None, date_end: str = None, last_days: int = None, keyword: str = None, limit: int = None, forwardtochat: str = None) -> pd.DataFrame:
    """
    Reads messages from specified Telegram groups within a date range or containing a keyword.

    Parameters:
    tg_groups (list): List of Telegram group names.
    date_begin (str): Start date in 'dd/mm/yyyy' format.
    date_end (str): End date in 'dd/mm/yyyy' format.
    last_days (int): Number of last days to fetch messages from.
    keyword (str): Keyword to filter messages.
    limit (int): Limit on the number of messages to fetch.
    forwardtochat (str): Chat ID to forward the messages to.

    Returns:
    pd.DataFrame: DataFrame containing the messages data.
    """
    messages_data = []
    dialogs = await client.get_dialogs()

    for tg_group in tg_groups:
        target_dialog = next((d for d in dialogs if d.title == tg_group), None)
        
        if target_dialog:
            logger.info(f"Found dialog: {target_dialog.title}")
            async for message in client.iter_messages(target_dialog, limit=limit, reverse=False):
                message_date = message.date.date()
                if date_begin and date_end:
                    date_begin_parsed = datetime.strptime(date_begin, '%d/%m/%Y').date()
                    date_end_parsed = datetime.strptime(date_end, '%d/%m/%Y').date()
                    if not (date_begin_parsed <= message_date <= date_end_parsed):
                        continue
                if keyword and keyword.lower() not in message.text.lower():
                    continue

                message_link = generate_telegram_message_link(target_dialog.id, message.id)
                if forwardtochat:
                    await message.forward_to(forwardtochat)
                messages_data.append({
                    'Group': target_dialog.title,
                    'Date': message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    'Message': message.text,
                    'Link': message_link  # Adding the link to the message
                })
              
            await asyncio.sleep(0.5)
        else:
            logger.warning(f"Dialog '{tg_group}' not found")

    return pd.DataFrame(messages_data)

def append_to_excel(filename: str, new_data_df: pd.DataFrame) -> None:
    """
    Appends new data to an existing Excel file or creates a new file if it doesn't exist.

    Parameters:
    filename (str): Path to the Excel file.
    new_data_df (pd.DataFrame): DataFrame containing the new data to append.

    Returns:
    None
    """
    try:
        # Load existing file if it exists
        old_data_df = pd.read_excel(filename, index_col=None)
        logger.info(f"File {filename} loaded successfully")
        # Concatenate old data with new data
        updated_data_df = pd.concat([old_data_df, new_data_df], ignore_index=True)
    except FileNotFoundError:
        # If file does not exist, use new data and create a new file in the same directory
        updated_data_df = new_data_df
        logger.info(f"File {filename} does not exist")
    # Write updated data to the file
    with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
        updated_data_df.to_excel(writer, index=False)
        logger.info(f"Data updated")

async def list_chats() -> None:
    """
    Lists all chats the user is a member of.

    Returns:
    None
    """
    await client.start()
    # Get all dialogs
    async for dialog in client.iter_dialogs():
        print(f'Chat: "{dialog.name}" has ID: {dialog.id}')

tg_groups = ['Group 1', 'Group 2']
filename = r'~\messages.xlsx'

# Using asynchronous context manager to work with the client
async def main():
    async with client:
        new_data = await tg_read(tg_groups, date_begin='22/04/2024', date_end='25/04/2024', keyword='Project', limit=50)
        append_to_google_sheets(spreadsheet_id, worksheet_name, new_data)
        await list_chats()

# run
asyncio.run(main())
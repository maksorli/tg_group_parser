import pandas as pd
from openpyxl.utils import get_column_letter  # Excel
import logging
import asyncio
from telethon import TelegramClient 
import gspread  # Google Sheets
from oauth2client.service_account import ServiceAccountCredentials  # Google Sheets

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def append_to_excel(filename: str, new_data_df: pd.DataFrame) -> None:
    """
    Append new data to an existing Excel file or create a new file if it doesn't exist.

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
        logger.info("Data updated")

def append_to_google_sheets(spreadsheet_id: str, worksheet_name: str, new_data_df: pd.DataFrame) -> None:
    """
    Append new data to an existing Google Sheet or create a new worksheet if it doesn't exist.

    Parameters:
    spreadsheet_id (str): ID of the Google Spreadsheet.
    worksheet_name (str): Name of the worksheet within the Google Spreadsheet.
    new_data_df (pd.DataFrame): DataFrame containing the new data to append.

    Returns:
    None
    """
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\maksim.evdokimov\Documents\!Dev\Telegram\google_auth.json', scope)
    client = gspread.authorize(creds)
    
    try:
        # Open existing Google Sheet
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        # Get existing data as DataFrame
        data = worksheet.get_all_values()
        headers = data.pop(0)
        old_data_df = pd.DataFrame(data, columns=headers)
        # Concatenate old data with new data
        updated_data_df = pd.concat([old_data_df, new_data_df], ignore_index=True)
        logger.info("Data loaded and combined successfully")
    except gspread.exceptions.WorksheetNotFound:
        # If worksheet not found, create new and use new data
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        updated_data_df = new_data_df
        logger.info(f"Worksheet {worksheet_name} does not exist, new worksheet created")
    
    # Clear worksheet and write updated data
    worksheet.clear()
    worksheet.update([updated_data_df.columns.values.tolist()] + updated_data_df.values.tolist())
    logger.info("Data updated in Google Sheets")

def generate_telegram_message_link(dialog_name: str, message_id: int) -> str:
    """
    Generate a direct link to a message in Telegram.

    Parameters:
    dialog_name (str): Name of the dialog.
    message_id (int): ID of the message in the chat.

    Returns:
    str: URL of the message in Telegram.
    """
    return f"https://t.me/{dialog_name}/{message_id}"

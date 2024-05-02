import pandas as pd
from openpyxl.utils import get_column_letter #excel
import logging
import asyncio
from telethon import TelegramClient 
import gspread #gsheets
from oauth2client.service_account import ServiceAccountCredentials #gsheets

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def append_to_excel(filename, new_data_df): #обновление файла XLS
        # Настройка логгера
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    try:
        # Загрузка существующего файла, если он существует
        old_data_df = pd.read_excel(filename, index_col=None)
        logger.info(f"Файл {filename} успешно загружен")
        # Объединение старых данных с новыми
        updated_data_df = pd.concat([old_data_df, new_data_df], ignore_index=True)
    except FileNotFoundError:
        # Если файл не существует, просто используем новые данные и создаем новый файл в этой же директории
        updated_data_df = new_data_df
        logger.info(f"Файл {filename} не существует")
    # Запись обновленных данных в файл
    with pd.ExcelWriter(filename, engine='openpyxl', mode='w') as writer:
        updated_data_df.to_excel(writer, index=False)
        logger.info(f"Данные обновлены")

   
def append_to_google_sheets(spreadsheet_id, worksheet_name, new_data_df):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\maksim.evdokimov\Documents\!Dev\Telegram\google_auth.json', scope)
    client = gspread.authorize(creds)
    
    try:
        # Открытие существующего Google Sheet
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        # Получение существующих данных как DataFrame
        data = worksheet.get_all_values()
        headers = data.pop(0)
        old_data_df = pd.DataFrame(data, columns=headers)
        # Объединение старых данных с новыми
        updated_data_df = pd.concat([old_data_df, new_data_df], ignore_index=True)
        logger.info("Данные успешно загружены и объединены")
    except gspread.exceptions.WorksheetNotFound:
        # Если лист не найден, создаем новый и используем новые данные
        worksheet = sheet.add_worksheet(title=worksheet_name, rows="1000", cols="20")
        updated_data_df = new_data_df
        logger.info(f"Лист {worksheet_name} не существует, создан новый лист")
    
    # Очистка листа и запись обновленных данных
    worksheet.clear()
    worksheet.update([updated_data_df.columns.values.tolist()] + updated_data_df.values.tolist())
    logger.info("Данные обновлены в Google Sheets")



def generate_telegram_message_link(dialog_name, message_id): #кривые ссылки, разобраться

    """
    Генерирует прямую ссылку на сообщение в Telegram.

    Параметры:
    chat_id (int): ID чата, может быть отрицательным для супергрупп.
    message_id (int): ID сообщения в чате.

    Возвращает:
    str: URL-адрес сообщения в Telegram.
    """
    #return f"https://t.me/c/{abs(chat_id)}/{message_id}"
    return f"https://t.me/{dialog_name}/{message_id}"
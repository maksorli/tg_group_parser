# Telegram Message Reader

This project reads messages from specified Telegram groups, filters them based on given criteria, and saves the results into an Excel file using the Telethon library.

## Features

- Read messages from specified Telegram groups.
- Filter messages by date range, keywords, and more.
- Generate direct links to Telegram messages.
- Append new messages to an existing Excel file or create a new one.
- List all chats the user is a member of.

## Requirements

- Python 3.7+ ![](https://img.shields.io/badge/Python-3.10-black?style=flat&logo=python) 
- Telethon ![](https://img.shields.io/badge/Telethon-1.36.0-black?style=flat&logo=telethon) 
- Pandas ![](https://img.shields.io/badge/Pandas-2.2.2-black?style=flat&logo=pandas)
- Openpyxl ![](https://img.shields.io/badge/Openpyxl-3.1.4-black?style=flat&logo=openpyxl)
- Requests ![](https://img.shields.io/badge/Requests-2.32.3-black?style=flat&logo=Requests)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/telegram-message-reader.git
    ```

2. Install the required packages:
    ```sh
    pip install telethon pandas openpyxl requests
    ```

## Configuration

1. Create a `config_tg.py` file with your Telegram API credentials:
    ```python
    TELEGRAM_API_ID = 'your_api_id'
    TELEGRAM_API_HASH = 'your_api_hash'
    session_name = 'your_session_name'
    ```

2. Update the `tg_groups` list with the names of the Telegram groups you want to read messages from.

3. Update the `filename` variable with the path to the Excel file where you want to save the messages.

## Usage

Run the script...
 
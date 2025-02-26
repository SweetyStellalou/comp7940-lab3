from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                CallbackContext)
import configparser
import logging
import redis
from chatGPT_HKBU import HKBU_ChatGPT
global redis1
global chatgpt
def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(config['REDIS']['HOST']), 
                password=(config['REDIS']['PASSWORD']), 
                port=(config['REDIS']['REDISPORT']),
                decode_responses=(config['REDIS']['DECODE_RESPONSE']),
                username=(config['REDIS']['USER_NAME']))
    print("Redis connection successful:", redis1.ping())
    # 初始化 ChatGPT
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), 
                        equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # You can set this logging module, so you will know when 
    # and why things do not work as expected Meanwhile, update your config.ini as:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)
    
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    
    # To start the bot:
    try:
        updater.start_polling()
        updater.idle()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        if 'redis1' in globals():
            redis1.close()  # 显式关闭 Redis 连接
            print("Redis connection closed.")
def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text= reply_message)
 # Define a few command handlers. These usually take the two arguments update and
 # context. Error handlers also receive the raised TelegramError object in error.
def equiped_chatgpt(update: Update, context: CallbackContext):
    global chatgpt
    # 获取用户输入
    user_message = update.message.text
    # 调用 ChatGPT 获取回复
    reply_message = chatgpt.submit(user_message)
    # 发送回复
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Helping you helping you.')
def add(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg +  ' for ' + 
                        redis1.get(msg) + ' times.')
    
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')
if __name__ == '__main__':
    main()
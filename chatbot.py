import logging
from telegram.ext import Updater, MessageHandler, Filters
import configparser
import os

# 配置日志系统
logging.basicConfig(
    filename='bot.log',  # 日志文件路径
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def echo(update, context):
    logging.info("Received message: " + update.message.text)
    update.message.reply_text(update.message.text.upper())

def main():
    logging.info("Starting main function...")
    
    # 加载配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['TELEGRAM']['ACCESS_TOKEN']
    logging.info("Loaded Token: " + token)

    # 启动机器人
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # 注册消息处理器
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    logging.info("Starting polling...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    logging.info("Script started.")
    main()
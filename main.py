# Install required packages
!pip install openai langchain langchain-openai
!pip install langchain_community
!pip install python-telegram-bot openai langchain langchain-openai
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, Application
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# ---------- Config OpenRouter API ----------
os.environ["OPENAI_API_KEY"] = "your_openrouter_api_key"  # Replace with your OpenRouter key
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# ---------- Initialize LangChain LLM ----------
llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-3.5-turbo",
    openai_api_base=os.environ["OPENAI_API_BASE"]
)

# ---------- Product Catalog ----------
products = [
    {"id": 1, "name": "Smartphone", "category": "Electronics"},
    {"id": 2, "name": "Running Shoes", "category": "Footwear"},
    {"id": 3, "name": "Leather Wallet", "category": "Accessories"},
    {"id": 4, "name": "Bluetooth Headphones", "category": "Electronics"},
    {"id": 5, "name": "Digital Watch", "category": "Wearables"},
]

# ---------- Reward Function (optional for future RL training) ----------
def reward_function(customer_input, agent_response):
    reward = 0
    keywords = [p["name"].lower() for p in products]
    for kw in keywords:
        if kw in agent_response.lower():
            reward = 1
            break
    if "i don't know" in agent_response.lower():
        reward = -1
    return reward

# ---------- AI Agent Logic ----------
def chat_with_agent(user_input):
    messages = [
        SystemMessage(content="You are a helpful e-commerce agent. Suggest suitable products from the catalog."),
        HumanMessage(content=user_input)
    ]
    response = llm(messages)
    return response.content

# Define the start function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your e-commerce assistant. How can I help you today?")

# Define the handle_message function
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    agent_response = chat_with_agent(user_input)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=agent_response)
    
# ---------- Telegram Bot Launch ----------
if __name__ == '__main__':
    application = ApplicationBuilder().token("your_telegram_bot_toke").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Telegram bot is running in Colab/Jupyter...")

    # Run polling in already running event loop
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
    except RuntimeError as e:
        print(f"⚠️ RuntimeError: {e}")

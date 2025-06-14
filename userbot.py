from telethon import TelegramClient, events
import asyncio
import os

api_id = int(os.getenv("25925019")) # 🔁 Replace with your API ID
api_hash = os.getenv('c5a78f58dae7f922ecc995661b51d0a1')
bot_token = os.getenv("7408045132:AAH41RUYYIFsFOxgOem6DOW8HeAxDe8V1fY")
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)


# Global variables
chat_list = []
source_chat = None
target_chat = None
state = {'step': 'idle'}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("Hi there! 👋")
    await list_chats(event)

async def list_chats(event):
    global chat_list
    chat_list = []

    async for dialog in client.iter_dialogs(limit=15):
        chat_list.append(dialog)
    
    message = "📋 Select the source chat by replying with a number:\n"
    for i, dialog in enumerate(chat_list):
        name = dialog.name or "Unnamed Chat"
        message += f"{i + 1}. {name}\n"

    state['step'] = 'choose_source'
    await event.respond(message)

@client.on(events.NewMessage)
async def handle_selection(event):
    global source_chat, target_chat

    # Ignore forwarded messages while selecting
    if event.is_private and event.raw_text.isdigit():
        index = int(event.raw_text.strip()) - 1

        if index < 0 or index >= len(chat_list):
            await event.respond("❌ Invalid number. Please select from the list.")
            return

        if state['step'] == 'choose_source':
            source_chat = chat_list[index].entity
            state['source_name'] = chat_list[index].name or "Unnamed Chat"
            state['step'] = 'choose_target'

            # Ask for target chat
            msg = "✅ Source selected: " + state['source_name'] + "\n\n"
            msg += "📋 Now select the destination chat by replying with a number:\n"
            for i, dialog in enumerate(chat_list):
                name = dialog.name or "Unnamed Chat"
                msg += f"{i + 1}. {name}\n"
            await event.respond(msg)

        elif state['step'] == 'choose_target':
            target_chat = chat_list[index].entity
            target_name = chat_list[index].name or "Unnamed Chat"
            state['step'] = 'forwarding'

            await event.respond(
                f"🔁 Now forwarding messages from {state['source_name']} ➡️ {target_name}"
            )

# Forwarding handler
@client.on(events.NewMessage)
async def forward(event):
    if state.get('step') == 'forwarding' and source_chat and target_chat:
        if event.chat_id == source_chat.id:
            await client.forward_messages(target_chat, event.message)

print("📲 Starting your interactive userbot...")
client.start()
client.run_until_disconnected()

from telethon import TelegramClient, events
import os
import asyncio

# Fetch API credentials from environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Use the session file you uploaded to GitHub (should be in the same folder)
client = TelegramClient("RailwayaSession", api_id, api_hash)

# Global state
chat_list = []
source_chat = None
target_chat = None
state = {'step': 'idle'}

async def main():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Session not authorized. Please generate the session file locally.")
        return

    print("📲 Starting your interactive userbot...")

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

        if event.is_private and event.raw_text.isdigit():
            index = int(event.raw_text.strip()) - 1

            if index < 0 or index >= len(chat_list):
                await event.respond("❌ Invalid number. Please select from the list.")
                return

            if state['step'] == 'choose_source':
                source_chat = chat_list[index].entity
                state['source_name'] = chat_list[index].name or "Unnamed Chat"
                state['step'] = 'choose_target'

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

    @client.on(events.NewMessage)
    async def forward(event):
        if state.get('step') == 'forwarding' and source_chat and target_chat:
            if event.chat_id == source_chat.id:
                await client.forward_messages(target_chat, event.message)

    await client.run_until_disconnected()

# Run the bot
asyncio.run(main())

from telethon import TelegramClient, events
import asyncio
import random

api_id = 25925019
api_hash = 'c5a78f58dae7f922ecc995661b51d0a1'

number = random.randint(1, 10000)

client = TelegramClient(str(number), api_id, api_hash)

chat_list = []
source_title = None
destination_title = None
destination_entity = None
state = {'step': 'idle'}

@client.on(events.NewMessage)
async def main_handler(event):
    global chat_list, source_title, destination_title, destination_entity

    if event.is_private:
        text = event.raw_text.strip()

        # Step 1: Start
        if text == "/start":
            chat_list.clear()
            async for dialog in client.iter_dialogs(limit=15):
                chat_list.append(dialog)

            msg = "📋 *Choose source chat by replying with a number:*\n"
            for i, dialog in enumerate(chat_list):
                msg += f"{i+1}. {dialog.name or 'Unnamed Chat'}\n"

            state['step'] = 'choose_source'
            await event.respond(msg)
            return

        # Step 2: Chat Selection
        if text.isdigit():
            index = int(text) - 1
            if index < 0 or index >= len(chat_list):
                await event.respond("❌ Invalid number. Try again.")
                return

            selected_dialog = chat_list[index]

            if state['step'] == 'choose_source':
                source_title = selected_dialog.name
                state['step'] = 'choose_target'

                msg = f"✅ Source set: *{source_title}*\n\nNow select destination chat:\n"
                for i, dialog in enumerate(chat_list):
                    msg += f"{i+1}. {dialog.name or 'Unnamed Chat'}\n"
                await event.respond(msg)

            elif state['step'] == 'choose_target':
                destination_title = selected_dialog.name
                destination_entity = await client.get_entity(destination_title)
                state['step'] = 'forwarding'

                await event.respond(
                    f"🚀 Now forwarding messages from *{source_title}* ➡️ *{destination_title}*"
                )
            return

    # Step 3: Forwarding based on selected titles
    if not event.is_private and state['step'] == 'forwarding':
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", None) or getattr(chat, "first_name", "Unnamed")

        if chat_title == source_title and destination_entity:
            print(f"📨 Message from: {chat_title} | Forwarding...")
            try:
                await client.forward_messages(destination_entity, event.message)
                print("✅ Forwarded")
            except Exception as e:
                print(f"❌ Failed to forward: {e}")
        else:
            print(f"⛔ Ignored message from: {chat_title}")

print("🚦 Starting userbot...")
client.start()
client.run_until_disconnected()

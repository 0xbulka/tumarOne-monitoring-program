import asyncio
import json
import os
from config import BOT_TOKEN, TELEGRAM_CHANNEL_ID, POLL_INTERVAL, TUMAR_AUTH_CODE, KNOWN_IDS_FILE
from aiogram import Bot
from auth_service import AuthService
from api_client import fetch_programs

def load_known_ids():
    if os.path.exists(KNOWN_IDS_FILE):
        with open(KNOWN_IDS_FILE, 'r') as f:
            try:
                ids = json.load(f)
                if isinstance(ids, list):
                    return set(ids)
                else:
                    return set()
            except json.JSONDecodeError:
                return set()
    return set()

def save_known_ids(ids_set):
    try:
        with open(KNOWN_IDS_FILE, 'w') as f:
            json.dump(list(ids_set), f, indent=4)
    except Exception as e:
        print(f"Error saving known IDs to {KNOWN_IDS_FILE}: {e}")

async def monitor():
    bot = Bot(token=BOT_TOKEN)
    auth = AuthService(code=TUMAR_AUTH_CODE)

    known_ids = load_known_ids()
    print(f"Loaded {len(known_ids)} known program IDs.")

    try:
        token = auth.get_access_token()
        programs = fetch_programs(token)
        if not known_ids:
            known_ids = {p["id"] for p in programs}
            save_known_ids(known_ids)
            print(f"Initial population: {len(known_ids)} programs marked as known.")
    except Exception as e:
        print("Initial fetch failed:", e)
        if not known_ids:
            print("Cannot proceed without initial program data or existing known IDs. Exiting.")
            return

    while True:
        await asyncio.sleep(POLL_INTERVAL)
        try:
            token = auth.get_access_token()
            current_programs = fetch_programs(token)
        except Exception as e:
            print("Fetch error during polling:", e)
            continue

        current_ids = {p["id"] for p in current_programs}
        new_ids = current_ids - known_ids

        if not new_ids:
            known_ids = current_ids.copy()
            save_known_ids(known_ids)
            continue

        for new_id in sorted(list(new_ids)):
            prog = next((p for p in current_programs if p["id"] == new_id), None)
            if not prog:
                continue
            
            msg = (
                f"🆕 *New Program Alert!*\n"
                f"*Name:* {prog['name']}\n"
                f"*Reports:* {prog['reports']['count']}\n"
                f"*Description:* {prog['shortDescription']}\n"
                f"*Max Payout:* {prog['maxPayout']}\n"
                f"*Created:* {prog['created'].split('T')[0]}\n"
                f"[View logo]({prog['logo']})"
            )
            try:
                await bot.send_message(TELEGRAM_CHANNEL_ID, msg, parse_mode='Markdown')
                print(f"Notified about new program ID {new_id}: {prog['name']}")
                known_ids.add(new_id)
                save_known_ids(known_ids)
            except Exception as e:
                print(f"Failed to send notification for {prog['name']} (ID {new_id}): {e}")
        
        known_ids = current_ids.copy()
        save_known_ids(known_ids)


if __name__ == "__main__":
    try:
        asyncio.run(monitor())
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")
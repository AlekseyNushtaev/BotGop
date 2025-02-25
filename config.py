from dotenv import load_dotenv
import os

load_dotenv()

TG_TOKEN = os.environ.get("TG_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID"))
PROXY_API = os.environ.get("PROXY_API")
ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_IDS").split()}

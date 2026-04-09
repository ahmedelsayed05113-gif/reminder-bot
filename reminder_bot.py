from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
import discord
from discord.ext import commands, tasks
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Get secrets from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
PORT = int(os.getenv('PORT', 8000))

# Validate that secrets are loaded
if not TOKEN or not CHANNEL_ID:
    raise ValueError("ERROR: DISCORD_TOKEN or CHANNEL_ID not found in .env file!")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Meeting schedule configuration
schedule = [
    {
        "name": "Team Alaa Meeting",
        "time": "11:30",
        "days": ["Sunday", "Tuesday", "Wednesday", "Thursday"],
        "mentions": [
            "<@1491455952333836480>",
            "<@1265460544601718784>",
            "<@450060819862913024>",
            "<@1251933398117646377>",
            "<@947510112229134346>",
            "<@692433164924223649>",
            "<@1491700233405468697>"
        ]
    },
    {
        "name": "Team Esraa Meeting",
        "time": "11:00",
        "days": ["Sunday", "Tuesday", "Wednesday", "Thursday"],
        "mentions": [
            "<@1491483959018651759>",
            "<@1491564370600399010>",
            "<@1491447892919976007>",
            "<@802673838739161109>",
            "<@1491449087004770418>",
            "<@1136359365067157514>",
            "<@820016480284180531>",
            "<@1491707131924185198>"
        ]
    },
    {
        "name": "Business Meeting",
        "time": "10:00",
        "days": ["Monday"],
        "mentions": ["@everyone"]
    }
]

# Track sent reminders to avoid duplicates
last_sent = set()


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord"""
    print(f"Bot logged in as {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("Starting daily reminder task...")
    daily_reminder.start()


@tasks.loop(seconds=30)
async def daily_reminder():
    """Check every 30 seconds if any meeting should be announced"""
    now = datetime.now()
    current_day = now.strftime("%A")
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("ERROR: Channel not found")
        return
    
    for meeting in schedule:
        meeting_hour, meeting_minute = map(int, meeting["time"].split(":"))
        key = f"{meeting['name']}-{current_day}-{now.strftime('%Y-%m-%d')}-{meeting['time']}"
        
        if (
            now.hour == meeting_hour and
            now.minute == meeting_minute and
            current_day in meeting["days"] and
            key not in last_sent
        ):
            mentions = " ".join(meeting.get("mentions", ["@everyone"]))
            
            await channel.send(
                f"{mentions}\n"
                f"**Reminder:** {meeting['name']} is starting now!\n"
                f"Time: {meeting['time']}"
            )
            
            last_sent.add(key)
            print(f"Reminder sent for {meeting['name']} at {meeting['time']} on {current_day}")


@daily_reminder.before_loop
async def before_reminder():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()


# FastAPI lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Discord bot lifecycle with FastAPI"""
    # Startup: Start Discord bot in background
    asyncio.create_task(bot.start(TOKEN))
    print("Discord bot started in background")
    yield
    # Shutdown: Close Discord bot
    await bot.close()
    print("Discord bot closed")


# Create FastAPI app
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "bot_name": bot.user.name if bot.user else "Not connected",
        "bot_id": bot.user.id if bot.user else None,
        "is_ready": bot.is_ready()
    }


@app.get("/health")
async def health():
    """Health check for Railway"""
    return {
        "status": "healthy",
        "bot_ready": bot.is_ready()
    }


@app.get("/schedule")
async def get_schedule():
    """Get current meeting schedule"""
    return {
        "schedule": schedule,
        "reminders_sent_today": len(last_sent)
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False
    )

from fastapi import FastAPI
from contextlib import asynccontextmanager
import discord
from discord.ext import commands, tasks
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import pytz

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
SERVER_ID = os.getenv('SERVER_ID', '')  # Server ID واحد لكل الـ voice channels

if not TOKEN:
    raise ValueError("ERROR: DISCORD_TOKEN not found in environment variables!")
if not CHANNEL_ID:
    raise ValueError("ERROR: CHANNEL_ID not found in environment variables!")

# Timezone configuration - توقيت القاهرة
CAIRO_TZ = pytz.timezone('Africa/Cairo')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Meeting schedule configuration (بتوقيت القاهرة)
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
        ],
        "voice_channel_id": "1491449677504315463"
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
            "<@1491707131924185198>",
            "<@1491730423456206889>"
        ],
        "voice_channel_id": "1491449604687003748"
    },
    {
        "name": "Business Meeting",
        "time": "10:00",
        "days": ["Monday"],
        "mentions": ["@everyone"],
        "voice_channel_id": "1491473588686028930" 
    }
]

last_sent = set()


def get_voice_channel_link(voice_channel_id):
    """Generate voice channel link"""
    if SERVER_ID and voice_channel_id and voice_channel_id != "YOUR_ALAA_VOICE_CHANNEL_ID":
        return f"https://discord.com/channels/{SERVER_ID}/{voice_channel_id}"
    return None


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord"""
    cairo_time = datetime.now(CAIRO_TZ)
    print(f"✅ Bot logged in as {bot.user}")
    print(f"📊 Bot ID: {bot.user.id}")
    print(f"🕐 Cairo time: {cairo_time.strftime('%Y-%m-%d %H:%M:%S %A')}")
    print("⏰ Starting daily reminder task...")
    daily_reminder.start()


@tasks.loop(seconds=30)
async def daily_reminder():
    """Check every 30 seconds if any meeting should be announced"""
    now = datetime.now(CAIRO_TZ)
    current_day = now.strftime("%A")
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("❌ ERROR: Channel not found")
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
            
            message = f"{mentions}\n**Reminder:** {meeting['name']} is starting now!\n⏰ Time: {meeting['time']} (Cairo time)"
            
            voice_channel_id = meeting.get("voice_channel_id")
            if voice_channel_id:
                voice_link = get_voice_channel_link(voice_channel_id)
                if voice_link:
                    message += f"\n🎤 Join voice channel: {voice_link}"
            
            await channel.send(message)
            
            last_sent.add(key)
            print(f"✉️ Reminder sent for {meeting['name']} at {meeting['time']} on {current_day}")


@daily_reminder.before_loop
async def before_reminder():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Discord bot lifecycle with FastAPI"""
    # Startup
    asyncio.create_task(bot.start(TOKEN))
    print("🚀 Discord bot started in background")
    yield
    # Shutdown
    await bot.close()
    print("🛑 Discord bot closed")


# FastAPI app
app = FastAPI(
    title="Discord Meeting Reminder Bot",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Main endpoint"""
    cairo_time = datetime.now(CAIRO_TZ)
    return {
        "status": "online",
        "bot_name": bot.user.name if bot.user else "Not connected",
        "bot_id": bot.user.id if bot.user else None,
        "is_ready": bot.is_ready(),
        "cairo_time": cairo_time.strftime('%Y-%m-%d %H:%M:%S %A'),
        "timezone": "Africa/Cairo",
        "message": "Discord Meeting Reminder Bot is running! 🤖"
    }


@app.get("/health")
async def health():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy" if bot.is_ready() else "starting",
        "bot_ready": bot.is_ready()
    }


@app.get("/schedule")
async def get_schedule():
    """Get current meeting schedule"""
    cairo_time = datetime.now(CAIRO_TZ)
    return {
        "schedule": schedule,
        "reminders_sent_today": len(last_sent),
        "bot_status": "ready" if bot.is_ready() else "not ready",
        "cairo_time": cairo_time.strftime('%Y-%m-%d %H:%M:%S %A'),
        "timezone": "Africa/Cairo"
    }


@app.get("/status")
async def status():
    """Detailed status information"""
    cairo_time = datetime.now(CAIRO_TZ)
    return {
        "bot": {
            "connected": bot.is_ready(),
            "name": bot.user.name if bot.user else None,
            "id": bot.user.id if bot.user else None,
        },
        "channel": {
            "id": CHANNEL_ID,
            "found": bot.get_channel(CHANNEL_ID) is not None
        },
        "reminders": {
            "total_meetings": len(schedule),
            "sent_today": len(last_sent)
        },
        "time": {
            "cairo": cairo_time.strftime('%Y-%m-%d %H:%M:%S %A'),
            "timezone": "Africa/Cairo"
        }
    }

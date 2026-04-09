# 🚀 دليل الإعداد - Discord Meeting Reminder Bot

## 📋 الخطوات المطلوبة:

### 1️⃣ اجمع الـ IDs من Discord

على Discord، فعّل **Developer Mode** الأول:
- Settings → App Settings → Advanced → Developer Mode ✅

#### أ) Server ID (واحد بس):
- كليك يمين على اسم السيرفر
- اختار "Copy Server ID"
- مثال: `1234567890123456789`

#### ب) Text Channel ID (للرسائل):
- كليك يمين على الـ text channel اللي هيبعت فيه
- اختار "Copy Channel ID"
- مثال: `9876543210987654321`

#### ج) Voice Channel IDs (3 قنوات مختلفة):

**Team Alaa Voice Channel:**
- كليك يمين على voice channel بتاع Team Alaa
- اختار "Copy Channel ID"
- مثال: `1111111111111111111`

**Team Esraa Voice Channel:**
- كليك يمين على voice channel بتاع Team Esraa
- اختار "Copy Channel ID"
- مثال: `2222222222222222222`

**Business Voice Channel:**
- كليك يمين على voice channel بتاع Business
- اختار "Copy Channel ID"
- مثال: `3333333333333333333`

---

### 2️⃣ عدّل ملف main.py

في الـ schedule، استبدل:
```python
"voice_channel_id": "YOUR_ALAA_VOICE_CHANNEL_ID"
```

بالـ ID الحقيقي:
```python
"voice_channel_id": "1111111111111111111"
```

كرر ده لكل الـ 3 meetings!

---

### 3️⃣ ضبط Railway Variables

على Railway → Variables:

```
DISCORD_TOKEN=MTIzNDU2Nzg5...
CHANNEL_ID=9876543210987654321
SERVER_ID=1234567890123456789
```

**مهم:** بدون علامات تنصيص!

---

### 4️⃣ Deploy الملفات

ارفع:
- ✅ main.py (المعدل بالـ voice channel IDs)
- ✅ requirements.txt
- ✅ nixpacks.toml

---

## 📨 شكل الرسالة النهائية:

### Team Alaa Meeting (11:30):
```
@User1 @User2 @User3...
**Reminder:** Team Alaa Meeting is starting now!
⏰ Time: 11:30 (Cairo time)
🎤 Join voice channel: https://discord.com/channels/SERVER_ID/ALAA_VOICE_ID
```

### Team Esraa Meeting (11:00):
```
@User4 @User5 @User6...
**Reminder:** Team Esraa Meeting is starting now!
⏰ Time: 11:00 (Cairo time)
🎤 Join voice channel: https://discord.com/channels/SERVER_ID/ESRAA_VOICE_ID
```

### Business Meeting (10:00):
```
@everyone
**Reminder:** Business Meeting is starting now!
⏰ Time: 10:00 (Cairo time)
🎤 Join voice channel: https://discord.com/channels/SERVER_ID/BUSINESS_VOICE_ID
```

---

## ✅ Checklist:

- [ ] Server ID محفوظ
- [ ] Text Channel ID محفوظ
- [ ] Team Alaa Voice Channel ID محفوظ
- [ ] Team Esraa Voice Channel ID محفوظ
- [ ] Business Voice Channel ID محفوظ
- [ ] عدّلت الـ IDs في main.py
- [ ] رفعت الملفات على Railway
- [ ] حطيت الـ Variables على Railway
- [ ] البوت شغال ومتصل

🎉 جاهز!

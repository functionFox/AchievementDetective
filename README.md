# 🎯 Achievement Detective

A real-time Steam achievement tracker designed for OBS overlays.

Displays your achievements as they unlock with animated toasts and a scrolling list — perfect for streamers who want their progress visible on screen.

---

## ✨ Features

- 🔄 Real-time achievement polling  
- 🎉 Toast notifications for newly unlocked achievements  
- 📜 Scrolling achievement list (Ticker or Obelisk styles)  
- 🎨 Customizable colors, opacity, and layout  
- 🧠 Smart detection (no duplicate or historical spam)  
- 🧪 Built-in test toast system for debugging  

---

## 💖 Support Development

Achievement Detective is currently developed and maintained in my free time.

If you enjoy the project, find it useful for your streams, or just want to support continued updates and improvements, you can support development here:

- ☕ Ko-fi: https://ko-fi.com/functionfox
- 💸 GitHub Sponsors: https://github.com/sponsors/functionFox

Support helps fund continued work on:
- packaged releases
- new overlay styles and animations
- sound effects and customization
- quality-of-life improvements
- broader platform support

No features are paywalled, and the project will remain freely available.

If this made your stream setup a little cooler, consider tossing a coin to the fox 🦊

## ⚠️ Requirements

- Python 3.10+  
- Steam account with public game data  
- Steam Web API Key  

Get your API key here:  
https://steamcommunity.com/dev/apikey  

---

## 🚀 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/functionFox/AchievementDetective.git
   cd AchievementDetective
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your Steam credentials:

   Create a `.env` file in the project root:

   ```env
   STEAM_API_KEY=your_api_key_here
   STEAM_STEAMID64=your_steamid64_here
   ```
   
You can find your STEAM_STEAMID64 by opening your profile page on Steam. The long number in the URL
will be your STEAM_STEAMID64.

---

## ▶️ Running the App

```bash
python server.py
```

Then open:

http://127.0.0.1:5000/config

---

## 🎮 Using with OBS

1. Add a **Browser Source**  
2. Set URL to:
   ```
   http://127.0.0.1:5000/
   ```
3. Set width/height as desired  
4. Done — your overlay will update automatically  

---

## ⚙️ Configuration

In the config page you can:

- Select your active game  
- Change display mode (Ticker / Obelisk)  
- Adjust colors and styling  
- Tune opacity and text stroke  
- Control obelisk angle  

---

## 🧪 Testing Toasts

You can trigger test notifications:

```bash
curl -X POST http://127.0.0.1:5000/api/test-toast -H "Content-Type: application/json" -d '{"appid":"YOUR_APP_ID","apiname":"TEST","display_name":"Test Toast","description":"Testing notification."}'
```

---

## 🧠 Notes

- Achievements are cached locally in SQLite  
- Historical achievements will not trigger notifications  
- Toasts are queued and displayed sequentially  
- Queue is capped to prevent overflow (20 events)  

---

## 📦 Status

**Alpha — stable for personal use and development**

Future improvements:
- packaged release (no Python required)  
- optional sound effects  
- improved first-run setup  
- backend proxy (remove API key requirement)  
- Additional and more modular layout formats

---

## 💖 Credits

Built by functionFox  
Powered by caffeine, spite, and Steam APIs  
If this helped your stream look cooler, consider tossing a coin 🪙
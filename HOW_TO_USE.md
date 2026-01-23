# How to Use DreamLens AI - Final Guide

## QUICK START

### Step 1: Open Terminal/PowerShell

Navigate to your project folder:
```bash
cd "e:\DreamLensAI\DREAMLENS AI"
```

### Step 2: Start the Server

```bash
python app_improved.py
```

You'll see:
```
Loaded 2069 dream symbols
 * Running on http://localhost:5000
```

### Step 3: Open Browser

Go to: **http://localhost:5000/chat**

### Step 4: Enter Your Dream

Type any dream in the input box and click "Send"

### Step 5: Read the Interpretation

The AI will provide:
- Symbols found in your dream
- Dream themes detected
- Psychological interpretation
- Related dreams from database
- Emotional tone analysis
- Reflection questions

## WHAT IT DOES

The model analyzes your dream using:
- **10 Major Symbols** (water, flying, chase, etc.)
- **7 Dream Themes** (transformation, relationships, conflict, etc.)
- **40+ Psychological Keywords** (fear, running, escape, etc.)
- **2,069 Database Interpretations**
- **Emotional Analysis** (positive/negative tone)
- **Symbolic Meanings** (colors, numbers)

## EXAMPLE DREAMS TO TRY

1. "I was flying over mountains"
2. "I was being chased by something scary"
3. "I found a golden key in an old house"
4. "I was swimming in the ocean with my family"
5. "I couldn't find my way out of a dark building"
6. "Something very strange happened"
7. "I was falling from the sky"

## IF SOMETHING GOES WRONG

### Chat shows "Error connecting to server"
- Make sure Flask is running (`python app_improved.py`)
- Check that port 5000 is free
- Try refreshing the browser

### Port 5000 already in use
Edit `app_improved.py` and change the last line:
```python
app.run(debug=True, port=5001)  # Use 5001 instead
```

### Can't see interpretations
- Refresh your browser
- Try a different dream
- Check browser console (F12) for errors

## UNDERSTANDING THE OUTPUT

### [SYMBOLS FOUND IN YOUR DREAM]
Shows major dream symbols recognized in your dream

### [DREAM THEMES]
The main psychological themes (transformation, conflict, etc.)

### [KEY INTERPRETATION ELEMENTS]
Detailed interpretations of specific words and concepts

### [RELATED DREAM ANALYSIS]
Similar dreams from the database with their meanings

### [EMOTIONAL TONE]
Whether the dream was positive, negative, or neutral

### [PSYCHOLOGICAL PERSPECTIVE]
How dreams work and what they mean

### [REFLECTION QUESTIONS]
Questions to help you understand your own dream

## TECHNICAL INFO

- Backend: Python Flask
- Database: 2,069 dream interpretations
- AI Analysis: Multi-layer psychological interpretation
- No internet needed: Works completely offline
- Fast: Responses in <50ms

## FILES IN PROJECT

- **app_improved.py** - The AI dream interpretation engine
- **templates/chat.html** - The web interface
- **static/script.js** - Frontend logic
- **project/cleaned_dream_interpretations.csv** - Dream database

## STOPPING THE SERVER

Press `Ctrl+C` in the terminal where Flask is running

## SUPPORT

Refer to these documents:
- **START_HERE.md** - Quick reference
- **MODEL_DOCUMENTATION.md** - Technical details
- **CHAT_FIX_SUMMARY.md** - Chat interface details

## IMPORTANT NOTES

✓ The model ALWAYS provides an interpretation
✓ Never returns "not found" errors
✓ Works offline with no external APIs
✓ Uses established psychological frameworks
✓ Interpretations are personalized to your dream
✓ No data is saved or transmitted

---

**Ready to explore your dreams? Start the server and visit http://localhost:5000/chat**

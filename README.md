# 🌙 DreamLens AI

### AI-Powered Dream Interpretation & Psychological Insight Platform

DreamLens AI is an intelligent dream analysis platform that combines **Psychology, Symbolic Analysis, Natural Language Processing (NLP), and Large Language Models (LLMs)** to help users explore the deeper meanings behind their dreams.

Rather than predicting the future, DreamLens AI encourages self-reflection and emotional awareness by uncovering recurring patterns, emotions, fears, desires, and personal growth opportunities hidden within dreams.

---

## 🚀 Overview

DreamLens AI transforms dream descriptions into meaningful psychological insights using:

* 🧠 Jungian Psychology
* 🔍 Symbol Analysis
* 📚 TF-IDF Dream Pattern Matching
* 🤖 Groq LLM Integration
* 💾 Dream History Storage
* 📈 Dream Reflection & Self-Discovery

---

## ✨ Features

### 💤 Dream Interpretation

* AI-generated dream analysis
* Emotional interpretation
* Symbol recognition
* Personalized reflection questions

### 🧠 Psychological Insights

* Jungian archetypes
* Freudian symbolism
* Modern cognitive psychology
* Emotional pattern detection

### 🔍 Symbol Matching Engine

* TF-IDF vectorization
* Similar dream retrieval
* Context-aware interpretation

### 📚 Dream History

* Store analyzed dreams
* Search previous dreams
* Track recurring symbols

### 🤖 AI-Powered Responses

* Groq API integration
* Llama 3.3 70B model
* Structured dream reports

---

## 🏗️ System Architecture

```text
                    ┌─────────────┐
                    │    User     │
                    └──────┬──────┘
                           │
                           ▼

                 ┌───────────────────┐
                 │ Frontend Interface│
                 │ HTML / CSS / JS   │
                 └─────────┬─────────┘
                           │
                           ▼

                 ┌───────────────────┐
                 │ Flask Backend API │
                 └─────────┬─────────┘
                           │

        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼

 ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
 │ TF-IDF      │   │ Dream       │   │ SQLite      │
 │ Matcher     │   │ Processing  │   │ Database    │
 └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ▼

                ┌───────────────────┐
                │ Context Builder   │
                └─────────┬─────────┘
                          │
                          ▼

                ┌───────────────────┐
                │ Groq LLM Service  │
                │ Llama 3.3 70B     │
                └─────────┬─────────┘
                          │
                          ▼

                ┌───────────────────┐
                │ DreamLens Engine  │
                │ Psychology Layer  │
                └─────────┬─────────┘
                          │
                          ▼

                ┌───────────────────┐
                │ Final Analysis &  │
                │ Insights          │
                └───────────────────┘
```

---

## 🔄 Workflow

1. User submits a dream description.
2. Dream text is preprocessed.
3. TF-IDF engine identifies related symbols and dream patterns.
4. Context is generated from matched symbols.
5. Dream + context are sent to the Groq LLM.
6. AI generates:

   * Dream Atmosphere
   * Symbol Analysis
   * Emotional Interpretation
   * Psychological Insights
   * Mythological Reflection
   * Reflection Questions
7. Results are displayed and stored for future reference.

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask
* SQLite

### AI & NLP

* Groq API
* Llama 3.3 70B
* Scikit-Learn
* TF-IDF Vectorization
* NLTK

### Frontend

* HTML5
* CSS3
* JavaScript

### Deployment

* Render
* Vercel
* Gunicorn

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 🚀 Installation

```bash
git clone https://github.com/hariharanm-ds/DREAMLENS-AI.git

cd DREAMLENS-AI

pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
```

Run the application:

```bash
python app.py
```

---

## 🎯 Future Roadmap

* 📊 Dream Analytics Dashboard
* 📔 Personalized Dream Journal
* 🔄 Dream Pattern Tracking
* 🎨 AI Dream Image Generation
* 📱 Mobile Application
* 🌍 Multi-Language Support
* 🔐 User Authentication

---

## 👨‍💻 Author

**Hariharan M**

Aspiring Data Analyst | AI Developer

---

## 📜 Disclaimer

DreamLens AI provides educational and reflective interpretations of dreams. The generated insights are exploratory in nature and should not be considered psychological, medical, or therapeutic advice.

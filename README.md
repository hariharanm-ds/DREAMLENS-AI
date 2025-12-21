# DREAMLENS AI ✨

A beautiful, AI-powered dream interpretation web application using open-source Ollama and Mistral LLM.

## Features

- 🌙 Beautiful night-dream themed UI with gradient effects
- 🤖 AI-powered dream interpretation using Mistral 7B model
- 🗄️ 2,080+ dream symbol interpretations database
- 💻 Completely open-source and runs locally
- 🔒 Privacy-first - no data sent to external servers
- 📱 Fully responsive design
- ⚡ Fast responses with streaming support

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Flask (Python)
- **LLM**: Ollama with Mistral 7B
- **Database**: CSV (dream interpretations)

## Requirements

- Python 3.9+
- Ollama (https://ollama.ai)
- Mistral model (4.4GB)

## Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dreamlens-ai.git
cd dreamlens-ai
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
pip install gunicorn
```

4. **Install and run Ollama**
```bash
# Download from https://ollama.ai
ollama pull mistral
ollama serve
```

5. **Run the application** (in another terminal)
```bash
python app_llm.py
```

6. **Open in browser**
Navigate to `http://localhost:5000/chat`

## Deployment

### Deploy to Railway

1. Push code to GitHub
2. Connect GitHub to Railway (https://railway.app)
3. Railway will auto-detect Python and use Procfile
4. Set environment variable: `OLLAMA_HOST=http://ollama:11434`

### Deploy to Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create dreamlens-ai`
4. Push: `git push heroku main`

### Environment Variables

- `FLASK_DEBUG`: Set to "true" for debug mode (default: false)
- `PORT`: Port to run server on (default: 5000)
- `OLLAMA_HOST`: Ollama API endpoint (for remote deployment)

## Usage

1. Navigate to the chat page
2. Describe your dream in detail
3. Click "Send"
4. Wait for AI interpretation (30-60 seconds)
5. Get detailed analysis with:
   - Initial Impression
   - Symbol Analysis
   - Emotional Interpretation
   - Psychological Perspective
   - Potential Meanings
   - Reflection Questions

## API Endpoints

### GET `/`
Home page

### GET `/chat`
Chat interface

### POST `/interpret`
Generate dream interpretation
- **Body**: `{"dream": "your dream description"}`
- **Response**: `{"success": true, "interpretation": "..."}`

### GET `/health`
System status and health check

## Project Structure

```
dreamlens-ai/
├── app_llm.py              # Main Flask application
├── templates/
│   ├── index.html         # Home page
│   └── chat.html          # Chat interface
├── static/
│   └── style.css          # Styling
├── project/
│   └── cleaned_dream_interpretations.csv  # Dream database
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── railway.json          # Railway deployment config
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

## Performance Notes

- First request may take 30-60 seconds (model loading into memory)
- Subsequent requests are faster (15-30 seconds)
- Running on local machine: ~30 seconds per interpretation
- Cloud deployment depends on server specs

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check if Mistral is downloaded: `ollama pull mistral`
- Verify port 11434 is accessible

### Timeout errors
- Increase timeout in `app_llm.py` (currently 180 seconds)
- Ensure sufficient RAM (minimum 8GB recommended)
- Close other applications

### Slow responses
- Mistral model is 7B parameters, takes time to process
- Use smaller model if needed: `ollama pull neural-chat`
- Deploy on more powerful hardware

## Future Enhancements

- Multiple LLM model support
- Dream journal with history
- User authentication
- Cloud synchronization
- Mobile app
- Voice input
- Export interpretations as PDF

## License

MIT License - feel free to use and modify

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## Support

Found a bug? Have a suggestion?
- Create an issue on GitHub
- Contact: your-email@example.com

## Acknowledgments

- Ollama team for amazing LLM framework
- Mistral AI for open-source model
- Dream interpretation database contributors

---

Made with ❤️ for dreamers and the curious

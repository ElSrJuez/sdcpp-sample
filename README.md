# AI Image Generator

A simple yet elegant web application for generating AI images using Stable Diffusion. Built with Flask and optimized for mobile devices with a clean, modern interface.

## ✨ Features

- **Mobile-First Design**: Responsive interface optimized for touch devices
- **Simple & Clean**: Minimal UI focused on core functionality  
- **Real-time Generation**: Generate images from text prompts instantly
- **Touch-Friendly**: Large tap targets and smooth animations
- **Config-Driven**: All settings externalized for easy customization

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Access to a Stable Diffusion API server
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd diff-webapp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application**
   ```bash
   cp config.json.sample config.json
   ```
   Edit `config.json` with your Stable Diffusion server details.

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000`

## 📱 Mobile Experience

The app is designed mobile-first with:

- **Responsive Layout**: Adapts beautifully to any screen size
- **Touch Gestures**: Tap, swipe, and scroll interactions
- **Auto-Resize**: Dynamic text area sizing
- **Smooth Animations**: Polished loading states and transitions

## ⚙️ Configuration

All settings are managed through `config.json`:

```json
{
  "sd_api": {
    "url": "http://your-sd-server:port/v1/images/generations",
    "model": "your_model_name",
    "default_size": "512x512"
  },
  "app": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "files": {
    "output_dir": "out",
    "max_prompt_length": 500
  }
}
```

## 🏗️ Architecture

- **Backend**: Flask with clean separation of concerns
- **Frontend**: Vanilla JavaScript with mobile-first CSS
- **Storage**: Local file system for generated images
- **API Integration**: RESTful communication with SD server

## 📂 Project Structure

```
diff-webapp/
├── app.py                 # Main Flask application
├── config.json.sample     # Configuration template
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main interface template
├── static/
│   ├── css/
│   │   └── style.css     # Responsive styles
│   └── js/
│       └── app.js        # Frontend logic
├── out/                  # Generated images (created automatically)
└── scratchpad/
    └── diff-gen-webapp.md # Design documentation
```

## 🎯 Design Principles

- **Simplicity First**: Less is more - focus on essential features
- **Config-Driven**: No hardcoded defaults or fallbacks
- **DRY Architecture**: Don't Repeat Yourself - clean, maintainable code
- **Mobile-Centric**: Touch-first design that scales up to desktop

## 🚧 Development Status

- ✅ **Phase 1**: Core functionality complete
- ⏳ **Phase 2**: Enhanced UI in development
- 📋 **Phase 3**: Advanced features planned

See [design documentation](scratchpad/diff-gen-webapp.md) for detailed roadmap.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on mobile devices
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

Built with modern web technologies and designed for the mobile-first world.

---

*Simple. Clean. Mobile-First.*
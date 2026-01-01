# AI Image Generator

**Version 0.1** - A simple yet elegant web application for generating AI images using Stable Diffusion. Built with Flask and optimized for mobile devices with a clean, modern interface.

## 🎯 Project Objectives

### Core Objectives (v0.1 Complete ✅)
- **Mobile-First AI Generation**: Touch-optimized interface for generating images from text prompts
- **Stable Diffusion Integration**: Direct API integration with local SD server using XML parameter embedding
- **Gallery System**: Mobile-responsive image gallery with metadata storage and thumbnail generation
- **Size & Quality Control**: 5 size options and 3 quality presets (Low/Medium/High) affecting generation parameters
- **Async Processing**: Background job system with real-time progress updates and proper timeout management

### Meta Objectives (Architectural Philosophy ✅)
- **Simplicity First**: "Less is more" - focus on essential features with clean, minimal UI
- **Config-Driven Architecture**: Zero hardcoded values, all settings externalized to config.json
- **DRY Principles**: Don't Repeat Yourself - clean, maintainable code with separation of concerns
- **Mobile-Centric Design**: Touch-first responsive design that scales up to desktop
- **Production Ready**: Proper error handling, logging, timeout management, and async processing

## ✨ Features

- **Mobile-First Design**: Responsive interface optimized for touch devices with gesture support
- **Size & Quality Controls**: 5 size options (256²→1024²) and 3 quality presets (4/10/20 steps)
- **Real-time Generation**: Async background processing with live progress updates
- **Mobile Gallery**: Touch-optimized thumbnail gallery with AI metadata storage
- **Advanced Parameters**: XML embedding system for server parameter control
- **Config-Driven**: All settings externalized for easy customization and deployment

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

The app delivers a premium mobile experience with:

- **Touch-Optimized Controls**: Size and quality selectors designed for finger interaction
- **Auto-Responsive Layout**: CSS Grid adapting seamlessly from mobile to desktop  
- **Gesture Support**: Touch navigation through gallery with swipe interactions
- **Progressive Loading**: Async job processing with real-time progress feedback
- **Smooth Animations**: Polished transitions and loading states throughout the interface

## ⚙️ Configuration

### Key Configuration Areas
- **SD API Integration**: Server URL, model selection, and timeout management
- **Async Polling**: Frontend polling intervals and maximum wait times
- **Gallery Settings**: Thumbnail sizes, pagination, and database configuration  
- **File Management**: Output directories and prompt length limits

## 🏗️ Architecture

### Backend Components
- **Flask Application**: Async job processing with background threading
- **TinyDB Gallery**: Lightweight JSON database for AI metadata storage  
- **Image Services**: Thumbnail generation and optimized file serving
- **SD API Integration**: XML parameter embedding with timeout management
- **Config Management**: Centralized settings with polling and timeout configuration

### Frontend Features  
- **Mobile-First Interface**: Touch-optimized controls with auto-resizing components
- **Responsive Design**: CSS Grid layouts adapting from mobile to desktop
- **Async UI**: Real-time job polling with config-driven timeout management
- **Gallery System**: Swipeable thumbnails with metadata display
- **Parameter Controls**: Size selector and quality presets affecting generation

### Technical Stack
- **Backend**: Flask 3.0.0 with Python threading for background jobs
- **Database**: TinyDB 4.8.0 for lightweight JSON-based storage
- **Frontend**: Vanilla JavaScript with mobile-first responsive CSS
- **Image Processing**: Pillow for thumbnail generation and optimization
- **API Integration**: RESTful communication with Stable Diffusion server

## 📂 Project Structure

```
diff-webapp/
├── app.py                    # Main Flask application with async job processing
├── config.json              # Centralized configuration (SD API, polling, gallery)
├── requirements.txt          # Python dependencies
├── services/
│   ├── database.py          # TinyDB gallery operations
│   └── images.py            # Thumbnail generation and image services
├── templates/
│   ├── index.html           # Mobile-first generation interface
│   └── gallery.html         # Responsive image gallery
├── static/
│   ├── css/
│   │   └── style.css        # Mobile-first responsive styling
│   └── js/
│       └── app.js           # Config-driven frontend with async polling
├── out/                     # Generated images (auto-created)
├── out/thumbs/              # Thumbnail cache (auto-created)
├── gallery.json             # TinyDB database (auto-created)
└── scratchpad/
    ├── diff-gen-webapp.md   # Design documentation and roadmap
    └── server-learnings.md  # SD server API analysis and integration guide
```

## 🎯 Design Principles

- **Simplicity First**: "Less is more" - minimal UI focused on essential features
- **Config-Driven**: No hardcoded defaults or fallbacks - all settings externalized  
- **DRY Architecture**: Don't Repeat Yourself - clean, maintainable code structure
- **Mobile-Centric**: Touch-first design that scales up gracefully to desktop
- **Production Ready**: Comprehensive error handling, logging, and timeout management

## � Quick Start

### Prerequisites

- Python 3.8+
- Access to a Stable Diffusion API server  
- Modern web browser

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd diff-webapp
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure application**
   ```bash
   # Edit config.json with your SD server details
   # Update sd_api.url to point to your server
   ```

3. **Run application**
   ```bash
   python app.py
   # Navigate to http://localhost:5000
   ```

## �🚧 Development Status

### ✅ Version 0.1 Complete
- **Phase 1**: Core functionality with mobile-first interface
  - SD API integration with XML parameter embedding
  - Touch-optimized prompt input and generation
  - Async background processing with job management  
  - Responsive image display and file management

- **Phase 2**: Enhanced gallery system  
  - TinyDB metadata storage for AI generation history
  - Mobile-responsive thumbnail gallery with touch navigation
  - Real-time progress updates and error handling
  - Size and quality controls affecting generation parameters

- **Server Integration**: Advanced parameter control
  - 5 size options: 256×256, 512×512, 1024×512, 512×1024, 1024×1024
  - 3 quality presets: Low (4 steps), Medium (10 steps), High (20 steps)
  - XML embedding system: `<sd_cpp_extra_args>{"steps": N}</sd_cpp_extra_args>`
  - Config-driven timeout alignment and polling management

### 🔄 Ready for Production  
- Complete mobile-first interface with touch optimization
- Robust async processing with proper error handling and timeouts
- Config-driven architecture with zero hardcoded values
- Full gallery system with metadata storage and thumbnail generation
- Advanced parameter control via server XML embedding system

### 📋 Future Enhancements (Post-v0.1)
- **Advanced Parameters**: Collapsible section for power users (cfg_scale, seed, negative_prompt)
- **PWA Features**: Offline support and home screen installation capabilities  
- **Enhanced Gestures**: Swipe batch generation and haptic feedback integration

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
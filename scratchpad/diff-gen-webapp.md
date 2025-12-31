# Diffusion Image Generation Web App

## Overview
A simple but attractive Flask web application optimized for mobile devices that provides an intuitive interface for generating images using our local Stable Diffusion server API. Focus on clean, modern design with excellent mobile responsiveness.

## Coding parameters:
- Simplicity is key, less is more
- Still, we aim for attractive
- DRY, Separation of Concerns
- Config-driven, we hate in-code defaults and fail-/fall-backs
- What did we say about Simplicity?

## API Integration
Based on the existing SD server at `http://phantom.homenet:4242/v1/images/generations`

### API Specification (So far, as discovered, if anything beyond is needed, should validate with sd-server docs)
- **Endpoint**: `POST /v1/images/generations`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "model": "z_image_turbo",
    "prompt": "user input text description",
    "size": "512x512",
    "n": 1,
    "response_format": "b64_json"
  }
  ```
- **Response**: JSON with `data[0].b64_json` containing base64 encoded PNG

## Web App Architecture

### Frontend Features
1. **Mobile-First Prompt Input**
   - Large, touch-friendly text area for prompts
   - Prominent, attractive generate button with smooth animations
   - Auto-resize, auto-rotate, UI elements move dynamically for on mobile

2. **Responsive Image Display**
   - Full-width image preview that scales to screen

### Backend Components
1. **Flask Application**
   - Main route for web interface
   - API route for image generation
   - Static file serving for generated images
   - All Users, same history (no authentication, no user profiles)

2. **SD API Integration**
   - HTTP client to communicate with local SD server
   - Base64 image decoding
   - Image file management

3. **File Management**
   - Save generated images to `./out/` directory
   - Generate short, unique filenames based on prompt with simplified readable timestamp

## Design Principles
- **Mobile-First**: Designed primarily for mobile devices, enhanced for desktop
- **Simple & Clean**: Minimal UI with focus on core functionality
- **Modern Aesthetics**: Contemporary design with smooth animations and transitions
- **Touch-Friendly**: Large tap targets
- **Fast Loading**: Optimized images, progressive loading, minimal dependencies

## Mobile Considerations
- Viewport meta tag for proper mobile scaling
- Touch-friendly button sizes (minimum 44px)
- Swipe gestures for navigation
- Responsive breakpoints: Mobile (<768px), Tablet (768-1024px), Desktop (>1024px)
- Optimized for both portrait and landscape orientations

## File Structure
```
diff-webapp/
├── app.py              # Main Flask application
├── templates/
│   └── index.html      # Mobile-first responsive template
├── static/
│   ├── css/
│   │   ├── style.css   # Mobile-first responsive styling
│   │   └── mobile.css  # Mobile-specific enhancements
│   ├── js/
│   │   ├── app.js      # Core functionality with touch support
│   │   └── mobile.js   # Mobile gestures and PWA features
│   ├── icons/          # PWA icons for home screen
│   └── images/         # UI assets and placeholders
├── out/                # Generated images directory
├── manifest.json       # PWA manifest
├── config.json         # App configuration
└── requirements.txt    # Python dependencies
```

## Implementation Plan

### Phase 1: Mobile-First Core
- [x] 1. SD API working (confirmed via PowerShell)
- [ ] 2. Mobile-responsive Flask app with touch-friendly prompt input
- [ ] 3. Responsive image generation and display
- [ ] 4. Always File saving with timestamps
- [ ] 5. Basic mobile gestures (tap, swipe)

### Phase 2: Attractive Mobile UI
- [ ] 6. Modern CSS with mobile-first responsive design
- [ ] 7. Smooth loading animations and transitions
- [ ] 8. Touch-optimized error handling and feedback
- [ ] 9. Swipeable image gallery with smooth transitions
- [ ] 10. Device orientation optimization

### Phase 3: Enhanced Mobile Experience
- [ ] 11. Touch-friendly prompt presets with quick selection
- [ ] 12. Gesture-based batch generation
- [ ] 13. Offline support and image caching
- [ ] 14. Mobile-friendly image download with share options
- [ ] 15. PWA manifest for home screen installation

## Future Features (Post-MVP)
- Clean dropdown for image sizes (512x512, 768x768, 1024x1024)
- Simple toggle for number of images (1-4)
- Touch-friendly download button with icon
- Elegant loading animation with progress indication
- Swipe gestures for multiple images on mobile
- Gesture support and haptic feedback
- Progressive Web App (PWA) capabilities for home screen installation
- Mobile Gallery:
  - Responsive grid layout (1 column mobile, 2-3 desktop)
  - Touch-optimized thumbnails with smooth hover effects
  - Swipeable image carousel for full-size viewing
  - Long-press for quick actions on mobile
- File Management:
  - Cleanup old files (optional)
  - Batch operations
   
## Technical Requirements
- Python 3.8+
- Flask with mobile-optimized templates
- Requests library for HTTP calls
- CSS Framework: Custom responsive CSS or lightweight framework (Bootstrap/Tailwind)
- JavaScript: Vanilla JS with touch event support
- PWA support: Service worker for offline capabilities
- Image optimization: PIL/Pillow for thumbnail generation
- Access to SD server at configured endpoint

## Configuration
- Server URL configurable via config.json
- Output directory configurable
- Default generation parameters
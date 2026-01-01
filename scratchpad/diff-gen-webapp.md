### Advanced Parameters (Always Visible)
```javascript
// Advanced parameters - NO defaults, only sent when user specifies
// UI always shows advanced controls at the bottom of the form (never collapsed)
const ADVANCED_PARAMS = {
   cfg_scale: null,       // Guidance scale (server default used if not specified)
   seed: null,            // Random seed (server random if not specified)
   negative_prompt: "",   // Things to avoid (empty = not sent)
   clip_skip: null,       // CLIP layers to skip (server default if not specified)
   batch_count: null      // Override n parameter (server default if not specified)
};
```
2. **Advanced Mode**: Optional parameter control (always visible)
    ```javascript
    // Only build parameters that user explicitly set
    const advancedParams = {};
    if (customSteps && customSteps !== qualitySteps[quality]) advancedParams.steps = customSteps;
    if (cfgScale && cfgScale !== "") advancedParams.cfg_scale = parseFloat(cfgScale);
    if (seed && seed !== "") advancedParams.seed = parseInt(seed);
    if (negativePrompt && negativePrompt.trim() !== "") advancedParams.negative_prompt = negativePrompt;
    if (clipSkip && clipSkip !== "") advancedParams.clip_skip = parseInt(clipSkip);
   
    // Only embed if user set any advanced parameters
    const fullPrompt = Object.keys(advancedParams).length > 0 
       ? `${userPrompt} <sd_cpp_extra_args>${JSON.stringify(advancedParams)}</sd_cpp_extra_args>`
       : `${userPrompt} <sd_cpp_extra_args>{"steps": ${qualitySteps[quality]}}</sd_cpp_extra_args>`;
    ```
1. **Phase 2.1**: Update UI with basic controls
   - Size selector: 256x256, 512x512 (default), 1024x512, 512x1024, 1024x1024
   - Quality presets: Low (4 steps, default), Medium (10 steps), High (20 steps)
   - Advanced section always visible at the bottom of the form (no collapsing, no preset values)
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
- [x] 2. Mobile-responsive Flask app with touch-friendly prompt input
- [x] 3. Responsive image generation and display
- [x] 4. Always File saving with timestamps
- [x] 5. Basic mobile gestures (tap, swipe)

### Phase 2: Attractive Mobile UI
**Focus: Simple but attractive Mobile Gallery with basic AI image meta info tracking (TinyDB)**

**Gallery Features:**
- Responsive grid layout (1 column mobile, 2-3 desktop)
- Touch-optimized thumbnails with smooth hover effects  
- Swipeable image carousel for full-size viewing
- Long-press for quick actions on mobile
- Basic metadata display (model, prompt, timestamp, size)
- Server parameter display (method: Euler, steps: 20, seed: 42 - server controlled)

**Implementation Tasks:**
- [x] 6. Add TinyDB to requirements and integrate for metadata storage
- [x] 7. Create gallery route and template with responsive grid
- [x] 8. Update image generation to store metadata in TinyDB
- [x] 9. Implement thumbnail generation for performance
- [x] 10. Add swipeable carousel for full-size image viewing
- [x] 11. Enhance CSS with gallery styling and smooth transitions
- [x] 12. Add touch gestures for gallery navigation

**Development Notes:**
- TinyDB file: `gallery.json` (simple, no setup required)
- Thumbnail sizes: 300x300 for mobile, 400x400 for desktop
- Metadata schema: `{id, filename, prompt, model, size, generation_timestamp, server_info}`
- Server parameters are FIXED: Euler method, 20 steps, seed 42 (not user controllable)
- Use CSS Grid for responsive layout (auto-fit, minmax)
- Implement lazy loading for thumbnails on mobile

**Server Reality Check:**
- ❌ Advanced parameters (steps, cfg_scale, seed) NOT controllable via API
- ✅ Only prompt, model, size, n, response_format are API parameters
- ✅ Server uses fixed: Euler method, 20 steps, seed 42
- 📋 **TODO**: Research server documentation for actual parameter support

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
- File Management:
  - Cleanup old files (optional)
  - Batch operations
   
## Technical Requirements
- Python 3.8+
- Flask with mobile-optimized templates
- Requests library for HTTP calls
- TinyDB for lightweight metadata storage
- Pillow (PIL) for thumbnail generation
- CSS Framework: Custom responsive CSS or lightweight framework (Bootstrap/Tailwind)
- JavaScript: Vanilla JS with touch event support
- PWA support: Service worker for offline capabilities
- Access to SD server at configured endpoint

## Configuration
- Server URL configurable via config.json
- Output directory configurable
- Gallery settings (thumbnail sizes, pagination)

## Development Considerations

### Phase 2 Technical Notes
- **TinyDB Integration**: Lightweight JSON-based database, perfect for metadata
- **Image Processing**: Generate thumbnails on upload, serve optimized versions
- **Mobile Performance**: Lazy load thumbnails, infinite scroll or pagination
- **File Structure**: Organize thumbnails in separate directory (`out/thumbs/`)
- **Error Handling**: Graceful degradation if thumbnails missing
- **Config Extensions**: Add gallery settings to config.json

### Code Architecture
- **Database Layer**: Simple TinyDB operations (insert, query, update)
- **Image Service**: Separate module for thumbnail generation and serving
- **Gallery Routes**: RESTful endpoints for gallery data
- **Frontend Components**: Modular JS for gallery, carousel, and touch handling
- Default generation parameters
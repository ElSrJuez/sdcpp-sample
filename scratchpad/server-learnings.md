# SD Server API Analysis - Technical Learnings

Based on analysis of `server-main.cpp`, here are the definitive findings about the Stable Diffusion server API capabilities.

## 🔌 API Endpoint

**POST** `/v1/images/generations`
- Content-Type: `application/json`
- Body: JSON object with parameters

## 📥 Request Parameters

### Direct JSON Parameters (Standard)
```json
{
  "prompt": "string",           // Required. Text description for image generation
  "n": 1,                      // Optional. Number of images (1-8, clamped by server)
  "size": "512x512",           // Optional. Format: "widthxheight" 
  "output_format": "png",      // Optional. "png" or "jpeg" (default: "png")
  "output_compression": 90     // Optional. JPEG quality 0-100 (default: 100)
}
```

### Embedded Parameters (Advanced)
The server supports a special XML embedding system within the prompt:

```
Your normal prompt here <sd_cpp_extra_args>{"steps": 30, "cfg_scale": 7.5, "seed": 123}</sd_cpp_extra_args>
```

**How it works:**
1. Server extracts JSON from `<sd_cpp_extra_args>` tags using regex
2. Removes the tags from the actual prompt sent to AI model  
3. Parses extracted JSON and applies to `SDGenerationParams`
4. This allows advanced parameter control without changing API structure

### Server Processing Logic
```cpp
// Extract embedded parameters from prompt
std::string sd_cpp_extra_args_str = extract_and_remove_sd_cpp_extra_args(prompt);

// Apply to generation parameters
if (!sd_cpp_extra_args_str.empty() && !gen_params.from_json_str(sd_cpp_extra_args_str)) {
    // Return error if invalid JSON
}
```

### Parameter Constraints
- `n` (batch count): Clamped to 1-8 range for safety
- `size`: Parsed as "WIDTHxHEIGHT", defaults to 512x512 if invalid
- `output_compression`: Clamped to 0-100 range
- Empty `prompt` returns 400 error

## 📤 Response Format

### Successful Response (200)
```json
{
  "created": "2025-12-31T18:48:19Z",    // ISO timestamp when generation started
  "data": [                             // Array of generated images
    {
      "b64_json": "iVBORw0KGgoAAAA..."   // Base64 encoded image data
    }
  ],
  "output_format": "png"                // Echo of requested format
}
```

### Error Responses (400/500)
```json
// 400 - Bad Request
{"error": "prompt required"}
{"error": "invalid output_format, must be one of [png, jpeg]"}
{"error": "invalid sd_cpp_extra_args"}
{"error": "invalid params"}

// 500 - Server Error  
{
  "error": "server_error",
  "message": "specific error details"
}
```

## � UI Configuration Strategy

### Basic Controls (Always Visible)
```javascript
// Image Size Options (radio buttons or dropdown)
const BASIC_SIZES = {
  "256x256": "Small Square",
  "512x512": "Medium Square (Default)", 
  "1024x512": "Wide",
  "512x1024": "Tall",
  "1024x1024": "Large Square"
};

// Quality Presets (radio buttons)  
const QUALITY_PRESETS = {
  "low": { steps: 4, label: "Low (Fast)", default: true },
  "medium": { steps: 10, label: "Medium" },
  "high": { steps: 20, label: "High (Best)" }
};
```

### Advanced Parameters (Collapsed by Default)
```javascript
// Advanced parameters - NO defaults, only sent when user specifies
// UI should show empty/placeholder values, collapsed until clicked
const ADVANCED_PARAMS = {
  cfg_scale: null,       // Guidance scale (server default used if not specified)
  seed: null,            // Random seed (server random if not specified) 
  negative_prompt: "",   // Things to avoid (empty = not sent)
  clip_skip: null,       // CLIP layers to skip (server default if not specified)
  batch_count: null      // Override n parameter (server default if not specified)
};
```

## 🎛️ Full Parameter Reference (via XML embedding)

Based on server code structure, these parameters are supported in the embedded JSON:

### Basic Generation Control
- `steps`: Number of inference steps (4=Low, 10=Medium, 20=High)
- `cfg_scale`: Classifier-free guidance scale 
- `seed`: Random seed for reproducible results 
- `negative_prompt`: Text to avoid in generation

### Image Control  
- `width`: Image width (overrides size parameter)
- `height`: Image height (overrides size parameter)  
- `strength`: Denoising strength for img2img
- `batch_count`: Number of images (overrides n parameter)

### Advanced Features
- `clip_skip`: CLIP layers to skip 
- `lora_vec`: LoRA model parameters
- `control_strength`: ControlNet strength
- Various specialized parameters for controlnet, inpainting, etc.

**Note**: Exact parameter names and supported values would need testing or deeper code analysis of the `SDGenerationParams` structure.

## 🔧 Implementation Strategy

### For Web App Integration:

1. **Basic Mode**: Default user-friendly interface
   ```javascript
   // Simple form with size and quality presets
   {
     "prompt": userPrompt,
     "size": selectedSize || "512x512",  // Default to medium square
     "n": 1
   }
   
   // For Low/Medium/High quality, embed steps
   const qualitySteps = { low: 4, medium: 10, high: 20 };
   const advancedPrompt = `${userPrompt} <sd_cpp_extra_args>{"steps": ${qualitySteps[quality]}}</sd_cpp_extra_args>`;
   ```

2. **Advanced Mode**: Optional parameter control (collapsed by default)
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

3. **Parameter Extraction**: Parse and store used settings
   ```javascript
   // Extract used parameters from sent prompt for database
   const extractedParams = parseEmbeddedParams(sentPrompt);
   const cleanPrompt = removeEmbeddedTags(sentPrompt);
   ```

### Database Schema Updates
```json
{
  "filename": "image.png",
  "prompt": "clean user prompt (XML tags removed)",
  "model": "z_image_turbo", 
  "size": "512x512",  // One of: 256x256, 512x512, 1024x512, 512x1024, 1024x1024
  "quality": "low",   // One of: low (4 steps), medium (10 steps), high (20 steps)
  "generation_timestamp": "2025-12-31T18:48:19Z", // From server response
  "parameters": {
    "steps": 4,              // Always present: 4=Low, 10=Medium, 20=High
    "cfg_scale": null,       // Only present if user specified (null = server default used)
    "seed": null,            // Only present if user specified (null = server random used)
    "negative_prompt": null, // Only present if user specified (null = none used)
    "clip_skip": null,       // Only present if user specified (null = server default used)
    "method": "Euler"        // Server default (always fixed)
  }
}
```

## 🚨 Important Discoveries

1. **Fixed Server Parameters**: Some parameters are compiled into server (Euler method, default steps)
2. **Parameter Validation**: Server validates and clamps all parameters for safety
3. **Embedded System**: The XML tag approach is the ONLY way to send advanced parameters
4. **Response Metadata**: Server provides timestamp and echoes format, but not generation parameters
5. **Batch Limit**: Maximum 8 images per request (safety constraint)

## 🎯 Recommended Implementation Order

1. **Phase 2.1**: Update UI with basic controls
   - Size selector: 256x256, 512x512 (default), 1024x512, 512x1024, 1024x1024  
   - Quality presets: Low (4 steps, default), Medium (10 steps), High (20 steps)
   - Collapsible advanced section (collapsed by default, no preset values)

2. **Phase 2.2**: Implement embedded parameter system
   - Build XML embedding for quality presets (always) and advanced parameters (only when specified)
   - Parse and clean prompts for database storage
   - Handle parameter extraction and validation (store null for unspecified advanced params)

3. **Phase 2.3**: Update response parsing and database
   - Extract server timestamp from response
   - Store size, quality preset, and actual parameters used
   - Update gallery to show generation details

4. **Phase 2.4**: Enhanced gallery features
   - Filter by size and quality settings
   - Display comprehensive generation parameters
   - Parameter copying for reuse

This approach provides immediate value with simple controls while enabling full server capabilities for advanced users.
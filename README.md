# atelier-client-d3
A fast translation layer for D3-based AI image generation.

## Features
- Automated authentication and session management
- Headless browser operation for efficient processing
- Support for both legacy (v1) and new (v2) image generation interfaces
- Automatic image format conversion (WebP/JPG)
- Configurable output directory and logging
- Handles explicit content filtering
- Unique task ID tracking for each request

## Installation
Install via pip:
```bash
pip install atelier-d3-client
```

## Usage

```python
from atelier_d3_client import AtelierD3Client

client = AtelierD3Client()
```

Initialize the client
```python
client = AtelierD3Client(
    log_on=True, # Enable logging (default: True)
    log_to=None, # Custom log directory (default: None)
    save_to="outputs", # Output directory (default: "outputs")
    save_as="webp" # Output format: "webp" or "jpg" (default: "webp")
)
```

Generate images
```python
images = client.generate_image("a cute cat playing with yarn")
print(f"Generated images saved at: {images}")
```


## Configuration Options

### Logging
- `log`: Enable/disable logging (boolean)
- `log_dir`: Specify custom log directory (string path)

### Output Settings
- `save_to`: Directory where generated images will be saved
- `save_as`: Image format for saving ("webp" or "jpg")
  - WebP offers better compression while maintaining quality
  - JPG is used as fallback if WebP conversion fails

### Output Structure
Images are saved with the following naming convention:
```
{save_to}/{YYYY-MM-DD}/{task_id}_{index}.{format}
```

## Error Handling
The client includes comprehensive error handling for:
- Authentication failures
- Network issues
- Content filtering
- Image processing errors
- Browser automation issues


Each operation is logged (when logging is enabled) and raises appropriate exceptions with detailed error messages.

## Requirements
- Python 3.8+
- Internet connection

## Notes
- The client automatically manages ChromeDriver installation and updates
- Operates in headless mode for improved performance
- Handles both single and multi-image generation requests

## License
See [LICENSE](LICENSE) for more details.
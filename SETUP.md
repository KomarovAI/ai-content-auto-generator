# 🚀 Setup Guide

## Prerequisites

- Python 3.11 or higher
- Git
- (Optional) Redis for caching
- (Optional) Docker & Docker Compose

## Installation Methods

### Method 1: Local Setup

#### 1. Clone Repository

```bash
git clone https://github.com/KomarovAI/ai-content-auto-generator.git
cd ai-content-auto-generator
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure API Keys

```bash
# Copy example config
cp config.yaml.example config.yaml

# Or use environment variables
cp .env.example .env
```

Edit `config.yaml` or `.env` and add your API keys:

```yaml
api_keys:
  openai: "sk-..."
  gemini: "AI..."
  anthropic: "sk-ant-..."
  stability: "sk-..."
```

#### 5. Run Tests

```bash
pytest tests/ -v
```

#### 6. Run Generator

```bash
python scripts/main.py
```

### Method 2: Docker Setup

#### 1. Using Docker Compose

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f generator

# Stop services
docker-compose down
```

#### 2. Using Plain Docker

```bash
# Build image
docker build -t ai-content-generator .

# Run container
docker run -d \
  --name generator \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/logs:/app/logs \
  ai-content-generator
```

## Configuration

### API Keys Setup

#### OpenAI (GPT & DALL-E)
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to config: `openai: "sk-..."`

#### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Add to config: `gemini: "AI..."`

#### Anthropic (Claude)
1. Go to https://console.anthropic.com/
2. Create API key
3. Add to config: `anthropic: "sk-ant-..."`

#### Stability AI
1. Go to https://platform.stability.ai/
2. Get API key
3. Add to config: `stability: "sk-..."`

### GitHub Actions Setup

For automatic deployment:

1. Go to your repo: Settings → Secrets and variables → Actions
2. Add secrets:
   - `OPENAI_API_KEY`
   - `GEMINI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `STABILITY_API_KEY`

## Usage Examples

### Basic Text Generation

```python
from scripts.main import ContentGenerator
import asyncio

generator = ContentGenerator()

# Generate single text
text = asyncio.run(generator.generate_text(
    "Write compelling restaurant description"
))

print(text)
```

### Batch Generation

```python
# Generate content for multiple pages
results = asyncio.run(generator.generate_batch(
    pages=["index.html", "about.html", "services.html"],
    mode="parallel"
))

for page, content in results.items():
    print(f"{page}: {content}")
```

### Image Generation

```python
# Generate multiple images
images = asyncio.run(generator.generate_images([
    "modern restaurant interior",
    "professional team photo"
], style="photorealistic"))

for img_url in images:
    print(f"Generated: {img_url}")
```

### Enable A/B Testing

```python
# Create A/B test
generator.create_ab_test(
    page="landing.html",
    variants=3,
    metric="conversion_rate"
)
```

### Enable Auto-Optimization

```python
# Enable self-learning
generator.enable_optimization(
    metrics=["time_on_page", "bounce_rate"],
    optimization_interval="daily"
)
```

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Redis Connection Error

If using Redis cache:

```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis  # macOS

# Start Redis
redis-server
```

Or switch to memory cache in `config.yaml`:

```yaml
cache:
  backend: "memory"
```

### API Rate Limits

If hitting rate limits:

1. Check usage: see `logs/generator.log`
2. Adjust limits in `config.yaml`
3. Enable caching to reduce API calls
4. Use `cost_optimized` distribution mode

## Performance Tips

1. **Enable Caching**: Reduces API calls by 40-60%
2. **Use Parallel Mode**: For batch generation
3. **Cost-Optimized Strategy**: Use cheaper APIs first
4. **Redis Cache**: Faster than memory for large datasets

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Check [README.md](README.md) for feature overview
- See `templates/` for prompt examples
- Review `tests/` for usage patterns
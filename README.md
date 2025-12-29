# 🤖 AI Content Auto-Generator

> Distributed AI content generation system with multi-API orchestration, smart limits management, A/B testing, and self-optimization for massive website deployment

## 🎯 Main Features

- **Multi-API Orchestration** - Distributed requests across multiple AI services (OpenAI, Google Gemini, Stable Diffusion, etc.)
- **Smart Limits Management** - Automatic tracking and rotation of API quotas
- **A/B Testing** - Automated content variants testing with analytics
- **Self-Optimization** - ML-driven content improvement based on user metrics
- **GitHub Actions Integration** - Full CI/CD automation
- **Semantic Caching** - Reuse similar generations to save API calls
- **Fallback Strategies** - Cascading backup systems for high availability
- **Real-time Dashboard** - Live monitoring of generation metrics

## 📋 Supported APIs

### Text Generation
- OpenAI GPT-4/GPT-3.5
- Google Gemini Flash/Pro
- Anthropic Claude
- Mistral AI

### Image Generation
- Google Imagen 3 (unlimited daily generations)
- OpenAI DALL-E 3 (50 images/month)
- Adobe Firefly (25 generations/day)
- Stability AI
- Microsoft Copilot Designer
- Recraft V3
- Canva AI

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/KomarovAI/ai-content-auto-generator.git
cd ai-content-auto-generator
pip install -r requirements.txt
```

### Configuration

1. Copy `config.yaml.example` to `config.yaml`
2. Add your API keys:

```yaml
api_keys:
  openai: "your-openai-key"
  gemini: "your-gemini-key"
  stability: "your-stability-key"
  # ... other keys
```

### Basic Usage

```python
from main import ContentGenerator

generator = ContentGenerator(config_path="config.yaml")

# Generate text for multiple pages
results = generator.generate_batch(
    pages=["index.html", "about.html", "services.html"],
    mode="auto"  # automatically distributes across APIs
)

# Generate images with fallback
images = generator.generate_images(
    prompts=["modern restaurant interior", "professional team photo"],
    style="photorealistic"
)
```

## 📁 Project Structure

```
ai-content-auto-generator/
├── README.md
├── requirements.txt
├── config.yaml
├── .gitignore
├── scripts/
│   ├── main.py                 # Main orchestrator
│   ├── api_manager.py          # API limits & rotation
│   ├── text_generator.py       # Text generation logic
│   ├── image_generator.py      # Image generation logic
│   ├── cache_manager.py        # Semantic caching
│   ├── analytics.py            # A/B testing & metrics
│   ├── optimizer.py            # Self-optimization engine
│   └── logger.py               # Logging system
├── templates/
│   ├── prompts.json            # Prompt library
│   └── page_config.json        # Page configurations
├── .github/
│   └── workflows/
│       └── auto_deploy.yml     # GitHub Actions workflow
└── tests/
    └── test_api_manager.py
```

## 🔧 Advanced Features

### Semantic Caching

Reduce API calls by reusing similar generations:

```python
generator.enable_cache(similarity_threshold=0.85)
```

### A/B Testing

Automatically test multiple content variants:

```python
generator.create_ab_test(
    page="landing.html",
    variants=3,
    metric="conversion_rate"
)
```

### Auto-Optimization

Enable self-learning based on user metrics:

```python
generator.enable_optimization(
    metrics=["time_on_page", "bounce_rate", "conversions"],
    optimization_interval="daily"
)
```

## 🤖 GitHub Actions Automation

The workflow automatically:
1. Triggers on push to `main` branch
2. Generates content for modified pages
3. Optimizes images and text
4. Runs A/B tests
5. Deploys to production

## 📊 Monitoring Dashboard

Access real-time metrics at `http://localhost:8080/dashboard`:
- API limits status
- Generation speed
- Cost tracking
- Quality metrics
- Error rates

## 🛡️ Fallback Strategy

```
Primary API → Secondary API → Cached Content → Template Fallback
```

Ensures 99.9% uptime even when APIs are unavailable.

## 📝 License

MIT License - feel free to use for commercial projects

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

## 📧 Contact

Created by [@KomarovAI](https://github.com/KomarovAI)

---

**⚡ Built with love for scaling content generation to 50+ websites**
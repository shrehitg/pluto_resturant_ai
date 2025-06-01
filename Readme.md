# 🪐 Pluto Restaurant AI

**AI Phone Agent for Restaurants** - Powered by OpenAI Realtime API & Twilio

Transform your restaurant's phone system with an intelligent AI assistant that handles reservations, takes orders, and provides exceptional customer service 24/7.

---

## 📋 Table of Contents

- [Features](#-features)
- [Demo](#-demo)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)

---

## ✨ Features

### 🎯 **24/7 Availability**
Never miss a call again. Pluto handles customer inquiries around the clock, ensuring consistent service even during busy periods or after hours.

### 🧠 **Smart Customer Insights**
Our AI remembers every customer's preferences, usual orders, and dining history. Send targeted promos via text, offer personalized recommendations, and create VIP experiences for your regulars automatically.

### 🍽️ **Restaurant Expertise**
Specialized AI trained on restaurant operations, menu knowledge, reservation systems, and customer service best practices.

### 📈 **Business Intelligence**
Get detailed reports on call volume, peak hours, popular menu items, and conversion rates. Track performance metrics and optimize your operations with comprehensive dashboards and real-time analytics.

---

## 🎮 Demo

**Try it live:** Call **(415) 449-7391** to experience Pluto in action!

> 🏮 **Featured Restaurant:** Shizen - A fully vegan sushi bar and izakaya in San Francisco
> 
> Our AI assistant "Pluto" handles:
> - **Reservations** - Complete booking system with availability checking
> - **Menu Information** - Detailed knowledge of vegan sushi offerings
> - **Customer Service** - Hours, policies, and general inquiries
> - **Order Taking** - To-go orders and special requests

---

## 🛠 Tech Stack

- **Backend:** FastAPI (Python)
- **AI:** OpenAI Realtime API (gpt-4o-realtime-preview)
- **Telephony:** Twilio Voice & Media Streams
- **Audio:** Real-time WebSocket streaming with G.711 μ-law
- **Deployment:** Railway (with Docker support)
- **Frontend:** Modern responsive website with custom logo integration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key
- Twilio account with phone number
- ngrok (for local development)

### 1. Clone & Install

```bash
git clone https://github.com/shrehitg/pluto_resturant_ai.git
cd pluto_restaurant_ai
pip3 install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=5050
```

### 3. Run Locally

```bash
# Start the server
python3 main.py

# In another terminal, expose via ngrok
ngrok http 5050
```

### 4. Configure Twilio

1. Set your Twilio webhook URL to: `https://your-ngrok-url.com/incoming-call`
2. Configure media streams to: `wss://your-ngrok-url.com/media-stream`

### 5. Test Your AI

- **Website:** Visit `http://localhost:5050`
- **Phone:** Call your Twilio number
- **Health Check:** `GET /test-twiml`

---

## 🌐 Deployment

### Railway (Recommended)

1. **Connect Repository:**
   - Go to [Railway](https://railway.app)
   - Connect your GitHub account
   - Select `pluto_resturant_ai` repository

2. **Environment Variables:**
   ```
   OPENAI_API_KEY=your_key_here
   PORT=5050
   ```

3. **Custom Domain:**
   - Add your domain in Railway dashboard
   - Update Twilio webhooks to your domain

### Alternative Platforms

- **Render:** Auto-deploys from GitHub
- **Heroku:** Use included `Procfile`
- **DigitalOcean Apps:** Container-ready
- **AWS/GCP:** Docker deployment

---

## ⚙️ Configuration

### Restaurant Customization

Edit the `SYSTEM_MESSAGE` in `main.py` to customize:

- **Restaurant Details:** Name, address, phone, hours
- **Menu Information:** Dishes, ingredients, specialties
- **Policies:** Reservations, cancellations, to-go orders
- **Brand Voice:** Personality, greeting, philosophy

### AI Voice Settings

```python
# Voice options: alloy, echo, fable, onyx, nova, shimmer, sage
"voice": "sage",

# Model selection
MODEL = "gpt-4o-realtime-preview"

# Temperature (creativity level)
"temperature": 0.8
```

### Website Branding

Customize in the HTML template:
- **Colors:** Update CSS variables for brand colors
- **Logo:** Replace `logo.png` with your restaurant logo
- **Content:** Modify features, contact info, and demo number

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page with demo |
| `/incoming-call` | GET/POST | Twilio webhook for calls |
| `/media-stream` | WebSocket | Real-time audio streaming |
| `/test-twiml` | GET | TwiML testing endpoint |
| `/logo.png` | GET | Serves restaurant logo |

---

## 📊 Call Analytics

Track important metrics:

- **Call Volume:** Daily, weekly, monthly trends
- **Peak Hours:** Optimize staffing schedules
- **Popular Inquiries:** Menu items, reservation requests
- **Customer Satisfaction:** Call duration and completion rates
- **Conversion Tracking:** Calls that result in reservations/orders

---

## 🎨 Customization Examples

### Change Restaurant Theme

```python
# Update system message for Italian restaurant
SYSTEM_MESSAGE = """
You are Marco, a friendly host at Bella Vista Italian Restaurant...
Our specialties include handmade pasta, wood-fired pizza...
"""
```

### Modify Voice Personality

```python
# Professional and formal
"temperature": 0.3,
"instructions": "Be professional and courteous..."

# Warm and casual
"temperature": 0.8,
"instructions": "Be warm, friendly, and conversational..."
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add tests for new features
- Update documentation for any API changes
- Test thoroughly with different restaurant scenarios

---

## 📞 Support

- **Email:** [hello@getplutoai.net](mailto:hello@getplutoai.net)
- **Phone:** (608) 886-1118
- **Issues:** [GitHub Issues](https://github.com/shrehitg/pluto_resturant_ai/issues)
- **Demo:** Call (415) 449-7391

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- **OpenAI** for the incredible Realtime API
- **Twilio** for robust telephony infrastructure
- **Shizen Restaurant** for being our featured demo partner
- **Railway** for seamless deployment platform

---

<div align="center">

**Built with ❤️ for the restaurant industry**

[🌐 Visit Pluto](https://getpluto.ai) | [📞 Try Demo](tel:+14154497391) | [⭐ Star on GitHub](https://github.com/shrehitg/pluto_resturant_ai)

</div>

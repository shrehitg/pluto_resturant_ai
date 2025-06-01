import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv
from websockets.connection import State

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = (
    "CRITICAL: NEVER ACCEPT RESERVATIONS FOR PAST DATES OR TIMES. Always check if the requested date/time has already occurred before proceeding.\n\n"

    "CRITICAL: If there is silence for 3-4 seconds and the customer hasn't specifically asked to hold or wait, "
    "proactively ask a follow-up question or offer additional help. Examples: 'Is there anything else I can "
    "help you with?', 'Would you like to hear about our popular dishes?', 'Are you ready to make a reservation?' "
    "This keeps the conversation flowing and shows attentive customer service.\n\n"
    
    "You are a Pluto, a friendly and knowledgeable server at Shizen, a fully vegan sushi bar and izakaya located at "
    "370 14th Street, San Francisco, CA 94103. You're answering customer calls to take orders, manage reservations, "
    "and answer questions about our restaurant. Phone: (415) 678-5767.\n\n"
    
    "RESTAURANT PHILOSOPHY & CONCEPT:\n"
    "Shizen is proud to be a fully vegan sushi bar and izakaya. We combine classic shojin and sushi techniques "
    "with local, seasonal ingredients to create healthy and flavorful dishes with a light footprint. We believe "
    "that the components of honest plant-based cuisine should speak for themselves. Our chefs use tapioca, "
    "mountain yam, konjac, bean curd, and other vegan ingredients to form complex and satisfying dishes that "
    "stand on their own without the need to imitate animal proteins.\n\n"
    
    "HOURS OF OPERATION:\n"
    "Monday-Thursday: 5:00pm to 9:00pm\n"
    "Friday-Saturday: 4:00pm to 9:30pm\n"
    "Sunday: 4:30pm to 9:00pm\n"
    "We will be closed December 24th through 26th.\n\n"
    
    "RESERVATION POLICIES:\n"
    "- Reservations are REQUIRED for the dining room; maximum party size is four people\n"
    "- Limited walk-in service available for the sushi bar; maximum party size of three\n"
    "- Dining room reservations can be made up to one week in advance\n"
    "- 90-minute seating time to accommodate other guests\n"
    "- We can only hold unclaimed tables for 15 minutes beyond the reserved time\n"
    "- Cancellations made with less than 24-hour notice may be subject to a $20/person cancellation fee\n"
    "- To-go orders are available for pickup\n\n"
    
    "COMPLETE MENU:\n\n"
    
    "APPETIZERS & SMALL PLATES:\n"
    "- Gyoza (6 pieces): $9 - Traditional vegan dumplings with crispy exterior and savory filling\n"
    "- Miso Soup: $6 - Classic Japanese soup with tofu and wakame seaweed\n"
    "- Tempura: $12 - Light, crispy vegetable tempura served with katsu sauce\n"
    "- Bean Curd Katsu: $14 - Crispy fried tofu cutlet with perfect texture and seasoning (highly recommended)\n"
    "- Shizen Poke: $16 - Vegan poke bowl with marinated vegetables and rice\n"
    "- Edamame: $7 - Steamed soybeans with sea salt\n"
    "- Garlic Edamame: $8 - Steamed soybeans with garlic and spices\n"
    "- Agedashi Tofu: $10 - Lightly fried tofu in savory dashi broth\n"
    "- Brussels Sprouts: $11 - Crispy Brussels sprouts served on sizzling plate\n"
    "- Mushroom Trio: $13 - Grilled eryngii, shiitake, and enoki mushrooms with tare sauce\n"
    "- Croquettes: $10 - Crispy vegetable and tofu croquettes\n\n"
    
    "RAMEN (Three varieties available):\n"
    "- Shio Ramen: $15 - Light and subtle broth with fresh noodles made in-house daily, bamboo shoots, and soy-based egg substitute\n"
    "- Shoyu Ramen: $15 - Earthy and intricate soy-based broth with complex umami flavors\n"
    "- Spicy Miso Garlic Ramen: $16 - Spicy and striking with rich miso base and garlic notes\n"
    "All ramen features fresh noodles made daily in-house and traditional toppings\n\n"
    
    "MAIN DISHES:\n"
    "- Lily Flower Curry: $18 - Japanese-style apple curry with sweet and savory flavors, served with rice\n"
    "- Chirashi Bowl: $22 - Assorted vegan sashimi over sushi rice\n"
    "- Donburi: $16 - Rice bowl with seasonal vegetables and protein\n\n"
    
    "NIGIRI (Individual pieces, $8 for 2 pieces):\n"
    "- Tomato Nigiri: $8 (2 pieces) - Shoyu and kombu-marinated tomato that resembles tuna\n"
    "- Eggplant Nigiri: $8 (2 pieces) - Grilled eggplant with traditional preparation\n"
    "- Avocado Nigiri: $8 (2 pieces) - Fresh avocado with sushi rice\n"
    "- Mushroom Nigiri: $8 (2 pieces) - Seasonal mushroom varieties\n"
    "- Inari: $8 (2 pieces) - Sweet seasoned tofu pockets\n"
    "- Mango Nigiri: $8 (2 pieces) - Fresh mango with sushi rice\n"
    "- Okra Nigiri: $8 (2 pieces) - Grilled okra with special preparation\n\n"
    
    "CLASSIC SUSHI ROLLS:\n"
    "- Avocado Roll: $8 - Simple and fresh avocado\n"
    "- Kappa Maki (Cucumber Roll): $7 - Traditional cucumber roll\n"
    "- California Roll: $10 - Vegan version with avocado and vegetables\n"
    "- Philadelphia Roll: $11 - Vegan cream cheese and vegetables\n"
    "- Spicy Tofuna Roll: $12 - Spicy marinated tofu that mimics tuna\n"
    "- Sweet Potato Tempura Roll: $10 - Crispy sweet potato tempura\n\n"
    
    "SPECIALTY SUSHI ROLLS (Our signature creations):\n"
    "- Body and Soul Roll: $16 - Spicy, crunchy with tempura coating and flavorful toppings (customer favorite)\n"
    "- Hidden Agenda Roll: $15 - Tempura eggplant, bell pepper, carrot, zucchini, onion, and fried garlic (second most popular)\n"
    "- Open Invitation Roll: $17 - Creative seasonal ingredients\n"
    "- Candlestick Roll: $18 - Dramatic presentation that lights up with fire during indoor dining\n"
    "- Secret Weapon Roll: $16 - Chef's special creation with habanero heat and marinated eryngii mushroom\n"
    "- Second Act Roll: $15 - Unique flavor combination\n"
    "- Surprise Ending Roll: $18 - Visually stunning roll served with sake or non-alcoholic shot\n"
    "- Prime Suspect Roll: $17 - Tempura asparagus and sweet potato with gochujang aioli\n"
    "- Colonel's Pipe Roll: $16 - Features beets and unique flavor profile\n"
    "- Proud Peacock Roll: $17 - Colorful and creative presentation\n"
    "- Plot Twist Roll: $15 - Unexpected flavor combinations\n"
    "- Scarlet Smile Roll: $16 - Vibrant and flavorful specialty roll\n\n"
    
    "BEVERAGES:\n"
    "- Sake (by glass): $8-12 - Curated selection of premium sake\n"
    "- Sake (by bottle): $35-65 - Premium sake selections\n"
    "- Natural Wine (by glass): $10-14 - Organic and biodynamic wine pairings\n"
    "- Japanese Beer: $6-8 - Asahi, Sapporo, and craft options\n"
    "- Specialty Cocktails: $12-15 - Creative cocktails with Japanese influences\n"
    "- Ginger Lemonade: $5 - House-made specialty drink\n"
    "- Passionfruit Ginger Sparkling: $6 - Refreshing sparkling drink\n"
    "- Tea (pot): $4-6 - Traditional Japanese teas including matcha\n"
    "- Non-alcoholic options: $3-5 - Sparkling water, sodas, fresh juices\n\n"
    
    "DESSERTS (Rotating selection):\n"
    "- Matcha Ice Cream: $8 - House-made green tea ice cream\n"
    "- Vegan Brownie: $9 - Rich chocolate brownie\n"
    "- Mochi Donut Holes: $10 - With strawberry ice cream and matcha powder\n"
    "- Guava Cheesecake: $11 - Seasonal vegan cheesecake\n"
    "- Seasonal Desserts: $8-12 - Chef's special creations that change weekly\n\n"
    
    "DIETARY ACCOMMODATIONS:\n"
    "- All dishes are 100% vegan (no animal products)\n"
    "- Gluten-free options available (ask about specific items)\n"
    "- Nut-free preparations can be accommodated\n"
    "- Soy-free options limited but available\n\n"
    
    "PRICING NOTES:\n"
    "- Generally more affordable than traditional sushi restaurants\n"
    "- Specialty rolls: $15-18 (most popular: Body and Soul $16, Hidden Agenda $15)\n"
    "- Classic rolls: $7-12 (simple options like Kappa Maki $7, Avocado Roll $8)\n"
    "- Ramen bowls: $15-16 (Shio and Shoyu $15, Spicy Miso Garlic $16)\n"
    "- Appetizers: $6-16 (Miso Soup $6, Shizen Poke $16)\n"
    "- Nigiri: $8 for 2 pieces (all varieties same price)\n"
    "- Main dishes: $16-22 (Donburi $16, Chirashi Bowl $22)\n"
    "- Beverages: $3-15 (Non-alcoholic $3-6, Cocktails $12-15, Sake by glass $8-12)\n"
    "- Desserts: $8-12 (Matcha Ice Cream $8, Guava Cheesecake $11)\n\n"
    
    "CUSTOMER SERVICE APPROACH:\n"
    "MULTILINGUAL SUPPORT: Detect the language the customer is speaking and respond in that same language throughout the entire conversation. "
    "If a customer speaks Spanish, respond in Spanish. If they speak French, respond in French. If they speak Mandarin, respond in Mandarin. "
    "Maintain the same warm, helpful tone and restaurant knowledge regardless of language. "
    "ALWAYS SPEAK FAST - maintain a quick, efficient pace throughout conversations. "
    "Be warm, helpful, and enthusiastic about our plant-based cuisine. Explain our vegan approach with pride, "
    "emphasizing how our dishes are crafted to be satisfying and flavorful on their own merit. Help customers "
    "understand our reservation system, suggest menu items based on their preferences, and always mention our "
    "philosophy: 'May all beings everywhere be happy and free.' Keep responses SHORT and CONCISE - aim for "
    "1-2 sentences maximum. Be direct and to the point while remaining friendly. Always offer to help with "
    "reservations or answer any questions about our unique vegan sushi experience. "
    "AFTER completing any task, answering questions, or providing information, ALWAYS ask 'Is there anything else I can help you with?' "
    "or similar follow-up questions to keep the conversation going and provide excellent customer service.\n\n"
    
    "HANDLING OFF-TOPIC QUESTIONS:\n"
    "Answer questions that are remotely related to the restaurant experience (nearby parking, attractions, neighborhood info, "
    "directions to Shizen, etc.) and obvious common knowledge questions anyone would know (color of sky, basic facts). "
    "For nearby amenities, provide specific addresses when possible: "
    "For complex unrelated topics (sports scores, politics, technical support, personal advice), "
    "politely respond: 'I don't know about that, but I can help with Shizen questions - menu, reservations, or orders.'\n\n"
    
    "REALISTIC RESERVATION HANDLING:\n"
    "- REMEMBER reservation details (date, time, party size) throughout the entire conversation - do NOT ask for the same information again\n"
    "- If a customer mentions a date and time, keep that information and use it for the rest of the conversation\n"
    "- ABSOLUTELY REFUSE reservations for any past dates or times that have already occurred no matter how many times the customer asks\n"
    "- If today is January 15th and someone asks for January 14th, say 'I cannot make reservations for past dates'\n"
    "- If it's currently 6pm and someone asks for 5pm today, say 'That time has already passed'\n"
    "- ONLY accept reservations during operating hours: Mon-Thu 5-9pm, Fri-Sat 4-9:30pm, Sun 4:30-9pm\n"
    "- STRICTLY enforce maximum party size: 4 people dining room, 3 people sushi bar walk-ins\n"
    "- NEVER make reservations more than one week in advance\n"
    "- ALWAYS ask for and collect the customer's name for all reservations and pickup orders\n"
    "- For reservations: 'Can I get a name for the reservation?' or 'What name should I put this under?'\n"
    "- For pickup orders: 'What name should I put this order under?' or 'Can I get a name for pickup?'\n"
    "- ALWAYS confirm: 'Let me confirm - that's [DATE] at [TIME] for [NUMBER] people under the name [NAME]'\n"
    "- For pickup orders confirm: 'So that's [ORDER DETAILS] for pickup under the name [NAME]'\n"
    "- For pickup orders, ALWAYS calculate and mention the order total: 'Your total comes to $[AMOUNT]'\n"
    "- Remind customers: 'We have a 90-minute seating time and 15-minute grace period'\n"
    "- CRITICAL: Check if the requested date/time makes logical sense before accepting ANY reservation"
)
VOICE = 'sage'
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

app = FastAPI()

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

# Serve the logo image
@app.get("/logo.png")
async def get_logo():
    return FileResponse("logo.png", media_type="image/png")

@app.get("/", response_class=HTMLResponse)
async def index_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pluto - AI Phone Agent for Restaurants</title>
        <link rel="icon" type="image/png" href="/logo.png">
        <style>
            /* Accent & neutrals */
            :root {
                --gold-accent: #f1c40f;
                --bg-light: #f5f6fa;
                --text-dark: #2e2e3d;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--text-dark);
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }
            
            header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 1rem 0;
                position: fixed;
                width: 100%;
                top: 0;
                z-index: 1000;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            }
            
            nav {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .logo {
                font-size: 1.8rem;
                font-weight: bold;
                color: #667eea;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .logo-icon {
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .logo-icon img {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }
            
            .nav-links {
                display: flex;
                list-style: none;
                gap: 2rem;
            }
            
            .nav-links a {
                text-decoration: none;
                color: var(--text-dark);
                font-weight: 500;
                transition: color 0.3s;
            }
            
            .nav-links a:hover {
                color: #667eea;
            }
            
            .hero {
                min-height: 100vh;
                display: flex;
                align-items: center;
                text-align: center;
                color: white;
                padding-top: 80px;
            }
            
            .hero-content h1 {
                font-size: 3.5rem;
                margin-bottom: 1rem;
                animation: fadeInUp 1s ease;
            }
            
            .hero-content p {
                font-size: 1.3rem;
                margin-bottom: 2rem;
                opacity: 0.9;
                animation: fadeInUp 1s ease 0.2s both;
            }
            
            .cta-button {
                display: inline-block;
                background: var(--gold-accent);
                color: white;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s;
                animation: fadeInUp 1s ease 0.4s both;
            }
            
            .cta-button:hover {
                background: #d4ac0d;
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(241, 196, 15, 0.3);
            }
            
            .features {
                background: var(--bg-light);
                padding: 80px 0;
            }
            
            .features h2 {
                text-align: center;
                font-size: 2.5rem;
                margin-bottom: 3rem;
                color: var(--text-dark);
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-top: 2rem;
            }
            
            .feature-card {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .feature-card h3 {
                font-size: 1.5rem;
                margin-bottom: 1rem;
                color: var(--text-dark);
            }
            
            .feature-card p {
                color: var(--text-dark);
            }
            
            .demo {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 80px 0;
                text-align: center;
            }
            
            .demo h2 {
                font-size: 2.5rem;
                margin-bottom: 2rem;
            }
            
            .demo-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 2rem;
                margin: 2rem auto;
                max-width: 600px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .phone-number {
                font-size: 2rem;
                font-weight: bold;
                color: var(--gold-accent);
                margin: 1rem 0;
            }
            
            .footer {
                background: var(--text-dark);
                color: white;
                text-align: center;
                padding: 2rem 0;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            @media (max-width: 768px) {
                .hero-content h1 {
                    font-size: 2.5rem;
                }
                
                .nav-links {
                    display: none;
                }
                
                .features-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <nav class="container">
                <div class="logo">
                    <div class="logo-icon">
                        <img src="/logo.png" alt="Pluto Logo">
                    </div>
                    <span>Pluto</span>
                </div>
                <ul class="nav-links">
                    <li><a href="#home">Home</a></li>
                    <li><a href="#features">Features</a></li>
                    <li><a href="#demo">Demo</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>

        <section id="home" class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1>AI Phone Agent for Restaurants</h1>
                    <p>Transform your restaurant's phone experience with intelligent AI assistants that handle reservations, orders, and customer inquiries 24/7</p>
                    <a href="#demo" class="cta-button">Try Our Demo</a>
                </div>
            </div>
        </section>

        <section id="features" class="features">
            <div class="container">
                <h2>Why Choose Pluto?</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">📞</div>
                        <h3>24/7 Availability</h3>
                        <p>Never miss a revenue opportunity. Our AI captures every order and reservation call, even during peak hours and after closing time.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🍽️</div>
                        <h3>Restaurant Expertise</h3>
                        <p>Trained specifically for restaurants, our AI understands menus, dietary restrictions, reservations, and food service operations.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Smart Customer Insights</h3>
                        <p>Boost revenue with AI that remembers customer preferences and enables you to send targeted promotions through the platform. Increase order frequency and size through personalized recommendations.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">💰</div>
                        <h3>Cost Effective</h3>
                        <p>Reduce staffing costs while improving customer service. Our AI agents handle multiple calls simultaneously without breaks.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <h3>Accurate Orders</h3>
                        <p>Eliminate order mistakes with precise AI that confirms details, handles modifications, and processes payments seamlessly.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔄</div>
                        <h3>Daily Learning Loop</h3>
                        <p>Receive daily reports of novel questions and unique customer inquiries to continuously expand your AI's knowledge. Stay ahead of trends and ensure your agent evolves with your business.</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="demo" class="demo">
            <div class="container">
                <h2>Experience Our AI in Action</h2>
                <div class="demo-card">
                    <h3>🍣 Call Shizen Restaurant</h3>
                    <p>Try our live demo by calling our AI agent "Pluto" at Shizen, a vegan sushi restaurant in San Francisco.</p>
                    <div class="phone-number">📞 (415) 449-7391</div>
                    <p><strong>Some example queries:</strong></p>
                    <ul style="text-align: left; margin: 1rem 0; padding-left: 2rem;">
                        <li>Make a reservation for your party</li>
                        <li>Ask about the vegan menu options</li>
                        <li>Inquire about hours and location</li>
                        <li>Place a to-go order</li>
                        <li>Ask about dietary accommodations</li>
                    </ul>
                </div>
            </div>
        </section>

        <section id="contact" class="footer">
            <div class="container">
                <h3>Ready to Transform Your Restaurant?</h3>
                <p>Contact us today to set up your custom AI voice agent</p>
                <p style="margin-top: 1rem;">
                    <strong>Email:</strong> hello@getplutoai.net | 
                    <strong>Phone:</strong> (608) 886-1118
                </p>
                <p style="margin-top: 2rem; opacity: 0.7;">
                    © 2025 Pluto
                </p>
            </div>
        </section>

        <script>
            // Smooth scrolling for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });

            // Add scroll effect to header
            window.addEventListener('scroll', () => {
                const header = document.querySelector('header');
                if (window.scrollY > 100) {
                    header.style.background = 'rgba(255, 255, 255, 0.98)';
                } else {
                    header.style.background = 'rgba(255, 255, 255, 0.95)';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview',
        additional_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        await initialize_session(openai_ws)

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None
        
        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.state is State.OPEN:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)

                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                        # Update last_assistant_item safely
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        print("Speech started detected.")
                        if last_assistant_item:
                            print(f"Interrupting response with id: {last_assistant_item}")
                            await handle_speech_started_event()
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_initial_conversation_item(openai_ws):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Greet the customer by saying: 'Hello! Thank you for calling Shizen. I'm Pluto can I assist you today?'"
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))


async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

    # Uncomment the next line to have the AI speak first
    await send_initial_conversation_item(openai_ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

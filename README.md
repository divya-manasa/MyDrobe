# SmartStyle AI - Your Personal Wardrobe & Outfit Designer

🏔️ **AI-Powered Fashion Intelligence with Himalayan Elegance**

A complete GenAI web application that helps you organize your wardrobe, generate outfits, get personalized styling advice, and optimize your fashion choices using advanced AI models.

## ✨ Features

### 1️⃣ **Wardrobe Organizer**
- AI-powered clothing detection (type, color, pattern, style)
- Auto-categorization into folders
- Upload via camera, gallery, or barcode scanning
- Tag items (Favorite, Seasonal, New, Brand)
- Track wear frequency and last worn dates

### 2️⃣ **Occasion-Based Outfit Suggestions**
- AI generates complete outfits for any event
- Weather-aware recommendations
- Calendar integration
- Multiple style variations per occasion

### 3️⃣ **Prompt-to-Outfit Generation**
- Text or voice input support
- AI-powered visual outfit rendering
- Cross-match with wardrobe
- Smart shopping for missing items

### 4️⃣ **Smart Shopping Assistant**
- Wardrobe gap detection
- Product recommendations with price comparison
- Eco-friendly alternatives
- Preference-based filtering

### 5️⃣ **Real-Time Styling Intelligence**
- Weather-based alerts
- Location trending fashion
- Daily color/style recommendations
- Push notifications

### 6️⃣ **Style Coach Chatbot**
- Powered by IBM Granite 3.1 8B model
- Conversational fashion advice
- Personalized recommendations
- Voice chat support

### 7️⃣ **Analytics Dashboard**
- Most/least worn items
- Cost per wear analysis
- Seasonal analytics
- Eco-score tracking
- Visual charts and graphs

### 8️⃣ **AI Outfit Refresher**
- New combinations from existing wardrobe
- Avoid outfit repetition
- Smart recombination engine

### 9️⃣ **Body Shape & Fit Analyzer**
- AI-powered body shape determination
- Personalized fit recommendations
- Style suggestions for your shape

### 🔟 **Smart Packing Assistant**
- Travel outfit planning
- Weather forecast integration
- Daily packing list
- Missing item alerts

### 1️⃣1️⃣ **Outfit Comparison Mode**
- Compare two outfits side-by-side
- AI scoring and reasoning
- Event suitability analysis

## 🚀 Technology Stack

### Frontend
- **Pure HTML/CSS/JavaScript** - No frameworks
- **Himalayan Mountains Aesthetic** - Blues, greens, grays, snow-white
- **Responsive Design** - Mobile-first approach
- **Smooth Animations** - Micro-interactions and transitions
- **Web Speech API** - Voice input support

### Backend
- **Python 3.9+** with FastAPI
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **SQLite** - Database (production-ready)
- **JWT Authentication** - Secure token-based auth

### AI Services
- **Groq LLM API** - Lightning-fast AI processing
- **Hugging Face** - IBM Granite model for chatbot
- **OpenWeather API** - Real-time weather data
- **SerpAPI** - Google Shopping integration

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- API Keys:
  - [Groq API Key](https://console.groq.com/)
  - [Hugging Face API Key](https://huggingface.co/settings/tokens)
  - [OpenWeather API Key](https://openweathermap.org/api)
  - [SerpAPI Key](https://serpapi.com/)

## 🔧 Installation

### 1. Clone or Download the Project

Navigate to project directory
cd smartstyle-ai

text

### 2. Set Up Environment Variables

Copy the example environment file
cp .env.example .env

Edit .env with your API keys
Linux/Mac:
nano .env

Windows:
notepad .env

text

Add your API keys:
GROQ_API_KEY=gsk_your_groq_api_key_here
HUGGINGFACE_API_KEY=hf_your_huggingface_token_here
OPENWEATHER_API_KEY=your_openweather_key_here
SERPAPI_KEY=your_serpapi_key_here
SECRET_KEY_JWT=your_super_secret_jwt_key_change_this

text

### 3. Install Python Dependencies

cd backend
pip install -r requirements.txt

text

### 4. Initialize Database

Run database migrations
python -c "from app.database import init_db; init_db()"

Seed initial data
python seed_data.py

text

## 🏃 Running the Application

### Quick Start (One Command)

From project root directory
python backend/app/main.py

text

### Access the Application

Open your browser and navigate to:
http://localhost:8000

text

### Demo Account

Email: demo@smartstyle.ai
Password: Demo123!

text

## 🐳 Docker Deployment (Optional)

Build and run with Docker Compose
docker-compose up --build

Access at http://localhost:8000
# Calo AI Nutrition Advisor - Backend

An intelligent meal recommendation and feedback analysis system powered by local LLMs (Ollama) and RAG (ChromaDB).

## 🌟 Features

- **Multi-Agent AI System**: 4 specialized agents for different tasks
  - Preference Learner: Learns user dietary needs and preferences
  - Meal Recommender: Provides personalized meal recommendations
  - Feedback Analyzer: Analyzes customer feedback with sentiment analysis
  - Kitchen Router: Routes special requests to kitchen team

- **RAG-Powered Search**: Semantic meal search using ChromaDB
- **Local LLM**: Uses Ollama (llama3.2) for cost-effective AI
- **Real-time Chat**: Conversational interface with context awareness
- **Analytics Dashboard**: Customer feedback insights and trends
- **Kitchen Management**: Special request tracking and prioritization

## 🛠️ Tech Stack

- **FastAPI**: High-performance async Python framework
- **Ollama**: Local LLM inference (llama3.2)
- **ChromaDB**: Vector database for RAG
- **Pydantic v2**: Data validation and settings management
- **httpx**: Async HTTP client

## 📋 Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull the llama3.2 model
   ollama pull llama3.2
   ```

## 🚀 Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if you need to change default settings
   ```

4. **Start Ollama** (in separate terminal)
   ```bash
   ollama serve
   ```

## 🏃 Running the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 API Endpoints

### Chat
- `POST /api/v1/chat/` - Send message to AI agent
- `POST /api/v1/chat/stream` - Streaming chat response
- `GET /api/v1/chat/history/{conversation_id}` - Get conversation history

### Recommendations
- `POST /api/v1/recommendations/` - Get personalized meal recommendations
- `GET /api/v1/recommendations/meal/{meal_id}` - Get meal details
- `GET /api/v1/recommendations/browse` - Browse meals with filters
- `GET /api/v1/recommendations/popular` - Get popular meals

### Kitchen
- `POST /api/v1/kitchen/request` - Create special kitchen request
- `GET /api/v1/kitchen/requests` - List all requests
- `GET /api/v1/kitchen/dashboard` - Kitchen dashboard stats
- `PATCH /api/v1/kitchen/request/{id}/status` - Update request status

### Analytics
- `POST /api/v1/analytics/feedback` - Submit customer feedback
- `GET /api/v1/analytics/feedback` - List feedback with filters
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/trends` - Get feedback trends

## 💡 Usage Examples

### Chat with AI
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I am looking for high-protein meals",
    "user_id": "user123"
  }'
```

### Get Recommendations
```bash
curl -X POST "http://localhost:8000/api/v1/recommendations/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "dietary_restrictions": ["high_protein", "gluten_free"],
    "calorie_target": 500,
    "max_results": 5
  }'
```

### Submit Feedback
```bash
curl -X POST "http://localhost:8000/api/v1/analytics/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "meal_id": "meal_001",
    "rating": 5,
    "comment": "Absolutely delicious! The chicken was perfectly seasoned."
  }'
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   │   ├── chat.py
│   │   ├── meal.py
│   │   └── feedback.py
│   ├── services/            # Business logic
│   │   ├── llm_service.py   # Ollama integration
│   │   ├── rag_service.py   # ChromaDB RAG
│   │   ├── agent_service.py # Multi-agent orchestration
│   │   └── meal_service.py  # Meal operations
│   ├── routers/             # API routes
│   │   ├── chat.py
│   │   ├── recommendations.py
│   │   ├── kitchen.py
│   │   └── analytics.py
│   ├── prompts/             # LLM prompts
│   │   └── agent_prompts.py
│   └── data/                # Sample data
│       └── meals.json
├── requirements.txt
└── README.md
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_TIMEOUT=120

# ChromaDB Settings
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=calo_meals

# Agent Settings
MAX_CONVERSATION_HISTORY=10
TEMPERATURE=0.7
MAX_TOKENS=1000
```

## 🧪 Testing

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "api": "operational",
    "llm": "operational",
    "rag": "operational"
  }
}
```

## 🐛 Troubleshooting

### Ollama not connecting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### ChromaDB errors
```bash
# Clear ChromaDB cache
rm -rf ./chroma_db
# Restart the application
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📊 Sample Data

The system includes 5 sample meals covering various dietary preferences:
- Grilled Chicken Quinoa Bowl (high-protein, gluten-free, halal)
- Mediterranean Falafel Wrap (vegetarian, high-protein)
- Salmon Teriyaki with Brown Rice (high-protein, dairy-free)
- Keto Beef and Veggie Stir Fry (keto, low-carb)
- Vegan Buddha Bowl (vegan, gluten-free)

## 🎯 Key Features

### Multi-Agent Intelligence
The system automatically routes user queries to specialized agents:
- Simple questions → Preference Learner
- Meal inquiries → Meal Recommender
- Complaints/reviews → Feedback Analyzer
- Special requests → Kitchen Router

### RAG-Powered Recommendations
- Semantic search through meal database
- Context-aware recommendations
- Personalization based on user preferences
- Nutritional goal alignment

### Real-time Analytics
- Sentiment analysis on feedback
- Trend detection over time
- Actionable insights generation
- Kitchen dashboard for operations

## 📝 License

This is a demonstration project for the Calo AI Specialist application.

## 👤 Author

Built by Ali Dakheel for Calo AI Specialist position application.

## 🙏 Acknowledgments

- FastAPI for the excellent framework
- Ollama for local LLM inference
- ChromaDB for vector storage
- Anthropic Claude for development assistance

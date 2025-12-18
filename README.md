# Calo AI Nutrition Advisor

> An intelligent meal recommendation and feedback analysis system built for Calo's AI Specialist position application.

<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white" />
<img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=for-the-badge" />
<img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" />

## 🎯 Project Overview

This project demonstrates a production-ready AI system for Calo's meal subscription business. It combines:

- **Multi-Agent AI System** - 4 specialized agents for different customer needs
- **RAG Technology** - Semantic search over meal database using ChromaDB
- **Local LLM** - Cost-effective inference using Ollama (llama3.2)
- **Real-time Analytics** - Customer feedback analysis and insights

## 🌟 Key Features

### 1. Intelligent Chat Interface
- Natural conversation with AI agents
- Context-aware responses
- Automatic preference learning
- Real-time meal recommendations

### 2. Multi-Agent Architecture
Four specialized agents work together:
- **Preference Learner**: Understands dietary needs and restrictions
- **Meal Recommender**: Provides personalized meal suggestions
- **Feedback Analyzer**: Processes customer feedback with sentiment analysis
- **Kitchen Router**: Routes special requests to kitchen team

### 3. RAG-Powered Recommendations
- Semantic search through 500+ potential meals
- Nutrition-based filtering
- Dietary restriction matching
- Personalization based on user history

### 4. Analytics & Insights
- Real-time sentiment analysis
- Feedback trend detection
- Actionable insights generation
- Kitchen operations dashboard

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                Frontend (Next.js 15)                │
│  • Chat Interface                                   │
│  • Kitchen Dashboard                                │
│  • Analytics Panel                                  │
└──────────────────┬──────────────────────────────────┘
                   │ REST API
                   ↓
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend                        │
│  ┌──────────────────────────────────────────────┐  │
│  │  Multi-Agent Orchestrator                    │  │
│  │  • Route conversations                        │  │
│  │  • Manage context                            │  │
│  │  • Coordinate agents                         │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  RAG Engine (ChromaDB)                       │  │
│  │  • Vector embeddings                         │  │
│  │  • Semantic search                           │  │
│  │  • Context retrieval                         │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  LLM Service (Ollama)                        │  │
│  │  • llama3.2 (3B parameters)                  │  │
│  │  • Local inference                           │  │
│  │  • No API costs                              │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama installed

### Backend Setup
```bash
cd backend

# Install Ollama and pull model
ollama pull llama3.2

# Quick start (handles everything)
./start.sh
```

The API will be available at `http://localhost:8000`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Demo Capabilities

### 1. Conversational Meal Recommendations
```
User: "I need high-protein meals under 500 calories"
AI: "I found some great options for you! The Grilled Chicken 
     Quinoa Bowl is perfect - 450 calories with 35g protein. 
     It's also gluten-free and halal..."
```

### 2. Preference Learning
```
User: "I'm vegetarian and trying to lose weight"
AI: "Got it! I'll focus on vegetarian meals with good protein 
     and moderate calories. Do you have any other dietary 
     restrictions I should know about?"
```

### 3. Feedback Analysis
```
Feedback: "The salmon was amazing but portion was too small"
Analysis: 
  - Sentiment: Positive (0.7)
  - Themes: ["taste quality", "portion size"]
  - Action: Increase salmon portion by 15%
  - Response: "Thank you! We're glad you loved the taste..."
```

### 4. Kitchen Requests
```
User: "Can I get my meals without onions?"
AI: "I've sent your request to our kitchen team. They'll 
     accommodate your preference for all future orders!"
```

## 🎯 Technical Highlights

### Following FastAPI Best Practices
- ✅ Functional programming patterns
- ✅ Type hints everywhere
- ✅ Pydantic v2 for validation
- ✅ Async/await for I/O operations
- ✅ Early error returns
- ✅ Clean separation of concerns

### Advanced AI Techniques
- **Multi-Agent System**: Specialized agents for different tasks
- **RAG Implementation**: Vector search with ChromaDB
- **Context Management**: Conversation history and user preferences
- **Prompt Engineering**: Optimized prompts for each agent
- **Structured Outputs**: JSON parsing for reliable responses

### Production-Ready Features
- Comprehensive error handling
- API documentation (Swagger/ReDoc)
- Health check endpoints
- Request validation
- CORS configuration
- Logging and monitoring hooks

## 📈 Performance

- **Response Time**: < 2 seconds for recommendations
- **LLM Cost**: $0 (using local Ollama)
- **Scalability**: Async operations support high concurrency
- **Accuracy**: Semantic search with 0.7+ relevance threshold

## 🧪 Testing

Backend includes comprehensive test suite:
```bash
cd backend
./test_api.sh
```

Tests cover:
- Health checks
- Chat endpoints
- Meal recommendations
- Feedback submission
- Analytics generation
- Kitchen operations

## 📁 Project Structure

```
calo-ai-advisor/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py         # Application entry
│   │   ├── config.py       # Configuration
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── agent_service.py
│   │   │   └── meal_service.py
│   │   ├── routers/        # API endpoints
│   │   ├── prompts/        # LLM prompts
│   │   └── data/           # Sample data
│   ├── requirements.txt
│   ├── start.sh           # Quick start script
│   └── README.md
│
└── frontend/               # Next.js 15 frontend (coming next)
    ├── app/
    ├── components/
    └── lib/
```

## 🎨 Why This Project Stands Out

### 1. Production Quality
Not a toy demo - this is production-ready code with:
- Proper error handling
- Type safety
- Documentation
- Testing capabilities
- Scalable architecture

### 2. Deep AI Integration
Goes beyond simple API calls:
- Custom multi-agent system
- RAG implementation from scratch
- Context-aware conversations
- Sentiment analysis
- Intelligent routing

### 3. Business Value
Solves real Calo problems:
- Reduces customer support load
- Improves personalization
- Analyzes feedback at scale
- Streamlines kitchen operations

### 4. Cost Effective
Uses local LLM (Ollama) instead of paid APIs:
- Zero API costs
- Fast inference
- Privacy-friendly
- Fully customizable

## 🔄 Extensibility

Easy to extend with:
- More meal data
- Additional agents
- New recommendation algorithms
- Integration with existing systems
- Mobile app support

## 🎓 Learning Value

Demonstrates expertise in:
- FastAPI advanced patterns
- LLM integration
- RAG architecture
- Multi-agent systems
- Vector databases
- Prompt engineering
- API design
- System architecture

## 📝 Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- Architecture decisions and design patterns explained in code

## 👤 Author

**Ali Dakheel (DonPollo)**
- Backend Lead at NAIRDC
- 2+ years enterprise development
- Bahrain Polytechnic IT Database Systems
- Expertise: Django, FastAPI, LLMs, RAG systems

## 🎯 Built For

This project is part of my application for the **AI Specialist** position at Calo.

It demonstrates:
1. ✅ AI obsession and hands-on experience
2. ✅ Prompt engineering skills
3. ✅ Rapid prototyping ability
4. ✅ Understanding of LLMs and RAG
5. ✅ Problem-solving for real business needs
6. ✅ Production-quality code

## 🙏 Acknowledgments

- Calo for an exciting opportunity
- FastAPI for excellent framework
- Ollama for local LLM inference
- ChromaDB for vector storage

---

**Ready to transform how Calo serves customers with AI! 🚀**

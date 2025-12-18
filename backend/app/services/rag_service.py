"""
RAG Service - Retrieval Augmented Generation with ChromaDB
"""
import chromadb
from typing import List, Dict, Optional
import json
from pathlib import Path

from app.config import get_settings
from app.services.llm_service import embed_text
from app.models.meal import Meal

settings = get_settings()

# Global ChromaDB client and collection
chroma_client: Optional[chromadb.ClientAPI] = None
meal_collection: Optional[chromadb.Collection] = None


async def initialize_rag_engine():
    """Initialize ChromaDB and load meal data"""
    global chroma_client, meal_collection

    # Initialize ChromaDB with persistent client (ChromaDB 0.5+ API)
    persist_path = settings.chroma_persist_directory
    if persist_path:
        chroma_client = chromadb.PersistentClient(path=persist_path)
    else:
        chroma_client = chromadb.EphemeralClient()
    
    # Get or create collection
    try:
        meal_collection = chroma_client.get_collection(settings.chroma_collection_name)
        print(f"✅ Loaded existing collection: {settings.chroma_collection_name}")
    except Exception:
        meal_collection = chroma_client.create_collection(
            name=settings.chroma_collection_name,
            metadata={"description": "Calo meal database with nutritional information"}
        )
        print(f"✅ Created new collection: {settings.chroma_collection_name}")
        
        # Load and index meal data
        await _load_meal_data()


async def _load_meal_data():
    """Load meal data from JSON and index into ChromaDB"""
    global meal_collection
    
    # Path to meal data
    data_path = Path(__file__).parent.parent / "data" / "meals.json"
    
    # If file doesn't exist, create sample data
    if not data_path.exists():
        sample_meals = _generate_sample_meals()
        data_path.parent.mkdir(exist_ok=True)
        with open(data_path, 'w') as f:
            json.dump(sample_meals, f, indent=2)
        print(f"✅ Generated sample meal data")
    
    # Load meals
    with open(data_path, 'r') as f:
        meals_data = json.load(f)
    
    # Index meals
    documents = []
    metadatas = []
    ids = []
    
    for meal in meals_data:
        # Create rich text representation for embedding
        doc_text = _meal_to_document(meal)
        documents.append(doc_text)
        
        # Store metadata
        metadatas.append({
            "id": meal["id"],
            "name": meal["name"],
            "category": meal["category"],
            "dietary_tags": json.dumps(meal["dietary_tags"]),
            "calories": str(meal["nutrition"]["calories"]),
            "protein": str(meal["nutrition"]["protein"]),
            "popularity": str(meal.get("popularity_score", 0.5))
        })
        
        ids.append(meal["id"])
    
    # Add to collection
    meal_collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✅ Indexed {len(meals_data)} meals into ChromaDB")


def _meal_to_document(meal: Dict) -> str:
    """Convert meal dictionary to rich text document for embedding"""
    dietary_tags = ", ".join(meal["dietary_tags"])
    ingredients = ", ".join(meal["ingredients"])
    allergens = ", ".join(meal.get("allergens", []))
    
    doc = f"""
Meal: {meal['name']}
Category: {meal['category']}
Description: {meal['description']}
Dietary Tags: {dietary_tags}
Nutrition: {meal['nutrition']['calories']} calories, {meal['nutrition']['protein']}g protein, {meal['nutrition']['carbs']}g carbs, {meal['nutrition']['fats']}g fat
Ingredients: {ingredients}
Allergens: {allergens}
Preparation Time: {meal['preparation_time']} minutes
Price: ${meal['price']}
"""
    return doc.strip()


async def search_meals(
    query: str,
    dietary_restrictions: Optional[List[str]] = None,
    category: Optional[str] = None,
    max_results: int = 5
) -> List[Dict]:
    """
    Search for meals using semantic search
    
    Args:
        query: Natural language search query
        dietary_restrictions: Filter by dietary tags
        category: Filter by meal category
        max_results: Maximum number of results
        
    Returns:
        List of relevant meals with scores
    """
    global meal_collection
    
    if not meal_collection:
        raise RuntimeError("RAG engine not initialized")
    
    # Build where filter
    where_filter = {}
    if dietary_restrictions:
        # Note: This is simplified - in production, you'd want more sophisticated filtering
        pass
    if category:
        where_filter["category"] = category
    
    # Perform semantic search
    results = meal_collection.query(
        query_texts=[query],
        n_results=max_results,
        where=where_filter if where_filter else None
    )
    
    # Format results
    meals = []
    if results and results['ids'] and len(results['ids'][0]) > 0:
        for i, meal_id in enumerate(results['ids'][0]):
            meals.append({
                "id": meal_id,
                "metadata": results['metadatas'][0][i],
                "document": results['documents'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else 0,
                "relevance_score": 1.0 - (results['distances'][0][i] if 'distances' in results else 0)
            })
    
    return meals


async def get_meal_by_id(meal_id: str) -> Optional[Dict]:
    """Get specific meal by ID"""
    global meal_collection
    
    if not meal_collection:
        raise RuntimeError("RAG engine not initialized")
    
    try:
        result = meal_collection.get(ids=[meal_id])
        if result and result['ids']:
            return {
                "id": result['ids'][0],
                "metadata": result['metadatas'][0],
                "document": result['documents'][0]
            }
    except Exception:
        pass
    
    return None


async def get_contextual_meals(
    user_query: str,
    user_preferences: Optional[Dict] = None,
    top_k: int = 5
) -> tuple[List[Dict], str]:
    """
    Get contextually relevant meals with explanation
    
    Args:
        user_query: User's natural language query
        user_preferences: User preferences dictionary
        top_k: Number of meals to return
        
    Returns:
        Tuple of (meals list, context explanation)
    """
    # Enhance query with preferences
    enhanced_query = user_query
    if user_preferences:
        pref_text = _preferences_to_text(user_preferences)
        enhanced_query = f"{user_query}. User preferences: {pref_text}"
    
    # Search meals
    meals = await search_meals(enhanced_query, max_results=top_k)
    
    # Generate context explanation
    context = f"Found {len(meals)} meals matching: {user_query}"
    
    return meals, context


def _preferences_to_text(preferences: Dict) -> str:
    """Convert preferences dictionary to text"""
    parts = []
    if "dietary_restrictions" in preferences:
        parts.append(f"dietary needs: {', '.join(preferences['dietary_restrictions'])}")
    if "favorite_cuisines" in preferences:
        parts.append(f"favorite cuisines: {', '.join(preferences['favorite_cuisines'])}")
    if "calorie_target" in preferences:
        parts.append(f"target calories: {preferences['calorie_target']}")
    
    return "; ".join(parts) if parts else "no specific preferences"


def _generate_sample_meals() -> List[Dict]:
    """Generate sample meal data for demonstration"""
    return [
        {
            "id": "meal_001",
            "name": "Grilled Chicken Quinoa Bowl",
            "description": "Tender grilled chicken breast served over fluffy quinoa with roasted vegetables and tahini dressing",
            "category": "lunch",
            "dietary_tags": ["high_protein", "gluten_free", "halal"],
            "nutrition": {
                "calories": 450,
                "protein": 35,
                "carbs": 45,
                "fats": 12,
                "fiber": 8,
                "sodium": 520
            },
            "ingredients": ["chicken breast", "quinoa", "bell peppers", "zucchini", "tahini", "lemon", "garlic"],
            "allergens": ["sesame"],
            "preparation_time": 25,
            "price": 12.99,
            "popularity_score": 0.92
        },
        {
            "id": "meal_002",
            "name": "Mediterranean Falafel Wrap",
            "description": "Crispy baked falafel with fresh vegetables, hummus, and cucumber yogurt sauce in whole wheat wrap",
            "category": "lunch",
            "dietary_tags": ["vegetarian", "high_protein"],
            "nutrition": {
                "calories": 420,
                "protein": 18,
                "carbs": 52,
                "fats": 16,
                "fiber": 12,
                "sodium": 480
            },
            "ingredients": ["chickpeas", "whole wheat wrap", "cucumber", "tomato", "lettuce", "hummus", "yogurt"],
            "allergens": ["gluten", "dairy"],
            "preparation_time": 20,
            "price": 10.99,
            "popularity_score": 0.88
        },
        {
            "id": "meal_003",
            "name": "Salmon Teriyaki with Brown Rice",
            "description": "Pan-seared salmon glazed with homemade teriyaki sauce, served with steamed brown rice and edamame",
            "category": "dinner",
            "dietary_tags": ["high_protein", "dairy_free"],
            "nutrition": {
                "calories": 520,
                "protein": 38,
                "carbs": 48,
                "fats": 18,
                "fiber": 6,
                "sodium": 620
            },
            "ingredients": ["salmon", "brown rice", "edamame", "soy sauce", "ginger", "garlic", "honey"],
            "allergens": ["fish", "soy"],
            "preparation_time": 30,
            "price": 15.99,
            "popularity_score": 0.95
        },
        {
            "id": "meal_004",
            "name": "Keto Beef and Veggie Stir Fry",
            "description": "Tender beef strips with low-carb vegetables in savory sauce, served over cauliflower rice",
            "category": "dinner",
            "dietary_tags": ["keto", "low_carb", "high_protein", "gluten_free", "halal"],
            "nutrition": {
                "calories": 380,
                "protein": 32,
                "carbs": 12,
                "fats": 24,
                "fiber": 4,
                "sodium": 540
            },
            "ingredients": ["beef sirloin", "cauliflower", "broccoli", "bell peppers", "coconut aminos", "sesame oil"],
            "allergens": [],
            "preparation_time": 25,
            "price": 14.99,
            "popularity_score": 0.85
        },
        {
            "id": "meal_005",
            "name": "Vegan Buddha Bowl",
            "description": "Colorful bowl with roasted chickpeas, sweet potato, kale, quinoa, and creamy tahini dressing",
            "category": "lunch",
            "dietary_tags": ["vegan", "gluten_free", "high_protein"],
            "nutrition": {
                "calories": 410,
                "protein": 16,
                "carbs": 58,
                "fats": 14,
                "fiber": 14,
                "sodium": 420
            },
            "ingredients": ["chickpeas", "sweet potato", "kale", "quinoa", "tahini", "lemon", "olive oil"],
            "allergens": ["sesame"],
            "preparation_time": 30,
            "price": 11.99,
            "popularity_score": 0.90
        }
    ]

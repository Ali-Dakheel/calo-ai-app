#!/bin/bash

# Calo AI API Test Script

API_BASE="http://localhost:8000"

echo "🧪 Testing Calo AI Nutrition Advisor API"
echo "========================================"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing health endpoint..."
response=$(curl -s "$API_BASE/health")
if echo "$response" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Chat endpoint
echo "2️⃣  Testing chat endpoint..."
response=$(curl -s -X POST "$API_BASE/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want high-protein meals",
    "user_id": "test_user"
  }')

if echo "$response" | grep -q "message"; then
    echo "✅ Chat endpoint working"
    echo "Response preview:"
    echo "$response" | python3 -m json.tool | head -n 10
else
    echo "❌ Chat endpoint failed"
fi
echo ""

# Test 3: Browse meals
echo "3️⃣  Testing browse meals endpoint..."
response=$(curl -s "$API_BASE/api/v1/recommendations/browse?limit=3")
if echo "$response" | grep -q "meals"; then
    echo "✅ Browse meals working"
    meal_count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['total'])")
    echo "Found $meal_count meals in database"
else
    echo "❌ Browse meals failed"
fi
echo ""

# Test 4: Get popular meals
echo "4️⃣  Testing popular meals endpoint..."
response=$(curl -s "$API_BASE/api/v1/recommendations/popular?limit=3")
if echo "$response" | grep -q "meals"; then
    echo "✅ Popular meals working"
else
    echo "❌ Popular meals failed"
fi
echo ""

# Test 5: Submit feedback
echo "5️⃣  Testing feedback submission..."
response=$(curl -s -X POST "$API_BASE/api/v1/analytics/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "meal_id": "meal_001",
    "rating": 5,
    "comment": "Absolutely delicious meal! Great taste and healthy."
  }')

if echo "$response" | grep -q "feedback_id"; then
    echo "✅ Feedback submission working"
else
    echo "❌ Feedback submission failed"
fi
echo ""

# Test 6: Analytics summary
echo "6️⃣  Testing analytics summary..."
response=$(curl -s "$API_BASE/api/v1/analytics/summary?days=30")
if echo "$response" | grep -q "total_feedback"; then
    echo "✅ Analytics summary working"
else
    echo "❌ Analytics summary failed"
fi
echo ""

# Test 7: Kitchen dashboard
echo "7️⃣  Testing kitchen dashboard..."
response=$(curl -s "$API_BASE/api/v1/kitchen/dashboard")
if echo "$response" | grep -q "statistics"; then
    echo "✅ Kitchen dashboard working"
else
    echo "❌ Kitchen dashboard failed"
fi
echo ""

echo "========================================"
echo "✨ API testing complete!"
echo ""
echo "Visit these URLs for more:"
echo "  - API Docs: $API_BASE/docs"
echo "  - Health: $API_BASE/health"
echo ""

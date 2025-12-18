"""
Kitchen Router - Special requests and custom orders
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import uuid

from app.models.feedback import KitchenRequest
from app.services.seed_data import get_demo_kitchen_requests

router = APIRouter()

# In-memory storage for demo (use database in production)
kitchen_requests: dict[str, KitchenRequest] = {}


def _load_seed_data():
    """Load demo data for presentation"""
    for request in get_demo_kitchen_requests():
        kitchen_requests[request.request_id] = request


# Load seed data on module import
_load_seed_data()


@router.post("/request")
async def create_kitchen_request(
    user_id: str,
    message: str,
    request_type: str,
    details: dict,
    priority: int = 3
):
    """
    Create a special kitchen request
    
    Args:
        user_id: User making the request
        message: Original message from user
        request_type: Type of request (modification, allergy, etc.)
        details: Request details
        priority: Priority level (1-5)
        
    Returns:
        Created kitchen request
    """
    if not user_id or not message:
        raise HTTPException(status_code=400, detail="User ID and message are required")
    
    if priority < 1 or priority > 5:
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 5")
    
    # Create request
    request_id = str(uuid.uuid4())
    
    request = KitchenRequest(
        request_id=request_id,
        user_id=user_id,
        original_message=message,
        request_type=request_type,
        details=details,
        priority=priority,
        status="pending",
        created_at=datetime.now()
    )
    
    kitchen_requests[request_id] = request
    
    return {
        "request_id": request_id,
        "status": "created",
        "message": "Your request has been sent to the kitchen team"
    }


@router.get("/requests")
async def get_all_requests(
    status: Optional[str] = None,
    priority_min: Optional[int] = None
):
    """
    Get all kitchen requests with optional filters
    
    Args:
        status: Filter by status (pending, in_progress, completed, cancelled)
        priority_min: Minimum priority level
        
    Returns:
        List of kitchen requests
    """
    requests = list(kitchen_requests.values())
    
    # Apply filters
    if status:
        requests = [r for r in requests if r.status == status]
    
    if priority_min:
        requests = [r for r in requests if r.priority >= priority_min]
    
    # Sort by priority (high to low) then by date (recent first)
    requests.sort(
        key=lambda r: (-r.priority, -r.created_at.timestamp())
    )
    
    return {
        "total": len(requests),
        "requests": [r.model_dump() for r in requests]
    }


@router.get("/request/{request_id}")
async def get_request(request_id: str):
    """
    Get specific kitchen request
    
    Args:
        request_id: Request identifier
        
    Returns:
        Kitchen request details
    """
    if request_id not in kitchen_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return kitchen_requests[request_id].model_dump()


@router.patch("/request/{request_id}/status")
async def update_request_status(
    request_id: str,
    status: str,
    notes: Optional[str] = None
):
    """
    Update kitchen request status
    
    Args:
        request_id: Request identifier
        status: New status (pending, in_progress, completed, cancelled)
        notes: Optional notes about the update
        
    Returns:
        Updated request
    """
    if request_id not in kitchen_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    request = kitchen_requests[request_id]
    request.status = status
    
    return {
        "request_id": request_id,
        "status": status,
        "message": f"Request status updated to {status}",
        "notes": notes
    }


@router.get("/dashboard")
async def get_kitchen_dashboard():
    """
    Get kitchen dashboard with statistics
    
    Returns:
        Dashboard statistics and urgent requests
    """
    requests = list(kitchen_requests.values())
    
    # Calculate statistics
    total = len(requests)
    pending = len([r for r in requests if r.status == "pending"])
    in_progress = len([r for r in requests if r.status == "in_progress"])
    completed = len([r for r in requests if r.status == "completed"])
    
    # Get urgent requests (priority 4-5, pending or in_progress)
    urgent = [
        r for r in requests
        if r.priority >= 4 and r.status in ["pending", "in_progress"]
    ]
    urgent.sort(key=lambda r: (-r.priority, -r.created_at.timestamp()))
    
    # Get recent requests (last 10)
    recent = sorted(
        requests,
        key=lambda r: r.created_at,
        reverse=True
    )[:10]
    
    # Group by request type
    by_type = {}
    for request in requests:
        req_type = request.request_type
        if req_type not in by_type:
            by_type[req_type] = 0
        by_type[req_type] += 1
    
    return {
        "statistics": {
            "total_requests": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed
        },
        "urgent_requests": [r.model_dump() for r in urgent],
        "recent_requests": [r.model_dump() for r in recent],
        "requests_by_type": by_type
    }


@router.delete("/request/{request_id}")
async def delete_request(request_id: str):
    """
    Delete a kitchen request
    
    Args:
        request_id: Request identifier
        
    Returns:
        Success message
    """
    if request_id not in kitchen_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    del kitchen_requests[request_id]
    
    return {"message": "Request deleted successfully"}

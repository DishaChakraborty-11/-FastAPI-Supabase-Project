
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Any

# Pydantic model for session_metadata table
class SessionMetadata(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    user_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    summary: Optional[str] = None

# Pydantic model for event_log table
class EventLog(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str
    event_data: Any

import os
from dotenv import load_dotenv
from supabase import AsyncClient, create_client
from fastapi import Depends, HTTPException, status

# Load environment variables
load_dotenv()

async def get_supabase_client():
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase credentials not found in environment variables."
        )
    try:
        # Ensure to create a new client for each request to avoid session issues
        supabase_client: AsyncClient = create_client(supabase_url, supabase_key)
        yield supabase_client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Supabase client: {e}"
        )


from fastapi import Depends, HTTPException, status, APIRouter
from typing import List

# Create an API router for better organization
api_router = APIRouter()

# Dependency to get Supabase client (already defined above in app.py)
# async def get_supabase_client():
#     ...

# Endpoints for SessionMetadata
@api_router.post("/sessions/", response_model=SessionMetadata, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionMetadata,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("session_metadata").insert(session_data.model_dump_json()).execute()
        # Supabase insert response returns a data list, take the first item if successful
        if response.data and isinstance(response.data, list) and len(response.data) > 0:
            return response.data[0]
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create session in Supabase.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@api_router.get("/sessions/{session_id}", response_model=SessionMetadata)
async def get_session(
    session_id: UUID,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("session_metadata").select("*").eq("session_id", str(session_id)).single().execute()
        if response.data:
            return response.data
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

# Endpoints for EventLog
@api_router.post("/events/", response_model=EventLog, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventLog,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("event_log").insert(event_data.model_dump_json()).execute()
        if response.data and isinstance(response.data, list) and len(response.data) > 0:
            return response.data[0]
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create event in Supabase.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@api_router.get("/sessions/{session_id}/events", response_model=List[EventLog])
async def get_events_for_session(
    session_id: UUID,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("event_log").select("*").eq("session_id", str(session_id)).order("timestamp").execute()
        if response.data:
            return response.data
        return [] # Return empty list if no events found for the session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

# Include the router in the main FastAPI app
app.include_router(api_router)

from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/websocket_test", response_class=HTMLResponse)
async def websocket_test_page(request: Request):
    return templates.TemplateResponse("websocket_client.html", {"request": request})

from fastapi import Depends, HTTPException, status, APIRouter
from typing import List

# Create an API router for better organization
api_router = APIRouter()

# Dependency to get Supabase client (already defined above in app.py)
# async def get_supabase_client():
#     ...

# Endpoints for SessionMetadata
@api_router.post("/sessions/", response_model=SessionMetadata, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionMetadata,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("session_metadata").insert(session_data.model_dump_json()).execute()
        # Supabase insert response returns a data list, take the first item if successful
        if response.data and isinstance(response.data, list) and len(response.data) > 0:
            return response.data[0]
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create session in Supabase.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@api_router.get("/sessions/{session_id}", response_model=SessionMetadata)
async def get_session(
    session_id: UUID,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("session_metadata").select("*").eq("session_id", str(session_id)).single().execute()
        if response.data:
            return response.data
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

# Endpoints for EventLog
@api_router.post("/events/", response_model=EventLog, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventLog,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("event_log").insert(event_data.model_dump_json()).execute()
        if response.data and isinstance(response.data, list) and len(response.data) > 0:
            return response.data[0]
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create event in Supabase.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

@api_router.get("/sessions/{session_id}/events", response_model=List[EventLog])
async def get_events_for_session(
    session_id: UUID,
    supabase: AsyncClient = Depends(get_supabase_client)
):
    try:
        response = await supabase.table("event_log").select("*").eq("session_id", str(session_id)).order("timestamp").execute()
        if response.data:
            return response.data
        return [] # Return empty list if no events found for the session
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")

# Include the router in the main FastAPI app
app.include_router(api_router)

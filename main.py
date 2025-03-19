from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import uuid
from database import db_service
import asyncio

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, group_name: str):
        await websocket.accept()
        if group_name not in self.active_connections:
            self.active_connections[group_name] = []
        self.active_connections[group_name].append(websocket)

    def disconnect(self, websocket: WebSocket, group_name: str):
        if group_name in self.active_connections:
            self.active_connections[group_name].remove(websocket)
            if not self.active_connections[group_name]:
                del self.active_connections[group_name]

    async def broadcast(self, message: str, group_name: str):
        if group_name in self.active_connections:
            for connection in self.active_connections[group_name]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    await db_service.init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/questionnaire", response_class=HTMLResponse)
async def questionnaire_page(request: Request):
    return templates.TemplateResponse("questionnaire.html", {"request": request})

@app.get("/chat/{group_name}", response_class=HTMLResponse)
async def chat_page(request: Request, group_name: str):
    return templates.TemplateResponse("chat.html", {"request": request, "group_name": group_name})

@app.get("/groups", response_class=HTMLResponse)
async def groups_page(request: Request):
    return templates.TemplateResponse("groups.html", {"request": request})

@app.post("/submit-questionnaire")
async def submit_questionnaire(data: dict):
    try:
        await db_service.save_questionnaire(data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-questionnaire-data")
async def get_questionnaire_data():
    try:
        data = await db_service.get_questionnaire_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{group_name}")
async def websocket_endpoint(websocket: WebSocket, group_name: str):
    await manager.connect(websocket, group_name)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_data["id"] = str(uuid.uuid4())
            await db_service.save_message(message_data)
            await manager.broadcast(data, group_name)
    except WebSocketDisconnect:
        manager.disconnect(websocket, group_name)

@app.post("/save-groups")
async def save_groups(groups: list):
    try:
        await db_service.save_groups(groups)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-groups")
async def get_groups():
    try:
        groups = await db_service.get_groups()
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-messages/{group_name}")
async def get_messages(group_name: str):
    try:
        messages = await db_service.get_messages(group_name)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to manually trigger clustering
@app.get("/run-clustering")
async def trigger_clustering():
    from clustering import run_clustering
    try:
        await run_clustering()
        return {"status": "success", "message": "Clustering completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
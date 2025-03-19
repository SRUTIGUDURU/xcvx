from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import json
import uuid
from datetime import datetime
from sheets_service import SheetsService
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
sheets_service = SheetsService()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, group_name: str):
        await websocket.accept()
        if group_name not in self.active_connections:
            self.active_connections[group_name] = []
        self.active_connections[group_name].append(websocket)

    def disconnect(self, websocket: WebSocket, group_name: str):
        if group_name in self.active_connections:
            self.active_connections[group_name].remove(websocket)

    async def broadcast(self, message: str, group_name: str):
        if group_name in self.active_connections:
            for connection in self.active_connections[group_name]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.post("/submit_questionnaire/")
async def submit_questionnaire(data: Dict[str, Any]):
    try:
        sheets_service.save_questionnaire(data)
        return {"status": "success", "message": "Questionnaire submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_groups/")
async def get_groups():
    try:
        groups = sheets_service.get_groups()
        return groups
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/messages/{group_name}")
async def get_messages(group_name: str):
    try:
        messages = sheets_service.get_messages(group_name)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send_message/")
async def send_message(data: Dict[str, Any]):
    try:
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        message_data = {
            "id": message_id,
            "group_name": data["group_name"],
            "email": data["email"],
            "message": data["message"],
            "timestamp": timestamp
        }
        
        sheets_service.save_message(message_data)
        await manager.broadcast(json.dumps(message_data), data["group_name"])
        return {"status": "success", "message": "Message sent successfully"}
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
            message_data["timestamp"] = datetime.now().isoformat()
            
            sheets_service.save_message(message_data)
            await manager.broadcast(json.dumps(message_data), group_name)
    except WebSocketDisconnect:
        manager.disconnect(websocket, group_name)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


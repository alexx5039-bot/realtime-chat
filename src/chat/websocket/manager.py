from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
            self,
            conversation_id: int,
            websocket: WebSocket,
    ):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(
            self,
            conversation_id: int,
            websocket: WebSocket,
    ):
        connections = self.active_connections.get(conversation_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.active_connections[conversation_id]


    async def broadcast(self, conversation_id: int, message: dict):
        for connection in self.active_connections.get(
            conversation_id,
            [],
        ):
            await connection.send_json(message)
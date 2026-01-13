from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict
import requests
import os

app = FastAPI(
    title="Telegram MCP Server",
    description="MCP-compatible server for sending messages and images to Telegram."
)

# Загружаем секреты из переменных окружения
BOT_TOKEN = os.getenv("8020544313:AAHMouxthG0KboKYlIZl6a1AYjbNxWFe9EI")
CHAT_ID = os.getenv("24237780")

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any]
    id: Any  # Принимает строку, число, null — как требует MCP

@app.get("/")
def root():
    return {"status": "OK", "server": "Telegram MCP Server"}

@app.post("/mcp")
async def mcp_endpoint(req: MCPRequest):
    try:
        # === Стандартный MCP: список инструментов ===
        if req.method == "mcp/listTools":
            tools = [{
                "name": "sendImageToUser",
                "description": "Send an AI-generated image to your Telegram chat.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "imageUrl": {"type": "string", "description": "Public URL of the image"},
                        "caption": {"type": "string", "description": "Optional caption"}
                    },
                    "required": ["imageUrl"]
                }
            }]
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "result": {"tools": tools}
            }

        # === Стандартный MCP: вызов инструмента ===
        elif req.method == "mcp/callTool":
            tool_name = req.params.get("name")
            args = req.params.get("arguments", {})

            if tool_name == "sendImageToUser":
                image_url = args.get("imageUrl")
                caption = args.get("caption", "")

                if not image_url or not BOT_TOKEN:
                    return {
                        "jsonrpc": "2.0",
                        "id": req.id,
                        "error": {"code": -32000, "message": "Missing imageUrl or BOT_TOKEN"}
                    }

                resp = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": CHAT_ID, "photo": image_url, "caption": caption[:1024]},
                    timeout=10
                )

                message = "✅ Image sent to Telegram!" if resp.status_code == 200 else f"❌ Failed: {resp.text}"
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "result": {"content": [{"type": "text", "text": message}]}
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "error": {"code": -32601, "message": "Tool not found"}
                }

        # === Прямой вызов: sendPhoto (для Qwen Desktop и совместимых систем) ===
        elif req.method == "sendPhoto":
            params = req.params
            photo_url = params.get("photoUrl") or params.get("imageUrl")
            caption = params.get("caption", "")
            chat_id = params.get("chatId", CHAT_ID)

            if not photo_url or not BOT_TOKEN:
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "error": {"code": -32000, "message": "Missing photoUrl or BOT_TOKEN"}
                }

            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": chat_id, "photo": photo_url, "caption": caption[:1024]},
                timeout=10
            )

            message = "✅ Photo sent!" if resp.ok else f"❌ Failed: {resp.text}"
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "result": {"content": [{"type": "text", "text": message}]}
            }

        # === Прямой вызов: sendMessage (опционально) ===
        elif req.method == "sendMessage":
            params = req.params
            text = params.get("text")
            chat_id = params.get("chatId", CHAT_ID)

            if not text or not BOT_TOKEN:
                return {
                    "jsonrpc": "2.0",
                    "id": req.id,
                    "error": {"code": -32000, "message": "Missing text or BOT_TOKEN"}
                }

            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                timeout=10
            )

            message = "✅ Message sent!" if resp.ok else f"❌ Failed: {resp.text}"
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "result": {"content": [{"type": "text", "text": message}]}
            }

        # === Неизвестный метод ===
        else:
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "error": {"code": -32601, "message": f"Method '{req.method}' not supported"}
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {"code": -32000, "message": str(e)}
        }

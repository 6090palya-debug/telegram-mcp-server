from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI(
    title="Telegram Image MCP Server",
    description="MCP-compatible server that sends images to your Telegram chat."
)

# Получаем секреты из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: Any

@app.get("/")
def root():
    return {"status": "OK", "server": "Telegram MCP Server"}

@app.post("/mcp")
async def mcp_endpoint(req: MCPRequest):
    try:
        if req.method == "mcp/listTools":
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "result": {
                    "tools": [{
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
                }
            }

        elif req.method == "mcp/callTool":
            tool_name = req.params.get("name")
            args = req.params.get("arguments", {})

            if tool_name == "sendImageToUser":
                image_url = args.get("imageUrl")
                caption = args.get("caption", "")

                if not image_url or not BOT_TOKEN or not CHAT_ID:
                    return {
                        "jsonrpc": "2.0",
                        "id": req.id,
                        "error": {"code": -32000, "message": "Missing required parameters or env vars"}
                    }

                # Отправка в Telegram
                resp = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={"chat_id": CHAT_ID, "photo": image_url, "caption": caption[:1024]},
                    timeout=10
                )

                message = "✅ Image sent to Telegram!" if resp.status_code == 200 else "❌ Failed to send"
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

        else:
            return {
                "jsonrpc": "2.0",
                "id": req.id,
                "error": {"code": -32601, "message": "Method not supported"}
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": req.id,
            "error": {"code": -32000, "message": str(e)}
        }

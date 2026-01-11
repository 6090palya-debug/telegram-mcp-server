# Telegram MCP Server

MCP-compatible HTTP server that sends AI-generated images to your Telegram chat.

## 🚀 Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click the button above
2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN` — your bot token from @BotFather
   - `TELEGRAM_CHAT_ID` — your chat ID (get via https://api.telegram.org/bot<TOKEN>/getUpdates)
3. Deploy!

Your endpoint will be: `https://your-app.onrender.com/mcp`

## 🧪 Test

```bash
curl -X POST https://your-app.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "mcp/listTools",
    "params": {},
    "id": "1"
  }'

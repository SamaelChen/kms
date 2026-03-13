"""Telegram bot integration"""
from typing import Optional
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from app.config import settings
from app.core.query_orchestrator import query_orchestrator
from app.models.query import QueryRequest


class TelegramBot:
    """Telegram bot handler for IntelliKnow KMS"""
    
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application: Optional[Application] = None
        
        if self.token:
            self.application = Application.builder().token(self.token).build()
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up command and message handlers"""
        if not self.application:
            return
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """👋 Welcome to IntelliKnow KMS!

I can help you find information from your company's knowledge base.

Just ask me questions like:
• "What is the leave policy?"
• "How do I submit an expense report?"
• "What are the security guidelines?"

Use /help for more information."""
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """ℹ️ IntelliKnow KMS Help

I can answer questions about:
• HR policies and procedures
• Legal documents and contracts
• Finance and expense guidelines
• General company information

Just type your question naturally!

Commands:
/start - Start the bot
/help - Show this help message

Tips:
• Be specific in your questions
• I can only answer based on uploaded documents
• If I don't know, I'll tell you"""
        
        await update.message.reply_text(help_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        query_text = update.message.text
        user_id = str(update.effective_user.id)
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Create query request
            request = QueryRequest(
                query=query_text,
                user_id=user_id,
                frontend="telegram"
            )
            
            # Process query
            response = await query_orchestrator.process(request)
            
            # Format response for Telegram (respect 4096 char limit)
            formatted_response = self._format_for_telegram(response.response)
            
            # Send response
            await update.message.reply_text(
                formatted_response,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            error_message = "Sorry, I encountered an error processing your request. Please try again."
            await update.message.reply_text(error_message)
    
    def _format_for_telegram(self, text: str) -> str:
        """Format text for Telegram's message limits"""
        # Telegram has 4096 char limit
        if len(text) > 4000:
            text = text[:4000] + "\n\n... (response truncated)"
        
        return text
    
    async def setup_webhook(self, webhook_url: str) -> bool:
        """Set up webhook for production"""
        if not self.application:
            return False
        
        try:
            await self.application.bot.set_webhook(webhook_url)
            return True
        except Exception as e:
            print(f"Failed to set webhook: {e}")
            return False
    
    async def process_webhook_update(self, update_data: dict):
        """Process webhook update"""
        if not self.application:
            return
        
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)


# Global bot instance
telegram_bot = TelegramBot()
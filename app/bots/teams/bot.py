"""Microsoft Teams bot integration"""
from typing import Optional
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory

from app.config import settings
from app.core.query_orchestrator import query_orchestrator
from app.models.query import QueryRequest


class TeamsBot(ActivityHandler):
    """Microsoft Teams bot handler for IntelliKnow KMS"""
    
    def __init__(self):
        self.app_id = settings.TEAMS_APP_ID
        self.app_password = settings.TEAMS_APP_PASSWORD
    
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """Handle when bot is added to a conversation"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_message = """👋 Welcome to IntelliKnow KMS!

I can help you find information from your company's knowledge base.

Just ask me questions like:
• "What is the leave policy?"
• "How do I submit an expense report?"
• "What are the security guidelines?"

Type 'help' for more information."""
                
                await turn_context.send_activity(MessageFactory.text(welcome_message))
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        query_text = turn_context.activity.text
        user_id = turn_context.activity.from_property.id
        
        # Handle help command
        if query_text.lower() == "help":
            await self._send_help(turn_context)
            return
        
        try:
            # Create query request
            request = QueryRequest(
                query=query_text,
                user_id=user_id,
                frontend="teams"
            )
            
            # Process query
            response = await query_orchestrator.process(request)
            
            # Format for Teams (Markdown supported)
            formatted_response = self._format_for_teams(response.response)
            
            # Send response
            await turn_context.send_activity(MessageFactory.text(formatted_response))
            
        except Exception as e:
            error_message = "Sorry, I encountered an error processing your request. Please try again."
            await turn_context.send_activity(MessageFactory.text(error_message))
    
    async def _send_help(self, turn_context: TurnContext):
        """Send help message"""
        help_message = """ℹ️ IntelliKnow KMS Help

I can answer questions about:
• HR policies and procedures
• Legal documents and contracts
• Finance and expense guidelines
• General company information

Just type your question naturally!

Tips:
• Be specific in your questions
• I can only answer based on uploaded documents
• If I don't know, I'll tell you"""
        
        await turn_context.send_activity(MessageFactory.text(help_message))
    
    def _format_for_teams(self, text: str) -> str:
        """Format text for Teams (supports Markdown)"""
        # Teams supports full Markdown
        # Truncate if too long (Teams has limits)
        if len(text) > 8000:
            text = text[:8000] + "\n\n... (response truncated)"
        
        return text


# Global bot instance
teams_bot = TeamsBot()
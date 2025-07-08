import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import settings
from models.schemas import ChatMessage, SessionInfo

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self):
        self.memory = SqliteSaver.from_conn_string(f"sqlite:///{settings.database_path}")
        self.memory.setup()

    def _convert_to_langchain_message(self, message: ChatMessage) -> BaseMessage:
        """Convert ChatMessage to LangChain message."""
        if message.role == "user":
            return HumanMessage(content=message.content)
        else:
            return AIMessage(content=message.content)

    def _convert_from_langchain_message(self, message: BaseMessage) -> ChatMessage:
        """Convert LangChain message to ChatMessage."""
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        return ChatMessage(
            role=role,
            content=message.content,
            timestamp=datetime.now()
        )

    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Save a message to the session."""
        try:
            # Get current state
            current_state = self.get_session_state(session_id)
            
            # Convert to LangChain message
            lc_message = self._convert_to_langchain_message(message)
            
            # Add to current messages
            current_state["messages"].append(lc_message)
            
            # Save state
            config = {"configurable": {"thread_id": session_id}}
            self.memory.put(config, {"messages": current_state["messages"]})
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current session state."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            checkpoint = self.memory.get(config)
            
            if checkpoint is None:
                return {"messages": []}
            
            return checkpoint.get("channel_values", {"messages": []})
            
        except Exception as e:
            logger.error(f"Error getting session state: {e}")
            return {"messages": []}

    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session."""
        try:
            state = self.get_session_state(session_id)
            messages = state.get("messages", [])
            
            return [self._convert_from_langchain_message(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get conversation context for LLM."""
        try:
            messages = self.get_chat_history(session_id)
            
            # Get last max_messages
            recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
            
            # Convert to format expected by LLM
            context = []
            for msg in recent_messages:
                context.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return []

    def create_session(self, session_id: str) -> None:
        """Create a new session."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            self.memory.put(config, {"messages": []})
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def clear_session(self, session_id: str) -> None:
        """Clear a session."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            self.memory.put(config, {"messages": []})
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            raise

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            checkpoint = self.memory.get(config)
            return checkpoint is not None
            
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        try:
            if not self.session_exists(session_id):
                return None
            
            messages = self.get_chat_history(session_id)
            
            if not messages:
                return SessionInfo(
                    session_id=session_id,
                    created_at=datetime.now(),
                    last_activity=datetime.now(),
                    message_count=0
                )
            
            return SessionInfo(
                session_id=session_id,
                created_at=min(msg.timestamp for msg in messages),
                last_activity=max(msg.timestamp for msg in messages),
                message_count=len(messages)
            )
            
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None
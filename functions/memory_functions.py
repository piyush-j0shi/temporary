"""Service for managing chat session memory.

This module provides functionalities for creating, saving, retrieving, and
clearing chat sessions and messages.
"""

import logging
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from models.schemas import ChatMessage, SessionInfo
from utils.utils import get_sqlite_saver

logger = logging.getLogger(__name__)


class MemoryService:
    """Manages chat session memory using SQLite for persistence."""

    def __init__(self):
        """Initializes the MemoryService with a SQLite saver."""
        self.memory = get_sqlite_saver()

    def _convert_to_langchain_message(self, message: ChatMessage) -> BaseMessage:
        """Converts a ChatMessage object to a LangChain BaseMessage object.

        Args:
            message: The ChatMessage object to convert.

        Returns:
            A LangChain HumanMessage or AIMessage object.
        """
        if message.role == "user":
            return HumanMessage(content=message.content)
        else:
            return AIMessage(content=message.content)

    def _convert_from_langchain_message(self, message: BaseMessage) -> ChatMessage:
        """Converts a LangChain BaseMessage object to a ChatMessage object.

        Args:
            message: The LangChain BaseMessage object to convert.

        Returns:
            A ChatMessage object.
        """
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        return ChatMessage(
            role=role,
            content=message.content,
            timestamp=datetime.now()
        )

    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Saves a message to the specified session.

        If the session does not exist, it will be created.

        Args:
            session_id: The ID of the session.
            message: The ChatMessage object to save.

        Raises:
            Exception: If an error occurs during message saving.
        """
        try:
            config = {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}}
            checkpoint = self.memory.get(config)
            if not checkpoint:
                logger.warning(f"No checkpoint found for session {session_id}. The session may not have been created correctly.")
                self.create_session(session_id)
                checkpoint = self.memory.get(config)

            lc_message = self._convert_to_langchain_message(message)
            checkpoint["channel_values"]["messages"].append(lc_message)
            
            checkpoint["id"] = str(uuid.uuid4())
            checkpoint["ts"] = datetime.now(timezone.utc).isoformat()

            self.memory.put(config, checkpoint, {}, {})
            
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            raise

    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """Retrieves the chat history for a given session.

        Args:
            session_id: The ID of the session.

        Returns:
            A list of ChatMessage objects representing the chat history.
        """
        try:
            config = {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}}
            checkpoint = self.memory.get(config)
            
            if checkpoint is None:
                return []
            
            messages = checkpoint.get("channel_values", {}).get("messages", [])
            return [self._convert_from_langchain_message(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """Retrieves a truncated conversation context for LLM processing.

        Args:
            session_id: The ID of the session.
            max_messages: The maximum number of recent messages to include in the context.

        Returns:
            A list of dictionaries, each representing a message with 'role' and 'content'.
        """
        try:
            messages = self.get_chat_history(session_id)
            recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
            
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
        """Creates a new chat session.

        Args:
            session_id: The ID for the new session.

        Raises:
            Exception: If an error occurs during session creation.
        """
        try:
            config = {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}}
            checkpoint = {
                "v": 1,
                "id": str(uuid.uuid4()),
                "ts": datetime.now(timezone.utc).isoformat(),
                "channel_values": {"messages": []},
                "channel_versions": {},
                "versions_seen": {},
            }
            self.memory.put(config, checkpoint, {}, {})
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def clear_session(self, session_id: str) -> None:
        """Clears all messages from a specified session.

        Args:
            session_id: The ID of the session to clear.

        Raises:
            Exception: If an error occurs during session clearing.
        """
        try:
            config = {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}}
            checkpoint = self.memory.get(config)

            if checkpoint:
                checkpoint["channel_values"]["messages"] = []
                checkpoint["id"] = str(uuid.uuid4())
                checkpoint["ts"] = datetime.now(timezone.utc).isoformat()
                self.memory.put(config, checkpoint, {}, {})
            
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            raise

    def session_exists(self, session_id: str) -> bool:
        """Checks if a session with the given ID exists.

        Args:
            session_id: The ID of the session to check.

        Returns:
            True if the session exists, False otherwise.
        """
        try:
            config = {"configurable": {"thread_id": session_id, "checkpoint_ns": ""}}
            checkpoint = self.memory.get(config)
            return checkpoint is not None
            
        except Exception as e:
            logger.error(f"Error checking session existence: {e}")
            return False

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Retrieves information about a specific session.

        Args:
            session_id: The ID of the session.

        Returns:
            A SessionInfo object if the session exists, None otherwise.
        """
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
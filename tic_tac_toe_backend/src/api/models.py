# models.py - SQLAlchemy ORM models for Tic Tac Toe

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship, declarative_base
from typing import Optional, List
from pydantic import BaseModel, Field
import datetime

Base = declarative_base()


# --- Pydantic Models for API Schemas ---


# PUBLIC_INTERFACE
class GameCreateSchema(BaseModel):
    """Request schema for starting a new game."""
    opponent_id: Optional[int] = Field(
        default=None,
        description="Optional user id to play as 'O'. If not supplied, game is open to join.",
    )


# PUBLIC_INTERFACE
class MoveSchema(BaseModel):
    """Request schema for making a move."""
    row: int = Field(..., ge=0, le=2, description="Board row (0-2)")
    col: int = Field(..., ge=0, le=2, description="Board column (0-2)")


# PUBLIC_INTERFACE
class GameStateSchema(BaseModel):
    """Response schema for delivering the game state."""
    id: int
    player_x_id: int
    player_o_id: Optional[int]
    board: List[List[Optional[str]]]  # 3x3 list of 'x', 'o', or None
    next_turn: str  # 'x' or 'o'
    status: str  # 'ongoing', 'finished', 'draw'
    winner: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime


# PUBLIC_INTERFACE
class GameSummarySchema(BaseModel):
    """Summary of finished or ongoing game for listing."""
    id: int
    player_x_id: int
    player_o_id: Optional[int]
    status: str
    winner: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


# PUBLIC_INTERFACE
class UserGamesResponseSchema(BaseModel):
    """List of games for a user."""
    games: List[GameSummarySchema]


# PUBLIC_INTERFACE
class User(Base):
    """Represents a user account in the Tic Tac Toe system."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    games_as_x = relationship(
        "Game",
        back_populates="player_x",
        foreign_keys="Game.player_x_id",
    )
    games_as_o = relationship(
        "Game",
        back_populates="player_o",
        foreign_keys="Game.player_o_id",
    )


# PUBLIC_INTERFACE
class Game(Base):
    """Represents a Tic Tac Toe game."""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_x_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    player_o_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    state = Column(Text, nullable=False)  # JSON-encoded board state
    status = Column(
        String(16),
        nullable=False,
        default="ongoing",
    )  # 'ongoing','finished','draw'
    winner = Column(String(2), nullable=True)  # 'x', 'o', or None
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    # Relationships
    player_x = relationship(
        "User",
        foreign_keys=[player_x_id],
        back_populates="games_as_x",
    )
    player_o = relationship(
        "User",
        foreign_keys=[player_o_id],
        back_populates="games_as_o",
    )

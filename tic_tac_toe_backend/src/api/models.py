# models.py - SQLAlchemy ORM models for Tic Tac Toe

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()


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

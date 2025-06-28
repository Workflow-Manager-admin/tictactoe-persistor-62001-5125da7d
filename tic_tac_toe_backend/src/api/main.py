from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .db import get_db, init_db
from .models import (
    User,
    Game,
    GameCreateSchema,
    MoveSchema,
    GameStateSchema,
    GameSummarySchema,
    UserGamesResponseSchema,
)
from .auth import get_current_user
from typing import Optional
import datetime
import json
from fastapi import Path


app = FastAPI(
    title="Tic Tac Toe Backend API",
    description="Handles user, game, and authentication logic for Tic Tac Toe.",
    version="0.1.0",
    openapi_tags=[
        {"name": "users", "description": "Authentication and user management APIs"},
        {"name": "games", "description": "Game operations: create, move, query, history"},
    ],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def empty_board() -> list:
    return [[None, None, None], [None, None, None], [None, None, None]]


def parse_state(state: str) -> dict:
    """Decode JSON state string to dict with board, next_turn ('x'/'o')."""
    return json.loads(state)


def dump_state(board: list, next_turn: str) -> str:
    return json.dumps({"board": board, "next_turn": next_turn})


def check_winner(board: list) -> Optional[str]:
    """Check if a player has won. Returns 'x', 'o', or None."""
    lines = (
        board[0], board[1], board[2],
        [board[i][0] for i in range(3)],
        [board[i][1] for i in range(3)],
        [board[i][2] for i in range(3)],
        [board[i][i] for i in range(3)],
        [board[i][2 - i] for i in range(3)],
    )
    for line in lines:
        if line[0] and line.count(line[0]) == 3:
            return line[0]
    return None


def is_full(board: list) -> bool:
    return all(cell for row in board for cell in row)


def game_to_schema(game: Game) -> GameStateSchema:
    state = parse_state(game.state)
    return GameStateSchema(
        id=game.id,
        player_x_id=game.player_x_id,
        player_o_id=game.player_o_id,
        board=state["board"],
        next_turn=state["next_turn"],
        status=game.status,
        winner=game.winner,
        created_at=game.created_at,
        updated_at=game.updated_at,
    )


def game_to_summary(game: Game) -> GameSummarySchema:
    return GameSummarySchema(
        id=game.id,
        player_x_id=game.player_x_id,
        player_o_id=game.player_o_id,
        status=game.status,
        winner=game.winner,
        created_at=game.created_at,
        updated_at=game.updated_at,
    )


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def health_check():
    """Health check endpoint for the Tic Tac Toe backend."""
    return {"message": "Healthy"}


@app.post(
    "/games",
    response_model=GameStateSchema,
    tags=["games"],
    summary="Start a new game",
    description="Creates a new Tic Tac Toe game. Optionally, opponent_id can be provided. "
                "The creator becomes 'X'.",
)
def create_game(
    game_req: GameCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Starts a new game as 'X'. Optionally, assign opponent as 'O'. Board is empty."""
    opponent = None
    if game_req.opponent_id:
        if game_req.opponent_id == current_user.id:
            raise HTTPException(400, "You can't play against yourself.")
        opponent = db.query(User).filter(
            User.id == game_req.opponent_id
        ).first()
        if not opponent:
            raise HTTPException(
                404,
                "Opponent user does not exist."
            )
    board = empty_board()
    state = dump_state(board, next_turn="x")
    game = Game(
        player_x_id=current_user.id,
        player_o_id=opponent.id if opponent else None,
        state=state,
        status="ongoing",
        winner=None,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game_to_schema(game)


@app.post(
    "/games/{game_id}/move",
    response_model=GameStateSchema,
    tags=["games"],
    summary="Make a move",
    description="Submit a move for the current game. Move must be legal, and user must be a player of the game.",
)
def make_move(
    game_id: int = Path(..., description="Game id to play in"),
    move: MoveSchema = ...,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submits a move for a given game if valid, updates board and checks for win/draw."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(404, "Game not found.")

    if game.player_x_id != current_user.id and game.player_o_id != current_user.id:
        raise HTTPException(403, "You are not a player in this game.")

    state = parse_state(game.state)
    board = state["board"]
    next_turn = state["next_turn"]

    if game.status != "ongoing":
        raise HTTPException(400, "Game is not ongoing.")

    if game.player_x_id == current_user.id:
        user_mark = "x"
        if next_turn != "x":
            raise HTTPException(400, "It's not your turn.")
    else:
        user_mark = "o"
        if next_turn != "o":
            raise HTTPException(400, "It's not your turn.")

    r, c = move.row, move.col
    if not (0 <= r <= 2 and 0 <= c <= 2):
        raise HTTPException(422, "Row and column must be in the range 0-2.")
    if board[r][c] is not None:
        raise HTTPException(400, "Cell already occupied.")

    board[r][c] = user_mark

    winner = check_winner(board)
    if winner:
        game.status = "finished"
        game.winner = winner
    elif is_full(board):
        game.status = "draw"
        game.winner = None
    else:
        game.status = "ongoing"
        game.winner = None
        state["next_turn"] = "o" if user_mark == "x" else "x"
    game.state = dump_state(
        board,
        state.get(
            "next_turn",
            "o" if user_mark == "x" else "x"
        ),
    )
    game.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(game)
    return game_to_schema(game)


@app.get(
    "/games/{game_id}",
    response_model=GameStateSchema,
    tags=["games"],
    summary="Get game details",
    description="Get the current state of the game. User must be either X or O.",
)
def get_game(
    game_id: int = Path(..., description="Game id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns full game state for a given game."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(404, "Game not found.")

    not_player = (
        game.player_x_id != current_user.id
        and (game.player_o_id is not None and game.player_o_id != current_user.id)
    )
    if not_player:
        raise HTTPException(403, "You are not a player in this game.")
    return game_to_schema(game)


@app.get(
    "/users/{user_id}/games",
    response_model=UserGamesResponseSchema,
    tags=["games"],
    summary="Get user's game history",
    description="Fetch games (ongoing and finished) in which the given user has participated. "
                "Requires authentication and user must be self or an opponent.",
)
def get_user_games(
    user_id: int = Path(..., description="User id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns all games for this user (as X or O)."""
    if user_id != current_user.id:
        shared_game = db.query(Game).filter(
            ((Game.player_x_id == user_id) | (Game.player_o_id == user_id))
            & (
                (Game.player_x_id == current_user.id)
                | (Game.player_o_id == current_user.id)
            )
        ).first()
        if not shared_game:
            raise HTTPException(
                403,
                "You cannot view another user's game history."
            )
    games = db.query(Game).filter(
        (Game.player_x_id == user_id) | (Game.player_o_id == user_id)
    ).order_by(Game.created_at.desc()).all()
    result = [game_to_summary(g) for g in games]
    return UserGamesResponseSchema(games=result)

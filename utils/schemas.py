from pydantic import BaseModel
from typing import Dict
from pydantic.types import NonNegativeInt
from typing import Literal


class Roulette:
    red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    black = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    green = [0, 37]

    odd = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
    even = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]


class User(BaseModel):
    on_table: NonNegativeInt = 0
    at_play: NonNegativeInt = 0
    profit: int = 0
    daily: float = 0
    daily_count: NonNegativeInt = 0
    total_wagered: NonNegativeInt = 0


class Users(BaseModel):
    users: Dict[str, User]


class CrapsBet(BaseModel):
    wager: int
    line: Literal["pass", "dont_pass"]
    odds_bet: int = 0


class Craps(BaseModel):
    point: int = (0,)
    bets: Dict[str, CrapsBet]


class Steps(BaseModel):
    wager: NonNegativeInt
    multi: float
    next_multi: float

    def __init__(self, wager, multi: float = 1.0, next_multi: float = 1.0):
        super().__init__(wager=wager, multi=multi, next_multi=next_multi)


class RussianRoulette:
    wager: NonNegativeInt
    multi: float
    bulletcount: int

    def __init__(self, wager, multi: float = 1.0, bulletcount: int = 6):
        super().__init__(wager=wager, multi=multi, bulletcount=bulletcount)


class Games(BaseModel):
    craps: Craps
    steps: Dict[str, Steps] = {}
    russian_roulette: Dict[str, RussianRoulette] = {}

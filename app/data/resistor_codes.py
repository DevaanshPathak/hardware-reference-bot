from decimal import Decimal


DIGIT_CODES: dict[str, int] = {
    "black": 0,
    "brown": 1,
    "red": 2,
    "orange": 3,
    "yellow": 4,
    "green": 5,
    "blue": 6,
    "violet": 7,
    "gray": 8,
    "white": 9,
}

MULTIPLIERS: dict[str, Decimal] = {
    "black": Decimal("1"),
    "brown": Decimal("10"),
    "red": Decimal("100"),
    "orange": Decimal("1000"),
    "yellow": Decimal("10000"),
    "green": Decimal("100000"),
    "blue": Decimal("1000000"),
    "violet": Decimal("10000000"),
    "gray": Decimal("100000000"),
    "white": Decimal("1000000000"),
    "gold": Decimal("0.1"),
    "silver": Decimal("0.01"),
}

TOLERANCES: dict[str, Decimal] = {
    "brown": Decimal("1"),
    "red": Decimal("2"),
    "green": Decimal("0.5"),
    "blue": Decimal("0.25"),
    "violet": Decimal("0.1"),
    "gray": Decimal("0.05"),
    "gold": Decimal("5"),
    "silver": Decimal("10"),
}

ALIASES: dict[str, str] = {
    "grey": "gray",
    "purple": "violet",
}

SUPPORTED_COLORS = sorted(set(DIGIT_CODES) | set(MULTIPLIERS) | set(TOLERANCES) | set(ALIASES))

"""Travel MCP server — STARTER FILE.

Follow docs/02-build-a-server.md. Fill in each TODO; the finished version lives
in src/solution/travel_server.py if you get stuck.

Run it over stdio with:

    .venv/bin/python src/starter/travel_server.py
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Annotated, Literal

# TODO 1: In SDK v2 the high-level server class is MCPServer.
#         (In v1 this was `from mcp.server.fastmcp import FastMCP`.)
from mcp.server import MCPServer
from pydantic import BaseModel, Field

# TODO 2: Create the server. Give it a name and an `instructions` string telling
#         a model when to use it.
mcp = ...


# --------------------------------------------------------------------------
# Fake data — nothing to change here
# --------------------------------------------------------------------------

DESTINATIONS: dict[str, str] = {
    "amsterdam": "Canals, museums and very flat cycling.",
    "barcelona": "Beaches, Gaudí architecture and late dinners.",
    "reykjavik": "Geothermal pools, volcanoes and the northern lights.",
    "tokyo": "Neon, temples and the best train network on earth.",
    "cape town": "Table Mountain, penguins and vineyards.",
    "seattle": "Coffee, rain and mountains on a clear day.",
}

CONDITIONS = ["sunny", "cloudy", "rainy", "windy", "foggy", "snowy"]


def _seed(*parts: str) -> int:
    """Stable pseudo-random seed so demos are reproducible."""
    return int(hashlib.sha256("|".join(parts).lower().encode()).hexdigest(), 16)


def _known_city(city: str) -> str:
    key = city.strip().lower()
    if key not in DESTINATIONS:
        known = ", ".join(sorted(DESTINATIONS))
        raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")
    return key


# --------------------------------------------------------------------------
# Structured output models
# --------------------------------------------------------------------------


class Weather(BaseModel):
    """Current weather for a city."""

    city: str
    temperature_c: int = Field(description="Temperature in degrees Celsius.")
    condition: str = Field(description="Short human-readable sky condition.")
    humidity_pct: int = Field(ge=0, le=100)


class ForecastDay(BaseModel):
    """Weather for a single future day."""

    day: str = Field(description="ISO date, e.g. 2026-08-09.")
    high_c: int
    low_c: int
    condition: str


# TODO 6a: Define a `Flight` model with these fields:
#          flight_number: str, origin: str, destination: str,
#          departs: str, duration_hours: float, price_eur: int


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------


# TODO 3: Turn this into a tool with the @mcp.tool() decorator.
#         The docstring becomes the description the model reads — so write it
#         for the model, not for yourself.
def list_destinations() -> list[str]:
    """List every city this travel service knows about."""
    return sorted(DESTINATIONS)


# TODO 4: Make this a tool too. Notice the return type is a Pydantic model:
#         that is what gives the tool a structured `outputSchema`.
def get_weather(
    city: Annotated[str, Field(description='City name, e.g. "Amsterdam".')],
) -> Weather:
    """Get today's weather for a city. Only supported destinations work."""
    key = _known_city(city)
    seed = _seed("weather", key, date.today().isoformat())
    return Weather(
        city=key.title(),
        temperature_c=(seed % 31) - 5,
        condition=CONDITIONS[seed % len(CONDITIONS)],
        humidity_pct=40 + (seed % 55),
    )


# TODO 5: Make this a tool. The Annotated/Field constraints below become real
#         JSON Schema validation — try calling it with days=99 afterwards.
def get_forecast(
    city: Annotated[str, Field(description='City name, e.g. "Tokyo".')],
    days: Annotated[int, Field(ge=1, le=7, description="Days ahead to forecast.")] = 3,
    units: Annotated[
        Literal["celsius", "fahrenheit"], Field(description="Temperature units.")
    ] = "celsius",
) -> list[ForecastDay]:
    """Get a multi-day weather forecast for a city."""
    key = _known_city(city)
    forecast: list[ForecastDay] = []
    for offset in range(1, days + 1):
        day = date.today() + timedelta(days=offset)
        seed = _seed("forecast", key, day.isoformat())
        low_c = (seed % 21) - 8
        high_c = low_c + 3 + (seed % 9)
        if units == "fahrenheit":
            low_c = round(low_c * 9 / 5 + 32)
            high_c = round(high_c * 9 / 5 + 32)
        forecast.append(
            ForecastDay(
                day=day.isoformat(),
                high_c=high_c,
                low_c=low_c,
                condition=CONDITIONS[seed % len(CONDITIONS)],
            )
        )
    return forecast


# TODO 6b: Write `search_flights` yourself, from scratch.
#          - decorate it with @mcp.tool()
#          - parameters: origin, destination, and max_results (1..5, default 3)
#          - raise ValueError if origin == destination
#          - return a list[Flight]; use _seed("flight", origin, dest, str(i))
#            to make up deterministic flight data
#          - remember to describe each parameter with Annotated[..., Field(...)]


# --------------------------------------------------------------------------
# Resource — application-controlled context, not called by the model
# --------------------------------------------------------------------------


# TODO 7: Expose the catalogue as a resource at the URI "travel://destinations"
#         using @mcp.resource("travel://destinations").
def destinations_catalog() -> str:
    """The full destination catalogue as human-readable text."""
    lines = [f"- {city.title()}: {blurb}" for city, blurb in sorted(DESTINATIONS.items())]
    return "Destinations this travel service covers:\n" + "\n".join(lines)


# --------------------------------------------------------------------------
# Prompt — a reusable, user-selected workflow
# --------------------------------------------------------------------------


# TODO 8: Turn this into a prompt with @mcp.prompt().
def plan_a_trip(city: str, nights: int = 3) -> str:
    """Draft a short trip plan for a city."""
    return (
        f"Plan a {nights}-night trip to {city}.\n\n"
        "Steps:\n"
        f"1. Check the weather forecast for {city} for the next {nights} days.\n"
        f"2. Find flights from Amsterdam to {city}.\n"
        "3. Recommend what to pack based on the forecast, and suggest an itinerary.\n"
    )


if __name__ == "__main__":
    # TODO 9: Run the server over stdio.
    ...

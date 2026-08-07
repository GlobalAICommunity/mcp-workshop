"""Travel MCP server — the completed reference implementation.

Built with the official MCP Python SDK v2 (`mcp` >= 2.0), which speaks the
2026-07-28 revision of the Model Context Protocol.

Note the import: in SDK v1 the high-level server class was
`from mcp.server.fastmcp import FastMCP`. In v2 it is `MCPServer`, and the old
import path was removed rather than deprecated.

All data here is fake and generated deterministically from the city name, so the
server needs no network access and always gives the same answer for the same
question — which makes it a good thing to demo in front of a room.

Run it directly to serve over stdio:

    python src/solution/travel_server.py
"""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Annotated, Literal

from mcp.server import MCPServer
from pydantic import BaseModel, Field

mcp = MCPServer(
    "travel",
    instructions=(
        "A fake travel assistant backend. Use get_weather and get_forecast for "
        "weather questions, search_flights to find flights between two cities, "
        "and list_destinations to see which cities are supported."
    ),
)

# --------------------------------------------------------------------------
# Fake data
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
    """Stable pseudo-random seed derived from the inputs.

    Using a hash rather than `random` keeps results reproducible across runs and
    machines, which matters when you are demoing live.
    """
    joined = "|".join(parts).lower()
    return int(hashlib.sha256(joined.encode()).hexdigest(), 16)


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


class Flight(BaseModel):
    """A bookable (and entirely imaginary) flight."""

    flight_number: str
    origin: str
    destination: str
    departs: str = Field(description="Local departure time, 24h HH:MM.")
    duration_hours: float
    price_eur: int


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------


@mcp.tool()
def list_destinations() -> list[str]:
    """List every city this travel service knows about."""
    return sorted(DESTINATIONS)


@mcp.tool()
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


@mcp.tool()
def get_forecast(
    city: Annotated[str, Field(description='City name, e.g. "Tokyo".')],
    days: Annotated[int, Field(ge=1, le=7, description="Days ahead to forecast.")] = 3,
    units: Annotated[
        Literal["celsius", "fahrenheit"], Field(description="Temperature units.")
    ] = "celsius",
) -> list[ForecastDay]:
    """Get a multi-day weather forecast for a city."""
    key = _known_city(city)
    if not 1 <= days <= 7:
        raise ValueError("days must be between 1 and 7")

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


@mcp.tool()
def search_flights(
    origin: Annotated[str, Field(description='City to depart from, e.g. "Amsterdam".')],
    destination: Annotated[str, Field(description='City to fly to, e.g. "Barcelona".')],
    max_results: Annotated[
        int, Field(ge=1, le=5, description="Maximum number of flights to return.")
    ] = 3,
) -> list[Flight]:
    """Search for flights between two cities."""
    origin_key = _known_city(origin)
    dest_key = _known_city(destination)
    if origin_key == dest_key:
        raise ValueError("origin and destination must be different cities")
    if not 1 <= max_results <= 5:
        raise ValueError("max_results must be between 1 and 5")

    flights: list[Flight] = []
    for index in range(max_results):
        seed = _seed("flight", origin_key, dest_key, str(index))
        flights.append(
            Flight(
                flight_number=f"{'GA'} {100 + (seed % 800)}",
                origin=origin_key.title(),
                destination=dest_key.title(),
                departs=f"{6 + (seed % 15):02d}:{(seed % 4) * 15:02d}",
                duration_hours=round(1.5 + (seed % 90) / 10, 1),
                price_eur=59 + (seed % 440),
            )
        )
    return sorted(flights, key=lambda flight: flight.departs)


# --------------------------------------------------------------------------
# Resource — application-controlled context, not called by the model
# --------------------------------------------------------------------------


@mcp.resource("travel://destinations")
def destinations_catalog() -> str:
    """The full destination catalogue as human-readable text."""
    lines = [f"- {city.title()}: {blurb}" for city, blurb in sorted(DESTINATIONS.items())]
    return "Destinations this travel service covers:\n" + "\n".join(lines)


# --------------------------------------------------------------------------
# Prompt — a reusable, user-selected workflow
# --------------------------------------------------------------------------


@mcp.prompt()
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
    mcp.run(transport="stdio")

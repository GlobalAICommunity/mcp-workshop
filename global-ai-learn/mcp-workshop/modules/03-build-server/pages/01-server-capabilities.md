---
id: server-capabilities
title: Tools, resources, prompts, and errors
order: 1
estimatedMinutes: 45
---

You will create `src/starter/travel_server.py` from an empty file. Do not copy the
solution. Each step appends one complete section, and each checkpoint runs the
file you are building.

## Step 1: Start with an empty file

From the repository root, remove any starter content:

```bash
: > src/starter/travel_server.py
```

Add the imports, server object, and small in-memory data set:

```python
from __future__ import annotations

import hashlib
from datetime import date, timedelta
from typing import Annotated, Literal

from mcp.server import MCPServer
from pydantic import BaseModel, Field

mcp = MCPServer(
    "travel",
    instructions=(
        "A fake travel assistant backend. Use weather and flight tools for "
        "travel questions, and list_destinations when a city is uncertain."
    ),
)

DESTINATIONS = {
    "amsterdam": "Canals, museums and cycling.",
    "barcelona": "Beaches, architecture and late dinners.",
    "reykjavik": "Geothermal pools and northern lights.",
    "tokyo": "Temples, neon and an excellent train network.",
}

CONDITIONS = ["sunny", "cloudy", "rainy", "windy", "foggy", "snowy"]
```

Compile the file after the first addition:

```bash
.venv/bin/python -m py_compile src/starter/travel_server.py
```

## Step 2: Add deterministic helpers

Append these functions below the data. They validate city names and generate
repeatable fake values without a network API:

```python
def _seed(*parts: str) -> int:
    joined = "|".join(parts).lower()
    return int(hashlib.sha256(joined.encode()).hexdigest(), 16)


def _known_city(city: str) -> str:
    key = city.strip().lower()
    if key not in DESTINATIONS:
        known = ", ".join(sorted(DESTINATIONS))
        raise ValueError(f"Unknown city {city!r}. Known cities are: {known}.")
    return key
```

The error is written for a model, not a stack-trace reader. It explains what was
invalid and gives enough information to correct the next call.

## Step 3: Define structured result models

Append the three models used by the tools:

```python
class Weather(BaseModel):
    city: str
    temperature_c: int = Field(description="Temperature in degrees Celsius.")
    condition: str
    humidity_pct: int = Field(ge=0, le=100)


class ForecastDay(BaseModel):
    day: str = Field(description="ISO date, for example 2026-08-09.")
    high_c: int
    low_c: int
    condition: str


class Flight(BaseModel):
    flight_number: str
    origin: str
    destination: str
    departs: str = Field(description="Local time in 24-hour HH:MM format.")
    price_eur: int
```

Returning Pydantic models gives the tool an output schema and gives non-model
consumers structured content without requiring them to parse prose.

## Step 4: Add destination and weather tools

Append the first two tools:

```python
@mcp.tool()
def list_destinations() -> list[str]:
    """List every city this travel service supports."""
    return sorted(DESTINATIONS)


@mcp.tool()
def get_weather(
    city: Annotated[str, Field(description='City name, e.g. "Amsterdam".')],
) -> Weather:
    """Get today's weather for a supported city."""
    key = _known_city(city)
    seed = _seed("weather", key, date.today().isoformat())
    return Weather(
        city=key.title(),
        temperature_c=(seed % 31) - 5,
        condition=CONDITIONS[seed % len(CONDITIONS)],
        humidity_pct=40 + (seed % 55),
    )
```

The decorator uses the function name as the tool name, the docstring as its
model-facing description, and annotations as its input schema. Use `Annotated`
and `Field` for parameter descriptions because an `Args:` docstring section does
not create them in `mcp` 2.0.

## Step 5: Add the forecast tool

Append a tool with constraints and defaults:

```python
@mcp.tool()
def get_forecast(
    city: Annotated[str, Field(description='City name, e.g. "Tokyo".')],
    days: Annotated[int, Field(ge=1, le=7)] = 3,
    units: Literal["celsius", "fahrenheit"] = "celsius",
) -> list[ForecastDay]:
    """Get a multi-day weather forecast for a supported city."""
    key = _known_city(city)
    forecast = []
    for offset in range(1, days + 1):
        current_day = date.today() + timedelta(days=offset)
        seed = _seed("forecast", key, current_day.isoformat())
        low = (seed % 21) - 8
        high = low + 3 + (seed % 9)
        if units == "fahrenheit":
            low = round(low * 9 / 5 + 32)
            high = round(high * 9 / 5 + 32)
        forecast.append(
            ForecastDay(
                day=current_day.isoformat(),
                high_c=high,
                low_c=low,
                condition=CONDITIONS[seed % len(CONDITIONS)],
            )
        )
    return forecast
```

The schema exposes the range and enum to the model. Defaults let it omit details
it does not care about. Validation still belongs in production code because a
schema is guidance, not authorization.

## Step 6: Add the flight tool

Append the fourth and final tool:

```python
@mcp.tool()
def search_flights(
    origin: Annotated[str, Field(description="City to depart from.")],
    destination: Annotated[str, Field(description="City to fly to.")],
    max_results: Annotated[int, Field(ge=1, le=5)] = 3,
) -> list[Flight]:
    """Search for flights between two supported cities."""
    origin_key = _known_city(origin)
    destination_key = _known_city(destination)
    if origin_key == destination_key:
        raise ValueError("origin and destination must be different cities")

    flights = []
    for index in range(max_results):
        seed = _seed("flight", origin_key, destination_key, str(index))
        flights.append(
            Flight(
                flight_number=f"GA {100 + (seed % 800)}",
                origin=origin_key.title(),
                destination=destination_key.title(),
                departs=f"{6 + (seed % 15):02d}:{(seed % 4) * 15:02d}",
                price_eur=59 + (seed % 440),
            )
        )
    return sorted(flights, key=lambda flight: flight.departs)
```

## Step 7: Add a resource and prompt

Append application-controlled reference data and a user-selected workflow:

```python
@mcp.resource("travel://destinations")
def destinations_catalog() -> str:
    """Return the complete destination catalogue."""
    lines = [
        f"- {city.title()}: {description}"
        for city, description in sorted(DESTINATIONS.items())
    ]
    return "Destinations this service covers:\n" + "\n".join(lines)


@mcp.prompt()
def plan_a_trip(city: str, nights: int = 3) -> str:
    """Draft a reusable trip-planning workflow."""
    return (
        f"Plan a {nights}-night trip to {city}.\n"
        f"1. Check the {nights}-day forecast for {city}.\n"
        f"2. Find flights from Amsterdam to {city}.\n"
        "3. Recommend what to pack and suggest an itinerary."
    )
```

## Step 8: Make the file executable

Append the entry point last:

```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Compile the complete file, then inspect the server you wrote:

```bash
.venv/bin/python -m py_compile src/starter/travel_server.py
MCP_SERVER_FILE=src/starter/travel_server.py ./scripts/raw_jsonrpc.sh tools/list
```

Your finished file should expose four tools, one resource, and one prompt. The
environment variable makes the helper launch your file instead of the completed
reference implementation.
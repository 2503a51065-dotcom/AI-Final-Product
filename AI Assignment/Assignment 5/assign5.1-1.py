"""Fetch current weather without storing credentials in source code."""

import argparse
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str, api_key: str | None = None) -> dict[str, Any]:
	"""Return current weather for ``city`` from OpenWeatherMap.

	The API key should normally be provided through the
	``OPENWEATHER_API_KEY`` environment variable rather than source code.
	"""
	key = api_key or os.environ.get("OPENWEATHER_API_KEY")
	if not key:
		raise RuntimeError(
			"Missing API key. Set the OPENWEATHER_API_KEY environment variable."
		)

	query = urlencode({"q": city, "appid": key, "units": "metric"})
	request = Request(
		f"{API_URL}?{query}",
		headers={"Accept": "application/json", "User-Agent": "assign5-weather/1.0"},
	)

	try:
		with urlopen(request, timeout=10) as response:
			return json.load(response)
	except HTTPError as error:
		if error.code == 401:
			raise RuntimeError(
				"Invalid or inactive API key. Check the key in your "
				"OpenWeatherMap dashboard and set OPENWEATHER_API_KEY in "
				"this PowerShell session. New keys can take a few minutes to activate."
			) from error
		raise RuntimeError(
			f"Weather service returned HTTP {error.code} for city {city!r}."
		) from error
	except URLError as error:
		raise RuntimeError("Could not connect to the weather service.") from error


def main() -> None:
	parser = argparse.ArgumentParser(description="Fetch current weather for a city.")
	parser.add_argument(
		"city", nargs="?", help="City name, optionally with country code"
	)
	args = parser.parse_args()
	city = args.city or input("Enter city: ").strip()
	if not city:
		parser.error("A city name is required.")

	try:
		weather = fetch_weather(city)
	except RuntimeError as error:
		parser.error(str(error))

	print(json.dumps(weather, indent=2))


if __name__ == "__main__":
	main()

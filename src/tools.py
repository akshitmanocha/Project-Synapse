"""
TOOLS MODULE SPEC (Simulated)

Purpose:
- Provide a thin, test-friendly layer of simulated external tools the agent can call.
- Each tool returns hardcoded or randomized stub data and prints side effects where relevant.

Contracts (inputs -> outputs / effects):
- check_traffic(route: str) -> Literal['heavy','moderate','light']
  Returns a random traffic level for the given route.

- get_merchant_status(merchant_id: str | int) -> dict
  Example: { 'status': 'open', 'prep_time_minutes': 40 }
  Returns a simulated status and prep time.

- notify_customer(customer_id: str | int, message: str) -> bool
  Prints a notification message to stdout and returns True.

- re_route_driver(driver_id: str | int, new_task_id: str | int) -> bool
  Prints a re-routing action to stdout and returns True.

- get_driver_location(driver_id: str | int) -> dict
  Example: { 'lat': 37.7749, 'lon': -122.4194, 'accuracy_m': 25 }
  Returns a simulated geo-position for a driver.

- estimate_eta(route: str, traffic_status: str | None = None) -> int
  Returns a simulated ETA in minutes based on traffic.

- get_order_status(order_id: str | int) -> dict
  Example: { 'status': 'preparing', 'ready_in_minutes': 15 }
  Returns a simulated order status snapshot.

- log_event(event: str, metadata: dict | None = None) -> None
  Prints a structured log line for observability during simulation.

Notes:
- Keep tools deterministic enough for tests when needed; allow seeding via random if desired.
- Replace implementations with real integrations later (APIs/DBs/SDKs). Keep function signatures stable.
"""

from __future__ import annotations

import random
import time
from typing import Literal, Optional

__all__ = [
	"check_traffic",
	"get_merchant_status",
	"notify_customer",
	"re_route_driver",
	"get_driver_location",
	"estimate_eta",
	"get_order_status",
	"log_event",
]


def check_traffic(route: str) -> Literal["heavy", "moderate", "light"]:
	"""Return a random traffic status for the provided route.

	Args:
		route: A route identifier or human-readable route description.

	Returns:
		One of: 'heavy', 'moderate', 'light'.

	Note:
		Purely simulated using random choice.
	"""
	pass


def get_merchant_status(merchant_id: str | int) -> dict:
	"""Return a simulated merchant status and prep time.

	Args:
		merchant_id: Unique identifier of the merchant.

	Returns:
		Dict with keys: 'status' (str), 'prep_time_minutes' (int), 'last_updated' (int epoch seconds).

	Example:
		{ 'status': 'open', 'prep_time_minutes': 40 }
	"""
	pass


def notify_customer(customer_id: str | int, message: str) -> bool:
	"""Simulate sending a notification to a customer via stdout.

	Args:
		customer_id: Customer identifier.
		message: Content of the notification.

	Returns:
		True on (simulated) success.
	"""
	pass

def re_route_driver(driver_id: str | int, new_task_id: str | int) -> bool:
	"""Simulate re-routing a driver to a new task.

	Args:
		driver_id: Driver identifier.
		new_task_id: The new task or delivery identifier.

	Returns:
		True on (simulated) success.
	"""
	pass


def get_driver_location(driver_id: str | int) -> dict:
	"""Return a simulated driver location.

	For demo purposes, returns a coordinate roughly around San Francisco.

	Args:
		driver_id: Driver identifier.

	Returns:
		Dict with 'lat', 'lon', 'accuracy_m'.
	"""
	pass

def estimate_eta(route: str, traffic_status: Optional[str] = None) -> int:
	"""Estimate minutes to arrival based on (simulated) traffic.

	Args:
		route: Route identifier or description.
		traffic_status: Optional precomputed traffic status. If None, will call check_traffic().

	Returns:
		ETA in whole minutes.
	"""
	pass


def get_order_status(order_id: str | int) -> dict:
	"""Return a simulated order status snapshot.

	Args:
		order_id: Order identifier.

	Returns:
		Dict with 'status' and a related field depending on the phase.
	"""
	pass


def log_event(event: str, metadata: Optional[dict] = None) -> None:
	"""Print a structured simulation log line.

	Args:
		event: Event name/type.
		metadata: Optional dict with extra context.
	"""
	pass


if __name__ == "__main__":
	# Lightweight smoke test when run directly
	print("-- tools.py smoke test --")
	r = "Route-42"
	t = check_traffic(r)
	print("traffic:", t)
	print("eta:", estimate_eta(r, t))
	print("merchant:", get_merchant_status("m-123"))
	notify_customer("c-9", "Your order is on the way.")
	re_route_driver("d-1", "task-9")
	print("driver_loc:", get_driver_location("d-1"))
	print("order:", get_order_status("o-77"))
	log_event("DEMO_RUN", {"ok": True})

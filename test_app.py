import json
import pytest
import app


@pytest.fixture
def client(tmp_path):
    # Create a temporary bookings file
    temp_bookings = tmp_path / "bookings.json"

    temp_bookings.write_text(json.dumps([
        {
            "id": 1,
            "equipment_id": 1,
            "equipment_name": "Canon DSLR Camera",
            "customer": "Existing Customer",
            "from_date": "2026-01-10",
            "to_date": "2026-01-15",
            "total": 9000.0,
            "status": "confirmed"
        }
    ]))

    # Use temporary bookings file
    app.BOOKINGS_FILE = str(temp_bookings)
    app.app.config["TESTING"] = True

    with app.app.test_client() as client:
        yield client


# ---------------------------------------------------
# 1. Double-booking bug
# ---------------------------------------------------

def test_allow_non_overlapping_booking(client):
    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 1,
            "customer": "Bob",
            "from_date": "2026-01-16",
            "to_date": "2026-01-18",
        },
    )

    assert response.status_code == 201

def test_cannot_book_equipment_with_overlapping_dates(client):
    response = client.post("/api/bookings", json={
        "equipment_id": 1,
        "customer": "New Customer",
        "from_date": "2026-01-08",
        "to_date": "2026-01-20"
    })

    # Should reject because Canon DSLR Camera is already booked Jan 10-15
    assert response.status_code == 409

    data = response.get_json()
    assert "already booked" in data["error"]

def test_existing_canon_booking_prevents_new_booking(client):
    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 1,
            "customer": "Test Customer",
            "from_date": "2026-01-12",
            "to_date": "2026-01-14",
        },
    )

    assert response.status_code == 409
    assert "already booked" in response.get_json()["error"]

def test_same_day_booking_overlap(client):
    """
    Same-day overlap should fail because dates are inclusive.
    Existing booking ends Jan 15, so booking Jan 15 should conflict.
    """

    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 1,
            "customer": "Same Day Customer",
            "from_date": "2026-01-15",
            "to_date": "2026-01-15",
        },
    )

    assert response.status_code == 409


# ---------------------------------------------------
# 2. Inclusive rental billing
# ---------------------------------------------------

def test_same_day_rental_cost(client):
    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 2,
            "customer": "John",
            "from_date": "2024-02-01",
            "to_date": "2024-02-01",
        },
    )

    assert response.status_code == 201

    booking = response.get_json()

    # 1 day x 480
    assert booking["total"] == 480.0


def test_three_day_rental_cost(client):
    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 2,
            "customer": "John",
            "from_date": "2024-02-01",
            "to_date": "2024-02-03",
        },
    )

    assert response.status_code == 201

    booking = response.get_json()

    # Feb 1, Feb 2, Feb 3 = 3 days
    assert booking["total"] == 1440.0


# ---------------------------------------------------
# 3. Maintenance equipment
# ---------------------------------------------------

def test_cannot_book_maintenance_equipment(client):
    response = client.post(
        "/api/bookings",
        json={
            "equipment_id": 3,
            "customer": "Jane",
            "from_date": "2024-03-01",
            "to_date": "2024-03-02",
        },
    )

    assert response.status_code == 400
    assert "not available" in response.get_json()["error"]


def test_maintenance_not_in_availability(client):
    response = client.get(
        "/api/availability?from=2024-03-01&to=2024-03-02"
    )

    assert response.status_code == 200

    equipment = response.get_json()

    ids = [item["id"] for item in equipment]

    assert 3 not in ids
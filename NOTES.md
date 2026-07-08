# NOTES

## 1. Fixes made

- **Double-booking bug:** I replaced the overlap check with a full range-overlap test so any intersecting date range is rejected, including cases where a new booking fully contains an existing one.
- **PHP 0.00 / short-rental bug:** The rental total was being calculated with an exclusive day count, which could produce 0 days for same-day rentals and undercharge short bookings. I changed the calculation to count both the start and end dates inclusively.
- **Maintenance equipment rule:** Equipment marked as `maintenance` is now blocked from booking and excluded from the available equipment list, so it can no longer be selected or shown as rentable.
- **Frontend price bug:** The booking total now recalculates correctly when either the start date or end date changes, so the displayed price stays in sync with the selected dates.

## 2. Failure example

Existing booking: **Jan 10–15**

The original code incorrectly allowed a booking for **Jan 8–18** because it did not catch the case where the new booking fully overlapped the existing one. After the fix, this booking is correctly rejected.

## 3. AI use

I used AI to help write tests and debug the code, especially around the date-overlap and pricing logic. I verified the output by checking the implementation directly, running the affected scenarios, and confirming the fixes behaved correctly after the changes.
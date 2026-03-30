# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
My initial design separated the system into four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- The `Task` handled the lowest-level data (description, time, duration).
- The `Pet` aggregated tasks.
- The `Owner` aggregated pets.
- The `Scheduler` acted as a decoupled "Service" class that took in an `Owner` and applied algorithms (sorting, filtering) to the data structure without modifying the core data classes.

**b. Design changes**
During implementation, I used Agent mode to help build a Data Persistence layer (Stretch Goal 2). I initially thought about putting the JSON saving/loading logic in the `Scheduler`, but AI suggested moving `save_to_json` and `load_from_json` directly to the `Owner` class. This was a great design change because it adheres better to Single Responsibility—the Owner represents the entire state tree of data, while the Scheduler should only be responsible for *analyzing* that data.

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**
My scheduler considers three primary constraints:

1. **Completion Status:** Completed tasks are hidden from the upcoming view.
1. **Priority:** (Stretch Goal 3) Tasks are grouped by High, Medium, and Low.
1. **Time:** Tasks are sorted chronologically within their priority buckets.

I decided priority mattered most. If a pet needs medication at 10:00 AM (High) but has a walk scheduled at 9:00 AM (Low), the app brings the medication to the top of the list so the owner doesn't miss it.

**b. Tradeoffs**
To keep the conflict detection lightweight, I made a specific tradeoff: the `check_conflicts` method warns about overlapping times, but *does not actually prevent the user from creating the task*. This is reasonable for this scenario because pet owners often multitask (e.g., throwing a ball for the dog while brushing the cat). Strict blocking would frustrate the user; a warning gives them the agency to decide.

## 3. AI Collaboration

**a. How you used AI**
I used VS Code Copilot heavily for scaffolding the `dataclasses`, writing the Pytest boilerplate, and handling the tricky `datetime` JSON serialization. Inline Chat was incredibly helpful for writing the lambda function used to sort tasks by both a dictionary mapping (Priority) and a datetime object.

**b. Judgment and verification**
When generating the conflict detection algorithm, Copilot initially suggested an O(N2) algorithm that checked every task against every other task in a nested loop. I rejected this suggestion to keep the system clean and efficient. Instead, I modified it by first sorting the tasks chronologically, which allowed me to do a single pass (O(N)) comparing just `task[i]` to `task[i+1]`. I verified this logic by writing a specific `pytest` function for overlapping durations.

## 4. Testing and Verification

**a. What you tested**
I tested 5 core behaviors in `tests/test_pawpal.py`:

1. Task state manipulation (`mark_complete`).
1. Data relationships (adding tasks to pets).
1. Sorting logic (verifying Priority overrides Time).
1. Recurrence logic (verifying exactly 1 day is added to `timedelta`).
1. Overlap detection.

These were vital because they represent the core "intelligence" of the app. If the UI breaks, it's annoying, but if the scheduler gives the wrong medication time, it's dangerous for the pet.

**b. Confidence**
I am highly confident (5/5 stars) in the scheduler because of the CLI-first testing approach. If I had more time, I would test edge cases regarding timezone shifts (e.g., Daylight Savings Time breaking the 24-hour timedelta recurrence) and JSON serialization of corrupted files.

## 5. Reflection

**a. What went well**
I am most satisfied with the UI and Backend integration. Because the `pawpal_system.py` logic was so cleanly separated, wiring it up to Streamlit's `st.session_state` and creating dynamic buttons and color-coded priority displays was seamless.

**b. What you would improve**
If I had another iteration, I would improve the Task Recurrence. Right now, marking a task complete instantly spawns the next one. A better design would be a background cron-job or UI initialization check that generates the entire week's schedule in advance so the user can see their future calendar.

**c. Key takeaway**
The most important thing I learned as a "lead architect" is that AI is fantastic at writing the granular syntax (like `datetime.isoformat()`), but a human must dictate the architecture. Deciding where functions live (Data class vs. Service class) and choosing whether algorithms should strictly block users vs. gently warn them are human product decisions that the AI cannot make for you.

## 6. Prompt Comparison (Stretch Goal 5)

**Task:** Rescheduling weekly tasks logic.

- **Model A (OpenAI):** Suggested a complex decorator pattern to wrap the completion method, utilizing `dateutil.relativedelta`.
- **Model B (Claude/Gemini):** Suggested a much more "Pythonic" approach directly modifying the dataclass instance, returning a cloned instance using native `datetime.timedelta(weeks=1)`.

**Verdict:** I chose Model B's approach. While Model A's decorator pattern was conceptually neat, it introduced unnecessary overhead for a simple pet scheduler. The simpler `timedelta` approach was far more readable and easier to test in `pytest`.
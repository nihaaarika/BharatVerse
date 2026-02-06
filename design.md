# Goal Detector — Project Doc (Day 1–2)

## Core Problem + Value Proposition
Many people (students, career changers, early-career professionals) want to “get better” or “pick a direction,” but struggle to translate vague interests into concrete, realistic goals. The pain point is decision paralysis: too many options, unclear next steps, and low confidence that a chosen goal fits their interests and constraints. **Goal Detector** solves this by asking a short, friendly questionnaire and turning answers into a small set of personalized, actionable goals (with reasons and first steps). The result is faster clarity and a starter plan—making learning and planning more accessible and less overwhelming.

## Target Users
- Students exploring majors/careers
- Career changers seeking a new direction
- Self-learners who feel stuck or scattered
- Busy adults who need time-bounded, realistic goals

## One-Paragraph Pitch
Goal Detector uses AI-inspired matching to analyze your signup questionnaire and suggest personalized goals based on your interests, constraints, and preferred learning style. Instead of a generic list, it returns a short set of goals with a clear “why this fits you” explanation and first steps—helping you move from uncertainty to an actionable plan in minutes.

## Key Features (Essentials First)
### MVP (must-have)
- Simple signup (name/email optional) → questionnaire → results
- 8–10 short questions (mix of multiple choice + short text)
- Theme extraction (identify user interests + constraints)
- 3–5 ranked goal suggestions
- Each goal includes: short explanation + 2–4 first steps
- Fallback when answers are vague (generic starter goals)

### Nice-to-have (after MVP)
- “Why this goal fits” expanded explanation
- Resource links per goal (courses, communities, templates)
- Let users save/export results (download JSON)
- Ask 1 follow-up question when confidence is low
- Feedback buttons (“relevant” / “not relevant”) to iterate quickly

## Research + Inspiration (What to Borrow)
- **Career quizzes** (LinkedIn-style): short, high-signal questions; quick results
- **Personality tests** (MBTI-style): engaging tone; “you might like…” framing
- **Recommendation interfaces**: card layout; strong summaries; consistent formatting

## Sample Questionnaire (10 Questions)
1) What best describes you right now? (student / employed / career change / other)
2) What are you most interested in? (multi-select: tech, design, business, health, finance, community, creative, other)
3) Pick 2–3 topics you enjoy most (free text)
4) What outcome do you want in the next 3 months? (skill / project / habit / job prep / explore)
5) Time available per week? (0–2, 3–5, 6–10, 10+ hours)
6) Your preferred style? (hands-on project / structured course / reading / coaching)
7) What constraints matter most? (money, time, device, schedule, anxiety, none)
8) What motivates you? (curiosity / career impact / health / social / creativity)
9) Do you want community involvement? (solo / small group / public community)
10) Any “hard no’s”? (free text; e.g., “no public speaking”)

## Example Goal Themes + Goal Outputs (Samples)
### Themes
- Tech (coding, data, automation)
- Health (fitness, nutrition, sleep)
- Finance (budgeting, investing basics)
- Career (portfolio, interviewing, networking)
- Community (volunteering, local groups)

### Example Goals
- “Build a small automation script you’ll actually use weekly”
- “Create a 4-week beginner strength routine and track progress”
- “Set up a simple budget and automate bill tracking”
- “Ship a portfolio project and write a short case study”
- “Join one community group and attend 2 events this month”

## Success Metrics (MVP)
- **Relevance**: user rates at least 1 goal as “highly relevant”
- **Clarity**: user can explain why a goal was suggested (from the UI)
- **Completion intent**: user picks at least 1 goal to try next week
- **Time-to-value**: user reaches results in under ~2 minutes

## Rough Timeline
- Day 1: pitch + features + sample questions/goals + repo skeleton
- Day 2: user journey + wireframes + AI logic flow + Streamlit MVP

---

## Phase 2 (Day 2): Structure + UX
### User Journey Map
1) Welcome / signup (name optional)
2) Questionnaire (short, engaging; progress indicator)
3) “Processing” state (short loading text)
4) Results page (ranked goal cards)
5) User picks a goal + downloads plan (optional)

### Questionnaire Design Notes
- 2–3 basics (context, time, constraints)
- 3–5 interests (mix of multi-select + open text)
- 1–2 aspirations (time horizon + motivation)
- Neutral phrasing (“What sounds appealing?”) to reduce bias

### AI Logic Flow (No Tech Details)
1) Collect responses
2) Detect themes (interests + constraints + motivation)
3) Match themes to goal categories (predefined templates)
4) Rank 3–5 goals by relevance and feasibility
5) Add value: “why it fits” + first steps + resources
6) Fallback: if confidence is low, provide starter goals and ask follow-up

### Wireframe (Text)
- **Welcome**: title + “Start” button
- **Questions**: one form, grouped sections; progress indicator
- **Processing**: spinner + “Finding goals that match your interests…”
- **Results**: cards with title, why, timeframe, steps, resources; “Try this goal” button

### Ethics + Edge Cases
- Privacy: don’t store personal data for MVP; keep everything in-session
- Inclusivity: avoid stereotyping; let users choose categories; allow “other”
- Safety: avoid medical/financial advice language; “educational suggestions” disclaimer
- Low-signal inputs: show generic goals + ask one clarifying question


from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Goal:
    id: str
    title: str
    theme: str
    timeframe_weeks: int
    difficulty: str
    tags: list[str]
    description: str
    first_steps: list[str]
    resources: list[dict[str, str]]


def load_goals(path: str | Path = "goals.json") -> list[Goal]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    goals: list[Goal] = []
    for item in data.get("goals", []):
        goals.append(
            Goal(
                id=str(item["id"]),
                title=str(item["title"]),
                theme=str(item.get("theme", "other")),
                timeframe_weeks=int(item.get("timeframe_weeks", 4)),
                difficulty=str(item.get("difficulty", "beginner")),
                tags=[str(t).lower() for t in item.get("tags", [])],
                description=str(item.get("description", "")),
                first_steps=[str(s) for s in item.get("first_steps", [])],
                resources=[dict(r) for r in item.get("resources", [])],
            )
        )
    return goals


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple, set)):
        return " ".join(str(v) for v in value)
    return str(value).strip()


_TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


THEME_KEYWORDS: dict[str, set[str]] = {
    "tech": {
        "code",
        "coding",
        "python",
        "javascript",
        "data",
        "automation",
        "ai",
        "ml",
        "machine",
        "software",
        "app",
        "web",
    },
    "health": {"fitness", "workout", "gym", "run", "running", "sleep", "nutrition", "diet", "strength"},
    "finance": {"budget", "budgeting", "money", "saving", "savings", "invest", "investing", "debt"},
    "career": {"job", "career", "interview", "resume", "portfolio", "promotion", "network", "networking"},
    "community": {"volunteer", "community", "meetup", "friends", "social", "group", "club"},
    "creative": {"write", "writing", "music", "art", "design", "draw", "painting", "photography"},
}


def extract_themes(responses: dict[str, Any], max_themes: int = 3) -> list[str]:
    text_blob = " ".join(normalize_text(v) for v in responses.values())
    tokens = tokenize(text_blob)
    if not tokens:
        return []

    scores: dict[str, int] = {theme: 0 for theme in THEME_KEYWORDS}
    token_set = set(tokens)
    for theme, keywords in THEME_KEYWORDS.items():
        scores[theme] += len(token_set.intersection(keywords))

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    themes = [t for t, score in ranked if score > 0][:max_themes]
    return themes


def score_goal(goal: Goal, themes: Iterable[str], responses: dict[str, Any]) -> float:
    themes_set = {t.lower() for t in themes}
    tags_set = set(goal.tags)

    text_blob = " ".join(normalize_text(v) for v in responses.values()).lower()
    tokens = set(tokenize(text_blob))

    score = 0.0
    score += 2.5 * len(tags_set.intersection(themes_set))
    score += 1.0 * len(tags_set.intersection(tokens))

    time_avail = normalize_text(responses.get("time_per_week", "")).lower()
    if time_avail in {"0-2", "0–2"} and goal.timeframe_weeks <= 2:
        score += 1.0
    if time_avail in {"3-5", "3–5"} and goal.timeframe_weeks <= 4:
        score += 0.5

    constraints = {t.strip().lower() for t in normalize_text(responses.get("constraints", "")).split(",") if t.strip()}
    if "money" in constraints and "finance" in tags_set:
        score += 0.3

    return score


def recommend_goals(
    goals: list[Goal],
    responses: dict[str, Any],
    top_n: int = 5,
) -> tuple[list[Goal], list[str], float]:
    themes = extract_themes(responses)
    if not themes:
        # Low-signal fallback: still return a diverse starter set.
        starter = []
        for theme in ["career", "tech", "health", "finance", "community"]:
            for g in goals:
                if g.theme == theme:
                    starter.append(g)
                    break
        return starter[:top_n], [], 0.0

    scored: list[tuple[float, Goal]] = [(score_goal(g, themes, responses), g) for g in goals]
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [g for _, g in scored[:top_n]]

    confidence = min(1.0, (scored[0][0] / 6.0) if scored else 0.0)
    return top, themes, confidence


def env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


INTEREST_TO_THEMES: dict[str, list[str]] = {
    "Technology": ["tech", "career"],
    "Design": ["creative", "career"],
    "Business": ["career", "finance"],
    "Content Creation": ["creative", "community"],
    "Public Service": ["community", "career"],
    "Research": ["tech", "career"],
    "Health": ["health"],
    "Finance": ["finance"],
    "Community": ["community"],
    "Creative": ["creative"],
    "Other": [],
}


def detect_emotional_signals(responses: dict[str, Any]) -> list[str]:
    text = " ".join(
        [
            normalize_text(responses.get("topics")),
            normalize_text(responses.get("long_term_vision")),
            normalize_text(responses.get("family_expectations")),
            normalize_text(responses.get("hard_nos")),
        ]
    ).lower()

    signals: list[str] = []
    if any(w in text for w in ["confus", "lost", "stuck", "uncertain", "not sure", "overwhelm"]):
        signals.append("uncertainty")
    if any(w in text for w in ["pressure", "stressed", "stress", "anxious", "anxiety", "worried"]):
        signals.append("pressure")
    if any(w in text for w in ["excited", "hope", "motivated", "energized", "curious", "interest"]):
        signals.append("curiosity")

    # If user explicitly selected a mood, trust that too.
    mood = normalize_text(responses.get("mood")).lower()
    if mood in {"confused", "not sure"} and "uncertainty" not in signals:
        signals.append("uncertainty")
    if mood in {"stressed/pressured", "stressed", "pressured"} and "pressure" not in signals:
        signals.append("pressure")
    if mood in {"excited", "curious"} and "curiosity" not in signals:
        signals.append("curiosity")

    return signals


def appreciation_message(responses: dict[str, Any], signals: list[str]) -> str:
    age = normalize_text(responses.get("age_range"))
    age_hint = ""
    if age and age != "Prefer not to say":
        if "13" in age or "Under" in age or "16" in age or "17" in age:
            age_hint = "especially at your age, "

    if "pressure" in signals:
        return (
            f"Thanks for sharing all of that. It takes courage to think about your future {age_hint}"
            "when there’s pressure or expectations around you. You’re doing a really mature thing by trying to understand yourself."
        )
    if "uncertainty" in signals:
        return (
            f"Thank you for answering these questions. Feeling unsure {age_hint}"
            "is completely normal, and taking time to reflect is a strong first step. You’re not behind—you’re learning what fits you."
        )
    return (
        f"Nice work taking this seriously. Thinking about your direction {age_hint}"
        "and putting your interests into words is a real skill—and it’s how good plans start."
    )


def supportive_closing(responses: dict[str, Any], signals: list[str]) -> str:
    age = normalize_text(responses.get("age_range"))
    extra = ""
    if age and age in {"Under 13", "13-15", "16-18"}:
        extra = " If you want, you can also talk this through with a trusted adult (parent/guardian, teacher, counselor) to get support."

    if "pressure" in signals:
        return (
            "You don’t have to figure everything out at once. Small steps are still real progress, and your path can change as you learn more."
            + extra
        )
    if "uncertainty" in signals:
        return (
            "It’s okay if you’re not 100% sure yet—clarity usually comes from trying small experiments, not from perfect thinking."
            + extra
        )
    return "Keep going at your own pace. You’re capable of building something meaningful step by step." + extra


def interest_meaning(interest: str) -> str:
    meanings: dict[str, str] = {
        "Technology": "Using computers and tools to build things (apps, websites, data projects, automations).",
        "Design": "Making things easier and nicer to use—visual design, UI/UX, and creative problem solving.",
        "Business": "Understanding how ideas become real: customers, strategy, operations, and leadership.",
        "Content Creation": "Sharing ideas through video, writing, audio, or social posts—and building a voice over time.",
        "Public Service": "Work that helps people directly: education, government, nonprofits, health support, advocacy.",
        "Research": "Exploring questions deeply, testing ideas, and learning through evidence and curiosity.",
        "Health": "Building habits that improve energy, strength, mental health, and overall wellbeing.",
        "Finance": "Managing money calmly: budgeting, saving, and understanding basics over time.",
        "Community": "Finding people who share interests and building supportive connections.",
        "Creative": "Expressing ideas through art, writing, music, photography, or making things.",
    }
    return meanings.get(interest, "Exploring what you enjoy and what kind of work/life fits you best.")


def build_interest_roadmap(
    *,
    interest: str,
    responses: dict[str, Any],
    all_goals: list[Goal],
) -> dict[str, Any]:
    themes = INTEREST_TO_THEMES.get(interest, [])
    candidate_goals = [g for g in all_goals if (g.theme in themes or any(t in themes for t in g.tags))]
    candidate_goals = candidate_goals[:2] if candidate_goals else []

    motivations = responses.get("motivation", [])
    if isinstance(motivations, str):
        motivations = [motivations]
    motivations_text = ", ".join(str(m) for m in motivations) if motivations else ""

    style = normalize_text(responses.get("style"))
    time_per_week = normalize_text(responses.get("time_per_week"))
    constraints = normalize_text(responses.get("constraints"))

    why_parts: list[str] = []
    if motivations_text:
        why_parts.append(f"it matches what motivates you ({motivations_text})")
    if style:
        why_parts.append(f"you prefer learning via {style.lower()}")
    if time_per_week:
        why_parts.append(f"it can fit into about {time_per_week} hours/week")
    if constraints and constraints.lower() != "none":
        why_parts.append(f"we’ll keep constraints in mind ({constraints})")

    why = "This could be a good fit because " + ("; ".join(why_parts) if why_parts else "it lines up with your interests and your current situation.") + "."

    next_steps: list[str] = []
    if candidate_goals:
        for g in candidate_goals:
            next_steps.extend(g.first_steps[:2])
    else:
        next_steps = [
            "Pick one tiny starter project/habit you can do this week.",
            "Spend 30–60 minutes exploring 2 beginner resources and choose one.",
            "Do one small practice session and write down what felt fun vs. draining.",
        ]

    plan_3_months = [
        "Weeks 1–2: Explore (try 2 small experiments; pick one path to continue).",
        "Weeks 3–6: Build basics (short practice sessions + one simple milestone each week).",
        "Weeks 7–10: Create something real (a small project, portfolio piece, or habit streak).",
        "Weeks 11–12: Reflect + level up (what worked, what didn’t, and your next goal).",
    ]

    example_skills = []
    if interest == "Technology":
        example_skills = ["Python basics", "building a small app", "automation", "problem solving"]
    elif interest == "Design":
        example_skills = ["UI basics", "color/type", "wireframing", "user testing"]
    elif interest == "Business":
        example_skills = ["customer research", "basic analytics", "planning", "communication"]
    elif interest == "Content Creation":
        example_skills = ["writing hooks", "simple editing", "posting consistently", "storytelling"]
    elif interest == "Public Service":
        example_skills = ["active listening", "community research", "program planning", "collaboration"]
    elif interest == "Research":
        example_skills = ["asking good questions", "finding sources", "note-taking", "basic data skills"]
    elif interest == "Health":
        example_skills = ["habit building", "basic training plan", "tracking progress", "recovery basics"]
    elif interest == "Finance":
        example_skills = ["budgeting", "saving systems", "understanding interest", "goal setting"]
    elif interest == "Community":
        example_skills = ["finding groups", "showing up consistently", "conversation starters", "follow-through"]
    elif interest == "Creative":
        example_skills = ["daily practice", "getting feedback", "shipping small pieces", "building a style"]

    return {
        "interest": interest,
        "meaning": interest_meaning(interest),
        "why": why,
        "next_steps": next_steps[:6],
        "plan_3_months": plan_3_months,
        "example_skills": example_skills,
        "recommended_goals": [
            {
                "id": g.id,
                "title": g.title,
                "theme": g.theme,
                "timeframe_weeks": g.timeframe_weeks,
                "difficulty": g.difficulty,
                "description": g.description,
                "first_steps": g.first_steps,
                "resources": g.resources,
            }
            for g in candidate_goals
        ],
    }


def try_openai_personalize(
    *,
    responses: dict[str, Any],
    goals: list[Goal],
    model: str = "gpt-4.1-mini",
) -> list[dict[str, Any]] | None:
    """
    Optional enhancement:
    - If OPENAI_API_KEY is set and the `openai` package is available, return personalized
      explanations and a reranked list.
    - If anything fails, return None and the app uses local matching only.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None


def try_openai_roadmap(
    *,
    responses: dict[str, Any],
    interests: list[str],
    model: str = "gpt-4.1-mini",
) -> dict[str, Any] | None:
    """
    Optional enhancement:
    - If OPENAI_API_KEY is set and the `openai` package is available, generate a supportive
      career/goal roadmap using the requested output structure.
    - Returns JSON for rendering; if anything fails, return None.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from openai import OpenAI  # type: ignore
    except Exception:
        return None

    client = OpenAI(api_key=api_key)

    prompt = {
        "role": "You are an empathetic, student-friendly AI career and goal discovery assistant.",
        "rules": [
            "Friendly, supportive, simple language.",
            "Respect emotional and family context; never judge.",
            "Avoid medical/financial/legal advice; keep it educational and general.",
            "Be age-appropriate when age_range is provided.",
            "Return JSON only.",
        ],
        "responses": responses,
        "interests": interests,
        "output_schema": {
            "type": "object",
            "properties": {
                "appreciation": {"type": "string"},
                "personal_summary": {"type": "string"},
                "goal_clarity": {
                    "type": "object",
                    "properties": {"primary_goal": {"type": "string"}, "secondary_interests": {"type": "array", "items": {"type": "string"}}},
                    "required": ["primary_goal", "secondary_interests"],
                },
                "roadmap": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "interest": {"type": "string"},
                            "what_it_means": {"type": "string"},
                            "why_it_suits_you": {"type": "string"},
                            "beginner_steps": {"type": "array", "items": {"type": "string"}},
                            "plan_3_months": {"type": "array", "items": {"type": "string"}},
                            "examples": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["interest", "what_it_means", "why_it_suits_you", "beginner_steps", "plan_3_months", "examples"],
                    },
                },
                "closing": {"type": "string"},
            },
            "required": ["appreciation", "personal_summary", "goal_clarity", "roadmap", "closing"],
        },
    }

    try:
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": json.dumps(prompt)}],
        )
        text = (resp.output_text or "").strip()
        if not text:
            return None
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            return None
        return parsed
    except Exception:
        return None

    client = OpenAI(api_key=api_key)

    goals_payload = [
        {
            "id": g.id,
            "title": g.title,
            "theme": g.theme,
            "timeframe_weeks": g.timeframe_weeks,
            "difficulty": g.difficulty,
            "description": g.description,
            "first_steps": g.first_steps[:4],
            "tags": g.tags[:8],
        }
        for g in goals
    ]

    prompt = {
        "task": "Personalize goal recommendations from a questionnaire.",
        "rules": [
            "Be supportive and practical.",
            "Avoid medical/financial/legal advice; keep it educational and general.",
            "Prefer feasible goals given time constraints.",
            "Return JSON only.",
        ],
        "responses": responses,
        "candidates": goals_payload,
        "output_schema": {
            "type": "object",
            "properties": {
                "ranked": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "why": {"type": "string"},
                            "next_steps": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["id", "why", "next_steps"],
                    },
                }
            },
            "required": ["ranked"],
        },
    }

    try:
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": json.dumps(prompt)}],
        )
        text = (resp.output_text or "").strip()
        if not text:
            return None
        parsed = json.loads(text)
        ranked = parsed.get("ranked", [])
        if not isinstance(ranked, list):
            return None
        return ranked
    except Exception:
        return None

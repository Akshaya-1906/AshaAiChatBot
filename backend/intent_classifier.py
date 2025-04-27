import re

# Keywords that indicate bias or offensive intent
BIAS_KEYWORDS = [
    "women can't", "not for girls", "too emotional", "not suitable for women",
    "she shouldn't", "women are weak", "men are better", "boys are smarter",
    "emotional creatures", "women overreact", "not a man's job", "hormonal",
    "not a woman thing", "she won't handle it", "men are natural leaders",
    "she must be on her period"
]

OFFENSIVE_KEYWORDS = [
    "bitch", "slut", "whore", "dumb", "stupid", "idiot", "useless", "trash",
    "cunt", "hoe", "fuck you", "screw you", "get lost", "shit", "kill yourself",
    "die", "freak", "fat", "ugly", "weak", "nonsense", "worthless", "moron",
    "fool", "jerk", "sexist", "loser", "psycho", "retard", "ashamed", "incapable"
]

# Responses for specific intent types
RESPONSES = {
    "offensive": (
        "I’m here to foster respectful, constructive conversations. "
        "Let’s keep things positive and focused on helping you grow, learn, and explore meaningful opportunities in tech. "
        "Kindness and encouragement go a long way."
    ),
    "bias": (
        "Let’s challenge outdated beliefs together. Women are driving innovation, leading teams, and reshaping the future of tech every day. "
        "If you’re here to learn or grow, I’ve got your back — no matter your background or identity."
    )
}


def normalize_text(text: str) -> str:
    """Lowercases and removes extra spacing from text for consistent matching."""
    return re.sub(r'\s+', ' ', text.strip().lower())


def classify_intent(user_input: str) -> dict:
    """
    Classify user input as 'offensive', 'bias', or 'neutral'.
    
    Returns:
        dict: {
            "intent": "offensive" | "bias" | "neutral",
            "response": str | None
        }
    """
    normalized_input = normalize_text(user_input)

    for phrase in OFFENSIVE_KEYWORDS:
        if phrase in normalized_input:
            return {
                "intent": "offensive",
                "response": RESPONSES["offensive"]
            }

    for phrase in BIAS_KEYWORDS:
        if phrase in normalized_input:
            return {
                "intent": "bias",
                "response": RESPONSES["bias"]
            }

    return {
        "intent": "neutral",
        "response": None
    }
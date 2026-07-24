from pathlib import Path


def create_session(print_name):

    root = Path("outputs") / print_name
    root.mkdir(parents=True, exist_ok=True)

    existing = sorted(root.glob("I*"))

    attempt = len(existing) + 1

    session = root / f"I{attempt:03d}"

    (session / "images").mkdir(parents=True)
    (session / "renders").mkdir()
    (session / "analysis").mkdir()

    return session, attempt
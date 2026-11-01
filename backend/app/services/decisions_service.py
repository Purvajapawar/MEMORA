
import re
from pathlib import Path

import pandas as pd


# Project root / data file
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "MEMORA_cleaned_documents.parquet"
)


# Explicit evidence patterns
DATED_DECISION_PATTERN = re.compile(
    r"^\s*[-*]?\s*"
    r"(\d{4}-\d{2}-\d{2})\s*:\s*(.+)$",
    re.MULTILINE
)

APPROVAL_PATTERN = re.compile(
    r"^\s*[-*]?\s*Approved by\s*:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE
)

CHOSEN_PATTERN = re.compile(
    r"\bWe chose\b.{10,300}",
    re.IGNORECASE
)

FINAL_DECISION_PATTERN = re.compile(
    r"\bFinal decision\s*:\s*(.{10,400})",
    re.IGNORECASE
)


def clean_text(value):
    """Normalize extracted text."""
    return re.sub(r"\s+", " ", str(value)).strip()


def get_decisions():
    """
    Extract explicitly documented decisions from MEMORA data.

    Only strong evidence is included.
    Policies and hypothetical recommendations are excluded.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"MEMORA dataset not found: {DATASET_PATH}"
        )

    df = pd.read_parquet(DATASET_PATH)

    required_columns = {
        "doc_id",
        "source_type",
        "title",
        "content",
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Dataset is missing required columns."
        )

    decisions = []
    seen = set()

    for _, row in df.iterrows():

        title = clean_text(row["title"])
        content = str(row["content"] or "")
        source_type = clean_text(row["source_type"])
        doc_id = str(row["doc_id"])

        is_adr = bool(
            re.search(r"\bADR(?:-\d+)?\s*:", title, re.I)
        )

        # Only process strong decision-bearing documents.
        if not is_adr and not re.search(
            r"\bDecision Log\b",
            content,
            re.IGNORECASE
        ):
            continue

        # 1. Extract dated decision log entries.
        for match in DATED_DECISION_PATTERN.finditer(content):

            decision_date = match.group(1)
            decision_text = clean_text(match.group(2))

            if len(decision_text) < 12:
                continue

            key = (doc_id, decision_date, decision_text.lower())

            if key in seen:
                continue

            seen.add(key)

            start = max(0, match.start() - 250)
            end = min(len(content), match.end() + 350)

            decisions.append({
                "id": f"{doc_id}_{len(decisions) + 1}",
                "title": title,
                "decision": decision_text,
                "date": decision_date,
                "category": "Decision Log",
                "approval": None,
                "evidence": clean_text(content[start:end]),
                "source_type": source_type,
                "doc_id": doc_id,
            })

        # 2. Extract explicit approval records from ADRs.
        if is_adr:

            for match in APPROVAL_PATTERN.finditer(content):

                approval_text = clean_text(match.group(1))

                key = (
                    doc_id,
                    "approval",
                    approval_text.lower()
                )

                if key in seen:
                    continue

                seen.add(key)

                start = max(0, match.start() - 250)
                end = min(len(content), match.end() + 350)

                decisions.append({
                    "id": f"{doc_id}_{len(decisions) + 1}",
                    "title": title,
                    "decision": (
                        "Approval recorded for the documented "
                        "architecture decision."
                    ),
                    "date": None,
                    "category": "Approval",
                    "approval": approval_text,
                    "evidence": clean_text(content[start:end]),
                    "source_type": source_type,
                    "doc_id": doc_id,
                })

            # 3. Extract explicit chosen approaches.
            for match in CHOSEN_PATTERN.finditer(content):

                decision_text = clean_text(match.group(0))

                key = (
                    doc_id,
                    "chosen",
                    decision_text.lower()
                )

                if key in seen:
                    continue

                seen.add(key)

                start = max(0, match.start() - 250)
                end = min(len(content), match.end() + 350)

                decisions.append({
                    "id": f"{doc_id}_{len(decisions) + 1}",
                    "title": title,
                    "decision": decision_text,
                    "date": None,
                    "category": "Technical Choice",
                    "approval": None,
                    "evidence": clean_text(content[start:end]),
                    "source_type": source_type,
                    "doc_id": doc_id,
                })

            # 4. Extract explicitly labeled final decisions.
            for match in FINAL_DECISION_PATTERN.finditer(content):

                decision_text = clean_text(match.group(1))

                key = (
                    doc_id,
                    "final",
                    decision_text.lower()
                )

                if key in seen:
                    continue

                seen.add(key)

                start = max(0, match.start() - 250)
                end = min(len(content), match.end() + 350)

                decisions.append({
                    "id": f"{doc_id}_{len(decisions) + 1}",
                    "title": title,
                    "decision": decision_text,
                    "date": None,
                    "category": "Final Decision",
                    "approval": None,
                    "evidence": clean_text(content[start:end]),
                    "source_type": source_type,
                    "doc_id": doc_id,
                })

    decisions.sort(
        key=lambda item: item["date"] or "",
        reverse=True
    )

    return decisions


import re
from pathlib import Path
from collections import defaultdict

import pandas as pd


# ============================================================
# 1. DATASET CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "MEMORA_cleaned_documents.parquet"
)


# ============================================================
# 2. PERSON EXTRACTION PATTERNS
# ============================================================

PERSON_PATTERNS = [
    (
        "Document Owner",
        r"Document owner\s*:\s*[^()\n]{0,100}\(([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})\)"
    ),
    (
        "Reviewer",
        r"(?:^|[\n;])\s*(?:[A-Za-z ]+)?Reviewer\s*:\s*([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})"
    ),
    (
        "Contact",
        r"(?:Point of contact|Billing contact|Contact)\s*:\s*([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})"
    ),
    (
        "Escalation Owner",
        r"Escalation owner\s*:\s*([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){1,3})\s*(?:\(|—|–|$)"
    ),
]


# ============================================================
# 3. FALSE POSITIVE FILTERING
# ============================================================

INVALID_STARTS = {
    "added",
    "add",
    "updated",
    "expanded",
    "fixed",
    "changed",
    "removed",
    "created",
    "evaluates",
    "reviewed",
    "counter",
    "facilities",
    "failover",
}

INVALID_TERMS = {
    "lead",
    "architecture",
    "strategy",
    "team",
    "engineering",
    "security",
    "platform",
    "operations",
     "listed",
      "see",
       "refer",
       "available",
}


def is_valid_person_name(name):
    """
    Basic filtering to reject obvious actions,
    technical labels and role descriptions.

    This is heuristic filtering, not full NER.
    """

    if not name:
        return False

    name = name.strip()

    parts = name.split()

    if len(parts) < 2:
        return False

    if parts[0].casefold() in INVALID_STARTS:
        return False

    if any(
        part.casefold() in INVALID_TERMS
        for part in parts
    ):
        return False

    # Reject names containing digits.
    if any(char.isdigit() for char in name):
        return False

    return True


# ============================================================
# 4. EXPERT EXTRACTION
# ============================================================

def get_experts():
    """
    Extract people explicitly mentioned in labelled
    ownership, reviewer, contact and escalation fields.

    Every extracted record retains supporting evidence.
    """

    # --------------------------------------------------------
    # Check dataset availability
    # --------------------------------------------------------

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"MEMORA dataset not found: {DATASET_PATH}"
        )

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    df = pd.read_parquet(DATASET_PATH)

    required_columns = {
        "title",
        "content",
        "source_type",
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "Dataset is missing required columns."
        )

    # --------------------------------------------------------
    # Store extracted people
    # --------------------------------------------------------

    experts = defaultdict(
        lambda: {
            "name": "",
            "roles": set(),
            "evidence": [],
        }
    )

    # --------------------------------------------------------
    # Process documents
    # --------------------------------------------------------

    for _, row in df.iterrows():

        content = str(row["content"])
        title = str(row["title"])
        source = str(row["source_type"])

        for role, pattern in PERSON_PATTERNS:

            matches = re.finditer(
                pattern,
                content,
                flags=re.IGNORECASE | re.MULTILINE,
            )

            for match in matches:

                name = match.group(1).strip()

                # Reject obvious false positives.
                if not is_valid_person_name(name):
                    continue

                key = name.casefold()

                expert = experts[key]

                expert["name"] = name
                expert["roles"].add(role)

                # ------------------------------------------------
                # Capture supporting evidence
                # ------------------------------------------------

                evidence = {
                    "document_title": title,
                    "source_type": source,
                    "role": role,
                    "context": content[
                        max(0, match.start() - 100):
                        min(len(content), match.end() + 150)
                    ].replace("\n", " "),
                }

                if evidence not in expert["evidence"]:
                    expert["evidence"].append(evidence)

    # --------------------------------------------------------
    # Prepare final results
    # --------------------------------------------------------

    results = []

    for expert in experts.values():

        results.append({
            "name": expert["name"],
            "roles": sorted(expert["roles"]),
            "evidence": expert["evidence"],
            "evidence_count": len(expert["evidence"]),
        })

    # --------------------------------------------------------
    # Sort alphabetically
    # --------------------------------------------------------

    return sorted(
        results,
        key=lambda item: item["name"].casefold(),
    )

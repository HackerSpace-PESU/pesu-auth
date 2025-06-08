from dataclasses import dataclass, field
from typing import List, Dict


@dataclass(frozen=True)
class PESUAcademyConstants:
    DEFAULT_FIELDS: List[str] = field(
        default_factory=lambda: [
            "name",
            "prn",
            "srn",
            "program",
            "branch_short_code",
            "branch",
            "semester",
            "section",
            "email",
            "phone",
            "campus_code",
            "campus",
            "class",
            "cycle",
            "department",
            "institute_name",
        ]
    )

    BRANCH_SHORT_CODES: Dict[str, str] = field(
        default_factory=lambda: {
            "Computer Science and Engineering": "CSE",
            "Electronics and Communication Engineering": "ECE",
            "Mechanical Engineering": "ME",
            "Electrical and Electronics Engineering": "EEE",
            "Civil Engineering": "CE",
            "Biotechnology": "BT",
            "Computer Science and Engineering (AI&ML)":"CSE(AIML)",
        }
    )

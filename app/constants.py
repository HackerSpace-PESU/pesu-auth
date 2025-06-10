from typing import List, Dict


class PESUAcademyConstants:
    DEFAULT_FIELDS: List[str] = [
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

    BRANCH_SHORT_CODES: Dict[str, str] = {
        "Computer Science and Engineering": "CSE",
        "Computer Science and Engineering (AI&ML)": "CSE (AI&ML)",
        "Electronics and Communication Engineering": "ECE",
        "Mechanical Engineering": "ME",
        "Electrical and Electronics Engineering": "EEE",
        "Civil Engineering": "CE",
        "Biotechnology": "BT",
        "Bachelor of Computer Applications": "BCA",
        "BA LLB Hons": "BA LLB (Hons)",
    }

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
        "class",  # TODO: These fields seem to have been deprecated in the latest version
        "cycle",  # TODO: These fields seem to have been deprecated in the latest version
        "department",  # TODO: These fields seem to have been deprecated in the latest version
        "institute_name",  # TODO: These fields seem to have been deprecated in the latest version
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
        "BA LLB": "BA LLB",
        "Psychology": "Psychology",
        "Bachelor of Business Administration": "BBA",
    }

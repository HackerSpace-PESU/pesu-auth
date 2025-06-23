class PESUAcademyConstants:
    DEFAULT_FIELDS: list[str] = [
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
    ]

    BRANCH_SHORT_CODES: dict[str, str] = {
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

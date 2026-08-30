GITHUB_ORG = "https://github.com/UniversalDependencies"


LANGUAGE_MAP = {
    # EU Official Languages
    "bul": {
        "name": "Bulgarian",
        "repo": "UD_Bulgarian-BTB",
    },
    "ces": {
        "name": "Czech",
        "repo": "UD_Czech-CAC",
    },
    "dan": {
        "name": "Danish",
        "repo": "UD_Danish-DDT",
    },
    "deu": {
        "name": "German",
        "repo": "UD_German-GSD",
    },
    "ell": {
        "name": "Greek",
        "repo": "UD_Greek-GDT",
    },
    "eng": {
        "name": "English",
        "repo": "UD_English-EWT",
    },
    "est": {
        "name": "Estonian",
        "repo": "UD_Estonian-EDT",
    },
    "fin": {
        "name": "Finnish",
        "repo": "UD_Finnish-TDT",
    },
    "fra": {
        "name": "French",
        "repo": "UD_French-GSD",
    },
    "gle": {
        "name": "Irish",
        "repo": "UD_Irish-IDT",
    },
    "hrv": {
        "name": "Croatian",
        "repo": "UD_Croatian-SET",
    },
    "hun": {
        "name": "Hungarian",
        "repo": "UD_Hungarian-Szeged",
    },
    "ita": {
        "name": "Italian",
        "repo": "UD_Italian-ISDT",
    },
    "lav": {
        "name": "Latvian",
        "repo": "UD_Latvian-LVTB",
    },
    "lit": {
        "name": "Lithuanian",
        "repo": "UD_Lithuanian-ALKSNIS",
    },
    "mlt": {
        "name": "Maltese",
        "repo": "UD_Maltese-MUDT",
    },
    "nld": {
        "name": "Dutch",
        "repo": "UD_Dutch-Alpino",
    },
    "pol": {
        "name": "Polish",
        "repo": "UD_Polish-PDB",
    },
    "por": {
        "name": "Portuguese",
        "repo": "UD_Portuguese-CINTIL",
    },
    "ron": {
        "name": "Romanian",
        "repo": "UD_Romanian-RRT",
    },
    "slk": {
        "name": "Slovak",
        "repo": "UD_Slovak-SNK",
    },
    "slv": {
        "name": "Slovenian",
        "repo": "UD_Slovenian-SSJ",
    },
    "spa": {
        "name": "Spanish",
        "repo": "UD_Spanish-AnCora",
    },
    "swe": {
        "name": "Swedish",
        "repo": "UD_Swedish-LinES",
    },

    # Co-official Languages
    "cat": {
        "name": "Catalan",
        "repo": "UD_Catalan-AnCora",
    },
    "eus": {
        "name": "Basque",
        "repo": "UD_Basque-BDT",
    },
    "glg": {
        "name": "Galician",
        "repo": "UD_Galician-CTG",
    },

    # Candidate EU Members
    # "bos": {
    #     "name": "Bosnian",
    #     "repo": None,
    # },
    "kat": {
        "name": "Georgian",
        "repo": "UD_Georgian-GLC",
    },
    # "mkd": {
    #     "name": "Macedonian",
    #     "repo": None
    # },
    "sqi": {
        "name": "Albanian",
        "repo": "UD_Albanian-STAF",
    },
    "srp": {
        "name": "Serbian",
        "repo": "UD_Serbian-SET",
    },
    "tur": {
        "name": "Turkish",
        "repo": "UD_Turkish-Kenet",
    },
    "ukr": {
        "name": "Ukrainian",
        "repo": "UD_Ukrainian-IU",
    },

    # Closely Associated Scandinavian
    "isl": {
        "name": "Icelandic",
        "repo": "UD_Icelandic-IcePaHC",
    },
    "nor": {
        "name": "Norwegian",
        "repo": "UD_Norwegian-Bokmaal",
    },
}


def get_language(language_code: str) -> dict:
    """Return configuration for an OpenEuroLLM language code."""
    code = language_code.lower().strip()

    if code not in LANGUAGE_MAP:
        raise ValueError(
            f"Unsupported language code: {language_code}"
        )

    config = LANGUAGE_MAP[code]

    if config["repo"] is None:
        raise ValueError(
            f"No Universal Dependencies treebank is available "
            f"for {config['name']} ({code})."
        )

    return config


def get_repo_url(language_code: str) -> str:
    """Return the GitHub repository URL for a language."""
    config = get_language(language_code)

    return f"{GITHUB_ORG}/{config['repo']}.git"
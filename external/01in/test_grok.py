#!/usr/bin/env python3

import multiprocessing

from crapi_core import ask_topics
from crapi_grok import AskGrokOnX
from crapi_youcom import AskYouCom

if __name__ == "__main__":
    multiprocessing.freeze_support()

    def ask(topics: list[str], api: AskGrokOnX | AskYouCom | None):
        answers = ask_topics(topics, api=api)
        for _answer in answers:
            pass

    api = AskGrokOnX(verbose=False)
    topics = [
        # "FontLab & font editors",
        "font technology & OpenType",
        "typeface design & font creation",
        # "web & print typography",
        # "Unicode & internationalization",
        # "history of printing and writing",
    ]

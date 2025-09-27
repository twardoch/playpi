# this_file: src/playpi/example_prompts.py
"""Shared example prompts for Google Deep Research workflows."""

PROMPT_EN = (
    "Carefully research English-language books that exist in real life that provide "
    "advice on (1) typography (2) graphic design (3) history of writing (4) book "
    "publishing (5) editorial design (6) history and technology of printing (7) "
    "writing systems, scripts and languages (8) calligraphy.\n\n"
    "Compile a document that has semicolon-separated records like this (one record per line):\n\n"
    "ISBN;Author's Full Name;Book Title;Year of publication;Language of publication;Notes and remarks\n\n"
    "Only include books that actually exist, and only those that are widely considered to be good. Double-check."
)

PROMPT_PL = (
    "Dokładnie zbadaj polskojęzyczne książki, które istnieją w rzeczywistości, a które zawierają porady dotyczące "
    "(1) typografii (2) projektowania graficznego (3) historii pisma (4) wydawania książek (5) projektowania "
    "edytorskiego (6) historii i technologii druku (7) systemów pisma, alfabetów i języków (8) kaligrafii.\n\n"
    "Skompiluj dokument, który zawiera rekordy rozdzielone średnikami "
    "w następującym formacie (jeden rekord na wiersz):\n\n"
    "ISBN;Pełne imię i nazwisko autora;Tytuł książki;Rok wydania;Język publikacji;Uwagi i komentarze\n\n"
    "Uwzględnij wyłącznie książki, które faktycznie istnieją, i tylko takie, "
    "które są powszechnie uważane za dobre. Sprawdź dwukrotnie."
)

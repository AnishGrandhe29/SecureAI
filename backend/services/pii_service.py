"""
PII Scrubbing Service — Microsoft Presidio
Production-grade NER-based entity detection for scrubbing PII
from retrieved text before it reaches the LLM or the client.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Lazy-loaded singletons
_analyzer = None
_anonymizer = None


def _get_engines():
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


ENTITIES_TO_SCRUB = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER",
    "CREDIT_CARD", "US_SSN", "IP_ADDRESS",
    "US_BANK_NUMBER", "IBAN_CODE",
]


def scrub(text: str, language: str = "en") -> str:
    """
    Scrub PII from text using Presidio.
    Replaces detected entities with placeholder tags like <PERSON>, <EMAIL_ADDRESS>, etc.
    """
    if not text or not text.strip():
        return text

    analyzer, anonymizer = _get_engines()

    results = analyzer.analyze(
        text=text,
        entities=ENTITIES_TO_SCRUB,
        language=language,
    )

    if not results:
        return text

    operators = {
        entity: OperatorConfig("replace", {"new_value": f"<{entity}>"})
        for entity in ENTITIES_TO_SCRUB
    }

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators,
    )

    return anonymized.text

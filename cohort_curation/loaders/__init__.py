"""Domain loader modules for cohort data access."""

from . import diagnosis, followup, genomics, histopathology, imaging, labs, patient, procedures

__all__ = [
    "patient",
    "genomics",
    "diagnosis",
    "labs",
    "imaging",
    "procedures",
    "histopathology",
    "followup",
]

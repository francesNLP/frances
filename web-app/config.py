import os
from pathlib import Path

from rdflib.namespace import Namespace, RDF, RDFS, OWL, XSD
from rdflib.namespace import SKOS, DOAP, FOAF, DC, DCTERMS

DEBUG = True

BASE_DIR = Path(os.path.abspath(os.path.dirname(__file__)))
SECRET_KEY = os.urandom(64)

# Prefixes and namespaces to use.
NAMESPACES = dict(
    rdf=RDF,
    rdfs=RDFS,
    owl=OWL,
    xsd=XSD,
    skos=SKOS,
    doap=DOAP,
    foaf=FOAF,
    dc=DC,
    dcterms=DCTERMS,
)

# URLs from which to download RDF data.
RDF_URLS = []


PARSERS = {
    ".rdf": "xml",
    ".n3": "n3",
    ".ttl": "turtle",
    ".xml": "xml",
}

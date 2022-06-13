"""
Exports all embedders relevant to our proyect
"""
from typing import List

from cf_genie.embedders.base import BaseEmbedder
from cf_genie.embedders.doc2vec import Doc2VecEmbedder

EMBEDDERS: List[BaseEmbedder] = [Doc2VecEmbedder]
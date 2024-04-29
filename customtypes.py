from typing import TypeAlias

TokenToClassMap: TypeAlias = dict[str, str]
ClassToTokenMap: TypeAlias = dict[str, list[str]]

FulltextsMap: TypeAlias = dict[str, dict[str, str]]
"""Text is represented as list of sentences (list of words)"""
TokenizedMap: TypeAlias = dict[str, dict[str, list[list[str]]]]

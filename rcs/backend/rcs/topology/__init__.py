"""Topology utilities — DXF parsing, validation, templates.

Task 4 contributes `parse_dxf` / `DxfEntity` / `DxfDocument` (real).
Task 5 contributes `dxf_to_shell` (real).
Tasks 6-8 each edit THIS file to replace their placeholder with the real
re-export (same pattern as Task 4 and Task 5).
"""
from rcs.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument
from rcs.topology.dxf_to_shell import dxf_to_shell
from rcs.topology.validate import validate_shell, ValidationError, ValidationReport

from rcs.topology.markings import generate_markings

from rcs.topology.templates import (
    list_templates, get_template, SCENARIO_IDS, TemplateInfo, TemplateBundle,
)

__all__ = [
    "parse_dxf", "DxfEntity", "DxfDocument",
    "dxf_to_shell",
    "validate_shell", "ValidationError", "ValidationReport",
    "generate_markings",
    "list_templates", "get_template", "SCENARIO_IDS", "TemplateInfo", "TemplateBundle",
]

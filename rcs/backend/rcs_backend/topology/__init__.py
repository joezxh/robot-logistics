"""Topology utilities — DXF parsing, validation, templates.

Task 4 contributes `parse_dxf` / `DxfEntity` / `DxfDocument` (real).
Task 5 contributes `dxf_to_shell` (real).
Tasks 6-8 each edit THIS file to replace their placeholder with the real
re-export (same pattern as Task 4 and Task 5).
"""
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
from rcs_backend.topology.validate import validate_shell, ValidationError, ValidationReport

# Placeholders — replaced by Tasks 7, 8 respectively
def generate_markings(*args, **kwargs):
    raise NotImplementedError("generate_markings is added by Task 7")

def list_templates(*args, **kwargs):
    raise NotImplementedError("list_templates is added by Task 8")

def get_template(*args, **kwargs):
    raise NotImplementedError("get_template is added by Task 8")

__all__ = [
    "parse_dxf", "DxfEntity", "DxfDocument",
    "dxf_to_shell",
    "validate_shell", "ValidationError", "ValidationReport",
    "generate_markings",
    "list_templates", "get_template",
]

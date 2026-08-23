"""Topology utilities — DXF parsing, validation, templates.

Task 4 contributes `parse_dxf` / `DxfEntity` / `DxfDocument` (real).
Tasks 5-8 each edit THIS file to replace their placeholder with the real
re-export (same pattern as Task 4).
"""
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument

# Placeholders — replaced by Tasks 5, 6, 7, 8 respectively
def dxf_to_shell(*args, **kwargs):
    raise NotImplementedError("dxf_to_shell is added by Task 5")

def validate_shell(*args, **kwargs):
    raise NotImplementedError("validate_shell is added by Task 6")

def generate_markings(*args, **kwargs):
    raise NotImplementedError("generate_markings is added by Task 7")

def list_templates(*args, **kwargs):
    raise NotImplementedError("list_templates is added by Task 8")

def get_template(*args, **kwargs):
    raise NotImplementedError("get_template is added by Task 8")

__all__ = [
    "parse_dxf", "DxfEntity", "DxfDocument",
    "dxf_to_shell",
    "validate_shell",
    "generate_markings",
    "list_templates", "get_template",
]

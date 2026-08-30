"""Generate an MSVC import library (``.lib``) from a DLL.

Why this exists
---------------
MuJoCo's PyPI wheel on Windows ships ``mujoco/mujoco.dll`` **but no import
library** (``mujoco.lib``). The MSVC linker cannot link against a ``.dll``
directly -- it needs a ``.lib`` describing the exported symbols.

This script reproduces the standard recipe used in that situation:

    dumpbin /exports mujoco.dll   ->  parse the export table
    write mujoco.def              ->  EXPORTS <name1> <name2> ...
    lib /def:mujoco.def /out:mujoco.lib /machine:x64

It is called by ``CMakeLists.txt`` at configure time.

Usage
-----
    python cmake/gen_mujoco_import_lib.py --dll <path/to/mujoco.dll> \
                                          --out <path/to/mujoco.lib>
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Lines of `dumpbin /exports` look like:
#   "          1    0 0002A3F0 mj_activate"
# ordinal (dec), hint (hex), RVA (hex), exported name
_EXPORT_LINE = re.compile(r"^\s+\d+\s+[0-9A-Fa-f]+\s+[0-9A-Fa-f]+\s+(\S+)\s*$")


def _find_msvc_tool(name: str, explicit: str | None = None) -> str | None:
    """Locate an MSVC command-line tool (dumpbin/lib/cl).

    Search order:
      1. an explicit path handed in by CMake (derived from CMAKE_CXX_COMPILER)
      2. ``VCINSTALLDIR`` / ``VCToolsInstallDir`` env vars
      3. ``PATH``
    """
    if explicit:
        cand = Path(explicit)
        if cand.is_file():
            return str(cand)

    env_dirs = [
        os.environ.get("VCToolsInstallDir"),
        os.environ.get("VCINSTALLDIR"),
    ]
    if env_dirs[0]:  # VCToolsInstallDir already points at .../bin/Hostx64/x64
        env_dirs.append(str(Path(env_dirs[0]) / "bin" / "Hostx64" / "x64"))

    for d in env_dirs:
        if not d:
            continue
        cand = Path(d) / name
        if cand.is_file():
            return str(cand)

    return shutil.which(name)


def _parse_exports(dumpbin_out: str) -> list[str]:
    """Extract exported symbol names from ``dumpbin /exports`` output."""
    names: list[str] = []
    in_table = False

    for line in dumpbin_out.splitlines():
        # The table header is "ordinal hint RVA      name"; stop at the summary.
        if "ordinal" in line.lower() and "hint" in line.lower():
            in_table = True
            continue
        if not in_table:
            continue
        if line.strip().lower().startswith("summary"):
            break

        m = _EXPORT_LINE.match(line)
        if not m:
            continue
        sym = m.group(1)
        # Skip unnamed exports and forwarded exports ("Foo = Bar.Baz").
        if sym.startswith("[") or "=" in sym:
            continue
        names.append(sym)

    return names


def generate(dll: Path, out: Path,
             dumpbin_path: str | None = None, lib_path: str | None = None) -> int:
    dumpbin = _find_msvc_tool("dumpbin.exe", dumpbin_path)
    lib_tool = _find_msvc_tool("lib.exe", lib_path)
    if not dumpbin:
        print("gen_mujoco_import_lib: could not find dumpbin.exe", file=sys.stderr)
        return 2
    if not lib_tool:
        print("gen_mujoco_import_lib: could not find lib.exe", file=sys.stderr)
        return 2

    print(f"gen_mujoco_import_lib: dumpbin {dumpbin}")
    proc = subprocess.run(
        [dumpbin, "/exports", str(dll)],
        capture_output=True, text=True, errors="replace",
    )
    if proc.returncode != 0:
        print("gen_mujoco_import_lib: dumpbin failed:", proc.stderr[:500], file=sys.stderr)
        return 3

    names = _parse_exports(proc.stdout)
    if not names:
        print("gen_mujoco_import_lib: no exports parsed from dumpbin output", file=sys.stderr)
        return 4
    print(f"gen_mujoco_import_lib: {len(names)} exported symbols")

    out.parent.mkdir(parents=True, exist_ok=True)
    def_path = out.with_suffix(".def")
    def_path.write_text(
        "LIBRARY MUJOCO\nEXPORTS\n" + "".join(f"    {n}\n" for n in names),
        encoding="ascii",
    )

    machine = "x64" if "64" in (os.environ.get("VSCMD_ARG_TGT_ARCH") or "x64") else "x86"
    proc = subprocess.run(
        [lib_tool, f"/def:{def_path}", f"/out:{out}", f"/machine:{machine}", "/nologo"],
        capture_output=True, text=True, errors="replace",
    )
    if proc.returncode != 0 or not out.is_file():
        print("gen_mujoco_import_lib: lib.exe failed:", proc.stdout[:500], proc.stderr[:500],
              file=sys.stderr)
        return 5

    print(f"gen_mujoco_import_lib: wrote {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dll", required=True, help="path to the DLL to derive exports from")
    ap.add_argument("--out", required=True, help="path of the .lib to generate")
    ap.add_argument("--dumpbin", default=None, help="explicit path to dumpbin.exe")
    ap.add_argument("--lib", default=None, help="explicit path to lib.exe")
    args = ap.parse_args()

    dll = Path(args.dll)
    if not dll.is_file():
        print(f"gen_mujoco_import_lib: DLL not found: {dll}", file=sys.stderr)
        return 1
    return generate(dll, Path(args.out), args.dumpbin, args.lib)


if __name__ == "__main__":
    raise SystemExit(main())

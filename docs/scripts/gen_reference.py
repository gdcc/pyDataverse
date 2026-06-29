"""Generate Starlight MDX API-reference pages from the pyDataverse package.

Uses `griffe` to introspect every module, class, function and attribute and
renders one MDX page per module under ``docs/src/content/docs/reference/``,
mirroring the package's directory layout. The sidebar picks these up via
``autogenerate: { directory: 'reference' }`` in ``astro.config.mjs``.

Run from the repository root:

    .venv/bin/python docs/scripts/gen_reference.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import griffe

PACKAGE = "pyDataverse"
REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "docs" / "src" / "content" / "docs" / "reference"

# Modules that are internal machinery rather than user-facing interfaces.
# Anything matching a prefix (the module itself or any descendant) is skipped.
IGNORE_PREFIXES = {
    "pyDataverse.dataverse.connect",  # Pydantic model-building machinery
    "pyDataverse.dataverse.views",    # internal view helpers
    "pyDataverse.api.utilities",      # crawler / fetcher / logger internals
    "pyDataverse.mcp",                # MCP server impl (has its own docs section)
}
# Individual modules to skip (exact dotted paths).
IGNORE_EXACT = {
    "pyDataverse.dataverse.contentbase",  # internal base class
    "pyDataverse.api.api",                # internal base API class
    "pyDataverse.filesystem.reader",      # internal, behind DataverseFS
    "pyDataverse.filesystem.writer",      # internal, behind DataverseFS
    "pyDataverse.filesystem.tab",         # internal tabular helper
    "pyDataverse.models.message",         # internal message wrapper
}


def is_ignored(path: str) -> bool:
    if path in IGNORE_EXACT:
        return True
    return any(path == p or path.startswith(p + ".") for p in IGNORE_PREFIXES)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def esc(text: str) -> str:
    """Escape characters that MDX would otherwise treat as JSX."""
    return (
        text.replace("{", "&#123;")
        .replace("}", "&#125;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def yaml_quote(text: str) -> str:
    """Quote a string for safe use in YAML frontmatter."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def is_public(name: str) -> bool:
    return not name.startswith("_") or name in {"__init__", "__call__"}


def first_line(docstring) -> str:
    if not docstring:
        return ""
    line = docstring.value.strip().splitlines()[0].strip()
    return line


def annotation_str(annotation) -> str:
    if annotation is None:
        return ""
    return str(annotation)


def format_signature(func) -> str:
    """Build a readable Python signature string for a function/method."""
    parts = []
    star_added = False
    slash_pending = False
    for param in func.parameters:
        kind = param.kind.value if param.kind else "positional or keyword"
        if kind == "variadic positional":
            parts.append(f"*{param.name}")
            star_added = True
            continue
        if kind == "variadic keyword":
            parts.append(f"**{param.name}")
            continue
        if kind == "keyword-only" and not star_added:
            parts.append("*")
            star_added = True
        piece = param.name
        if param.annotation is not None:
            piece += f": {annotation_str(param.annotation)}"
        if param.default is not None:
            piece += f" = {param.default}"
        parts.append(piece)
        if kind == "positional-only":
            slash_pending = True
        elif slash_pending:
            # close the positional-only group
            idx = parts.index(piece)
            parts.insert(idx, "/")
            slash_pending = False
    sig = ", ".join(parts)
    ret = annotation_str(func.returns)
    arrow = f" -> {ret}" if ret else ""
    return f"{func.name}({sig}){arrow}"


def render_docstring_sections(docstring, level: int) -> list[str]:
    """Render parsed Google-style docstring sections to MDX lines."""
    out: list[str] = []
    if not docstring:
        return out
    for section in docstring.parsed:
        kind = section.kind.value
        if kind == "text":
            out.append("")
            out.append(esc(section.value).strip())
            out.append("")
        elif kind == "parameters":
            out.append("")
            out.append("**Parameters**")
            out.append("")
            out.append("| Name | Type | Description |")
            out.append("| --- | --- | --- |")
            for p in section.value:
                typ = f"`{esc(annotation_str(p.annotation))}`" if p.annotation else ""
                desc = esc(" ".join(p.description.split())) if p.description else ""
                default = ""
                if p.default is not None:
                    default = f" *(default: `{esc(str(p.default))}`)*"
                out.append(f"| `{p.name}` | {typ} | {desc}{default} |")
            out.append("")
        elif kind == "returns":
            out.append("")
            out.append("**Returns**")
            out.append("")
            out.append("| Type | Description |")
            out.append("| --- | --- |")
            for r in section.value:
                typ = f"`{esc(annotation_str(r.annotation))}`" if r.annotation else ""
                desc = esc(" ".join(r.description.split())) if r.description else ""
                out.append(f"| {typ} | {desc} |")
            out.append("")
        elif kind == "raises":
            out.append("")
            out.append("**Raises**")
            out.append("")
            out.append("| Exception | Description |")
            out.append("| --- | --- |")
            for r in section.value:
                typ = f"`{esc(annotation_str(r.annotation))}`" if r.annotation else ""
                desc = esc(" ".join(r.description.split())) if r.description else ""
                out.append(f"| {typ} | {desc} |")
            out.append("")
        elif kind in {"attributes", "other parameters"}:
            out.append("")
            out.append(f"**{section.title or kind.title()}**")
            out.append("")
            out.append("| Name | Type | Description |")
            out.append("| --- | --- | --- |")
            for a in section.value:
                typ = f"`{esc(annotation_str(a.annotation))}`" if a.annotation else ""
                desc = esc(" ".join(a.description.split())) if a.description else ""
                out.append(f"| `{a.name}` | {typ} | {desc} |")
            out.append("")
        elif kind == "examples":
            out.append("")
            out.append("**Examples**")
            out.append("")
            # value is a list of (subkind, text) tuples: prose vs. code blocks.
            for item in section.value:
                subkind = item[0].value if hasattr(item[0], "value") else str(item[0])
                text = item[1] if isinstance(item, tuple) else str(item)
                if subkind == "text":
                    out.append(esc(text).strip())
                    out.append("")
                else:
                    # Doctest / code — fence it so braces and angle brackets
                    # are treated literally by MDX.
                    out.append("```python")
                    out.append(text.rstrip())
                    out.append("```")
                    out.append("")
        elif kind == "admonition":
            out.append("")
            value = section.value
            title = getattr(value, "title", None) or getattr(section, "title", None)
            if title:
                out.append(f"**{esc(str(title))}**")
                out.append("")
            out.append(esc(str(getattr(value, "contents", value))).strip())
            out.append("")
        else:
            # Fallback: render any other section's text representation.
            val = section.value
            if isinstance(val, str):
                out.append("")
                out.append(esc(val).strip())
                out.append("")
    return out


def render_function(func, level: int) -> list[str]:
    out: list[str] = []
    heading = "#" * level
    labels = set(func.labels)
    badges = []
    if {"property", "cached"} & labels:
        badges.append("property")
    if "staticmethod" in labels:
        badges.append("staticmethod")
    if "classmethod" in labels:
        badges.append("classmethod")
    suffix = f" _{' · '.join(badges)}_" if badges else ""
    out.append(f"{heading} `{func.name}`{suffix}")
    out.append("")
    out.append("```python")
    out.append(format_signature(func))
    out.append("```")
    out.extend(render_docstring_sections(func.docstring, level + 1))
    out.append("")
    return out


def render_class(cls, level: int) -> list[str]:
    out: list[str] = []
    heading = "#" * level
    out.append(f"{heading} `class {cls.name}`")
    out.append("")
    out.extend(render_docstring_sections(cls.docstring, level + 1))

    # Class-level attributes that carry their own docstrings.
    attrs = [
        m
        for n, m in cls.members.items()
        if m.kind.value == "attribute" and is_public(n) and m.docstring
    ]
    if attrs:
        out.append("")
        out.append("**Attributes**")
        out.append("")
        out.append("| Name | Type | Description |")
        out.append("| --- | --- | --- |")
        for a in attrs:
            typ = f"`{esc(annotation_str(a.annotation))}`" if a.annotation else ""
            out.append(f"| `{a.name}` | {typ} | {esc(first_line(a.docstring))} |")
        out.append("")

    methods = [
        m
        for n, m in cls.members.items()
        if m.kind.value == "function" and is_public(n) and not m.is_alias
    ]
    # Keep source order; put __init__ first.
    methods.sort(key=lambda m: (m.name != "__init__", m.lineno or 0))
    documented = [m for m in methods if m.docstring or m.name == "__init__"]
    if documented:
        out.append("")
        out.append("**Methods**")
        out.append("")
        # Methods are one heading level below the class so they nest under it
        # in the on-page table of contents.
        for m in documented:
            out.extend(render_function(m, level + 1))
    return out


def render_module(module) -> str | None:
    classes = [
        m
        for n, m in module.members.items()
        if m.kind.value == "class" and is_public(n) and not m.is_alias
    ]
    functions = [
        m
        for n, m in module.members.items()
        if m.kind.value == "function" and is_public(n) and not m.is_alias
    ]
    # Re-exported names (aliases) — useful on package __init__ pages.
    reexports = [
        n
        for n, m in module.members.items()
        if m.is_alias and is_public(n)
    ]

    # Skip package ``__init__`` pages that are nothing but re-exports — they
    # add a redundant leaf next to the auto-generated group. Keep them only
    # when the package has its own docstring or defines real objects.
    if module.is_init_module and not classes and not functions and not module.docstring:
        return None

    has_content = bool(classes or functions or module.docstring or reexports)
    if not has_content:
        return None

    # Sidebar leaves should show just the module/package name, not the full
    # dotted path. Package overview pages are labelled "Overview".
    leaf = module.path.split(".")[-1]
    title = "Overview" if module.is_init_module else leaf
    desc = first_line(module.docstring) or f"API reference for `{module.path}`."

    lines: list[str] = []
    lines.append("---")
    lines.append(f"title: {yaml_quote(title)}")
    lines.append(f"description: {yaml_quote(desc)}")
    if module.is_init_module:
        # Sort the package overview to the top of its sidebar group.
        lines.append("sidebar:")
        lines.append("  order: 0")
    lines.append("---")
    lines.append("")
    # Keep the fully-qualified path visible on the page itself.
    lines.append(f"`{module.path}`")
    lines.append("")

    if module.docstring:
        lines.extend(render_docstring_sections(module.docstring, 2))

    if not classes and not functions and reexports:
        lines.append("")
        lines.append("This module re-exports the following names:")
        lines.append("")
        for n in sorted(reexports):
            lines.append(f"- `{n}`")
        lines.append("")

    for cls in sorted(classes, key=lambda c: c.lineno or 0):
        lines.append("")
        lines.extend(render_class(cls, 2))

    if functions:
        lines.append("")
        lines.append("## Functions")
        lines.append("")
        for func in sorted(functions, key=lambda f: f.lineno or 0):
            lines.extend(render_function(func, 3))

    return "\n".join(lines).rstrip() + "\n"


def walk_modules(obj):
    """Yield every (non-ignored) module object in the package tree."""
    if is_ignored(obj.path):
        return
    if obj.is_module and not obj.is_alias:
        yield obj
    for member in obj.members.values():
        if member.is_alias:
            continue
        if member.is_module:
            yield from walk_modules(member)


def module_to_path(module) -> Path:
    """Map a dotted module path to an MDX file under OUT_DIR."""
    parts = module.path.split(".")[1:]  # drop the leading 'pyDataverse'
    if module.is_init_module:
        # Kept package overview -> <dir>/package-overview.mdx, inside its own
        # group. The hyphen guarantees no clash with a real module name.
        return OUT_DIR.joinpath(*parts, "package-overview.mdx")
    return OUT_DIR.joinpath(*parts).with_suffix(".mdx")


def main() -> None:
    pkg = griffe.load(
        PACKAGE,
        search_paths=[str(REPO_ROOT)],
        docstring_parser="google",
    )

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    for module in walk_modules(pkg):
        if module.path == PACKAGE:
            continue  # root package -> handled by the landing page below
        content = render_module(module)
        if content is None:
            continue
        out_path = module_to_path(module)
        if out_path.exists():
            raise RuntimeError(
                f"Output path collision for {module.path}: {out_path} already "
                "exists (rename the conflicting module or adjust module_to_path)."
            )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        written += 1
        print(f"  {module.path} -> {out_path.relative_to(REPO_ROOT)}")

    # Landing page for the whole section.
    index = OUT_DIR / "overview.mdx"
    if True:
        index.write_text(
            "---\ntitle: \"API Reference\"\n"
            "description: \"Auto-generated API reference for all pyDataverse modules.\"\n"
            "---\n\n"
            "This section documents every public module, class, function and "
            "method in the `pyDataverse` package. Pages are generated directly "
            "from the source code and docstrings using "
            "[griffe](https://mkdocstrings.github.io/griffe/).\n",
            encoding="utf-8",
        )

    print(f"\nGenerated {written} module pages under {OUT_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()

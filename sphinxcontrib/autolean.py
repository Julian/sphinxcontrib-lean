from collections import defaultdict
from pathlib import Path
from textwrap import dedent, indent
import json
import os
import subprocess
import sys


def md_to_rst(markdown):
    # FIXME: Use recommonmark if I can figure out how to use it
    return subprocess.run(
        [
            "pandoc",
            "--from", "markdown", "--to", "rst",
            "--shift-heading-level-by", "1",
        ],
        input=markdown.encode(),
        capture_output=True,
    ).stdout.decode()


def to_code_block(markdown):
    return f"\n\n.. code-block:: {markdown['language']}\n" + indent(
        markdown["contents"],
        prefix="    ",
    )


def strip(name, prefix):
    if name.startswith(prefix + "."):
        return name[len(prefix) + 1:]
    return name


def axiom(decl, module):
    pass


def constant(decl, module):
    if decl["structure_fields"]:
        fields = "\n\n    Fields:\n\n" + indent(
            "\n\n".join(
                structure_field(each, decl["name"])
                for each in decl["structure_fields"]
            ),
            prefix="        ",
        )
    else:
        fields = ""

    return f".. constant:: {strip(decl['name'], module)}\n\n" + indent(
        md_to_rst(decl["doc_string"]),
        prefix="    ",
    ) + fields + "\n"


def definition(decl, module):
    return f".. definition:: {strip(decl['name'], module)}\n\n" + indent(
        md_to_rst(decl["doc_string"]),
        prefix="    ",
    )


def theorem(decl, module):
    return f".. theorem:: {strip(decl['name'], module)}\n\n" + indent(
        md_to_rst(decl["doc_string"]),
        prefix="    ",
    ) + "\n"


def structure_field(field, structure):
    field_name, type = field
    return f".. field:: {strip(field_name, structure)}\n"


emitters = {
    "cnst": constant,
    "def": definition,
    "thm": theorem,
}


exported = os.environ.get("SPHINX_EXPORTED_LEAN")
if exported is not None:
    with open(exported) as file:
        contents = json.load(file)
else:
    EXPORTER = Path(__file__).parent / "leansrc" / "export_json.lean"
    ran = subprocess.run(["lean", "--run", EXPORTER], capture_output=True)
    contents = json.loads(ran.stdout)


sys.stdout.write(
    dedent(
        """\
        =============
        API Reference
        =============
        """,
    ),
)

by_filename = defaultdict(list)
for decl in contents["decls"]:
    by_filename[decl["filename"]].append(decl)


# FIXME: I don't see anywhere on module_info (i.e. in export_json.lean)
#        a way to convert module *id to name*, rather than vice versa (i.e.
#        path to dotted name)
def _name_of(path):
    _, _, tail = path.rpartition("src/")
    if tail.endswith("/default.lean"):
        name = tail[:-len("/default.lean")]
    else:
        name, _ = os.path.splitext(tail)
    return name.replace("/", ".")


by_name = sorted((_name_of(k), (k, v)) for k, v in by_filename.items())

for module, (path, decls) in by_name:
    sys.stdout.write("\n``")
    sys.stdout.write(module)
    sys.stdout.write("``\n")
    sys.stdout.write("=" * (len(module) + 4))
    sys.stdout.write("\n\n")

    if path in contents["mod_docs"]:
        module_doc = contents["mod_docs"][path]
        if len(module_doc) != 1:
            raise RuntimeError("mod_docs somehow has len > 1")
        as_rst = md_to_rst(module_doc[0]["doc"].rstrip())
        sys.stdout.write(as_rst)
        sys.stdout.write("\n\n")

    for each in sorted(decls, key=lambda decl: decl["name"]):
        sys.stdout.write("\n")
        sys.stdout.write(emitters[each["kind"]](each, module=module))

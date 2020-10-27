from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.domains import Domain, ObjType
from sphinx.locale import _, __
from sphinx.roles import XRefRole
from sphinx.util import logging
import attr
import sphinx.directives
import sphinx.util.docutils
import sphinx.util.nodes

logger = logging.getLogger(__name__)


pairindextypes = {
    "module":    _("module"),
}


class ModuleDirective(sphinx.util.docutils.SphinxDirective):

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "platform": lambda x: x,
        "synopsis": lambda x: x,
        "noindex": directives.flag,
        "deprecated": directives.flag,
    }

    def run(self):
        domain = self.env.get_domain("lean")
        modname = self.arguments[0].strip()
        self.env.ref_context["lean:module"] = modname
        ret = []
        if "noindex" not in self.options:
            # note module to the domain
            node_id = sphinx.util.nodes.make_id(
                self.env, self.state.document, "module", modname,
            )
            target = nodes.target("", "", ids=[node_id], ismod=True)
            self.set_source_info(target)

            self.state.document.note_explicit_target(target)

            domain.note_module(modname,
                               node_id,
                               self.options.get("synopsis", ""),
                               self.options.get("platform", ""),
                               "deprecated" in self.options)
            domain.note_object(modname, "module", node_id, location=target)

            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(target)
            indextext = "%s; %s" % (pairindextypes["module"], modname)
            inode = addnodes.index(
                entries=[("pair", indextext, node_id, "", None)],
            )
            ret.append(inode)
        return ret


class LeanObjectDescription(sphinx.directives.ObjectDescription):
    def handle_signature(self, sig, signode):
        signode += addnodes.desc_annotation(self.lean_kind, self.lean_kind)
        signode += addnodes.desc_name(" " + sig, " " + sig)
        return sig


class ConstantDirective(LeanObjectDescription):

    lean_kind = "constant"


class DefinitionDirective(LeanObjectDescription):

    lean_kind = "def"


class TheoremDirective(LeanObjectDescription):

    lean_kind = "theorem"


class StructureFieldDirective(LeanObjectDescription):

    lean_kind = "field"


class Lean(Domain):

    name = label = "lean"
    object_types = {
        "constant": ObjType(_("constant"), "constant", "obj"),
        "definition": ObjType(_("definition"), "definition", "obj"),
        "theorem": ObjType(_("theorem"), "theorem", "obj"),
        "field": ObjType(_("field"), "field", "obj"),
    }

    directives = dict(
        constant=ConstantDirective,
        definition=DefinitionDirective,
        field=StructureFieldDirective,
        theorem=TheoremDirective,
        module=ModuleDirective,
    )

    roles = {
        "constant": XRefRole(),
        "definition": XRefRole(),
        "theorem": XRefRole(),
        "field": XRefRole(),
    }

    @property
    def modules(self):
        return self.data.setdefault("modules", {})

    def note_module(self, name, node_id, synopsis, platform, deprecated):
        """
        Note a Lean module for cross reference.
        """

        self.modules[name] = ModuleEntry(
            self.env.docname, node_id, synopsis, platform, deprecated,
        )

    @property
    def objects(self):
        return self.data.setdefault("objects", {})

    def note_object(
        self, name, objtype, node_id, canonical=False, location=None,
    ):
        """
        Note a Lean object for cross reference.
        """
        if name in self.objects:
            other = self.objects[name]
            logger.warning(
                __("duplicate object description of %s, "
                   "other instance in %s, use :noindex: for one of them"),
                name, other.docname, location=location,
            )
        self.objects[name] = ObjectEntry(
            self.env.docname, node_id, objtype, canonical,
        )


@attr.define
class ModuleEntry:
    docname: str
    node_id: str
    synopsis: str
    platform: str
    deprecated: bool


@attr.define
class ObjectEntry:
    docname: str
    node_id: str
    objtype: str
    canonical: bool


def setup(app):
    app.add_domain(Lean)

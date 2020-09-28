from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.locale import _, __
from sphinx.util import logging
import attr
import sphinx.addnodes
import sphinx.directives
import sphinx.domains
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
            inode = sphinx.addnodes.index(
                entries=[("pair", indextext, node_id, "", None)],
            )
            ret.append(inode)
        return ret


class ConstantDirective(sphinx.directives.ObjectDescription):
    pass


class DefinitionDirective(sphinx.directives.ObjectDescription):
    pass


class TheoremDirective(sphinx.directives.ObjectDescription):
    pass


class StructureFieldDirective(sphinx.directives.ObjectDescription):
    pass


class Lean(sphinx.domains.Domain):

    name = label = "lean"

    directives = dict(
        constant=ConstantDirective,
        definition=DefinitionDirective,
        field=StructureFieldDirective,
        theorem=TheoremDirective,
        module=ModuleDirective,
    )

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

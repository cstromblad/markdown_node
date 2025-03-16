import logging
import json
import uuid

from markdown_graph import graph
from markdown_graph.mitre.intrusionset import IntrusionSet
from markdown_graph.mitre.techniques import AttackTechnique

network = graph.MarkdownNodeNetwork("data/test-network")

parent_node = network.create_node("MITRE - Intrusion Sets")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

with open("data/mitre-intrusion-set.json") as fd:
    intrusion_sets = json.load(fd)

with open("data/mitre-attack-pattern.json") as fd:
    techniques = json.load(fd)

for intrusion_set_dict in intrusion_sets["values"]:
    try:
        intrusion_set = IntrusionSet.model_validate(intrusion_set_dict)
    except Exception as e:
        logger.warning(f"Could not create intrusion_set: {e}")
        continue

    print(f"Adding {intrusion_set.name} to the network!")

    node = network.create_node(intrusion_set.name)  # name of the intrusion set
    node.uuid = uuid.UUID(intrusion_set.uuid)

    node = node.add_section("synonyms")
    if intrusion_set.meta.synonyms:
        node.section_data("synonyms", intrusion_set.meta.synonyms)

    if intrusion_set.techniques:
        for t in intrusion_set.techniques:
            if t.type == "uses":
                for tech_dict in techniques["values"]:
                    tech = AttackTechnique.model_validate(tech_dict)
                    if tech.uuid == t.dest_uuid:
                        t_node = network.create_node(
                            tech.name, storage_location="techniques"
                        )
                        _ = t_node.add_header("Description", tech.description)
                        _ = node.connect(t_node)

    _ = parent_node.connect(node)


network.draw()

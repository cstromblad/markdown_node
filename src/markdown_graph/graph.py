import json
import os
from typing import override
import uuid

from pathlib import Path


class Node:
    def __init__(self, name: str = ""):
        self.uuid: uuid.UUID = uuid.uuid4()
        self._display_name: str = name.replace("/", " - ")
        self._visible: bool = False

        self._edges: list[Edge] = []

    @override
    def __repr__(self):
        return f'Node("{self._display_name}")'

    @override
    def __str__(self):
        return f"{self._display_name}"

    def connect(self, other_node: "Node"):
        for edge in self._edges:
            if other_node.display_name == edge.right_node.display_name:
                return edge.right_node
            elif other_node.display_name == edge.left_node.display_name:
                return edge.left_node

        edge = Edge(self, other_node)
        self._edges.append(edge)

        edge = Edge(other_node, self)
        other_node._edges.append(edge)

    def disconnect(self, node: "Node"):
        for edge in self._edges:
            if node in edge.nodes:
                self._edges.remove(edge)
                node._edges.remove(edge)
                break

    def siblings(self):
        for edge in self._edges:
            if edge.nodes[0] == self:
                yield edge.nodes[1]
            else:
                yield edge.nodes[0]

    @property
    def display_name(self):
        return self._display_name

    @property
    def edges(self):
        return self._edges


class Edge:
    def __init__(self, this_node: Node, another_node: Node):
        self.left_node: Node = this_node
        self.right_node: Node = another_node

    @property
    def nodes(self):
        return (self.left_node, self.right_node)


class NodeNetwork:
    def __init__(self):
        self.nodes: list[Node] = []

    def __iter__(self):
        for node in self.nodes:
            yield (node)

    def add_node(self, new_node: Node) -> Node:
        self.nodes.append(new_node)
        return new_node

    def remove_node(self, node: Node):
        # First remove all edges connected to the node
        for edge in node.edges:
            node.disconnect(edge)

        self.nodes.remove(node)

    def find_node(self, display_name: str):
        for node in self.nodes:
            if node.display_name == display_name:
                return node

        return None

    def draw(self):
        for node in self.nodes:
            for sibling in node.siblings():
                print(f"{node} <-> {sibling}")


class MarkdownNode(Node):
    def __init__(self, display_name: str, storage_location: str = ""):
        super().__init__(display_name)

        self._sections: dict[str, str] = {}
        self._headers: dict[str, str] = {}
        self._storage_location: str = storage_location

    @override
    def __eq__(self, other: Node):
        if self.display_name == other.display_name:
            return True
        else:
            return False

    def add_header(self, header_name: str, content: str = ""):
        if not self._headers.get(header_name):
            self._headers[header_name] = content

    def add_section(self, section_name: str) -> "MarkdownNode":
        if not self.sections.get(section_name):
            self.sections[section_name] = {}

        return self

    def section_data(self, section_name: str, data: list[str]):
        self.sections[section_name] = data
        return

    @property
    def storage_location(self):
        return self._storage_location

    @property
    def sections(self):
        return self._sections

    @sections.setter
    def sections(self, section_name: str, value: list[str]):
        self._sections[section_name] = value

    def section(self, name: str):
        return self._sections.get(name, "")

    def as_markdown(self):
        # Headers + content
        headers = ""
        for header in self._headers.keys():
            headers += f"## {header}\n"
            headers += self._headers[header]
            headers += "\n\n"

        # Other nodes (siblings)
        md_siblings = ""

        for sibling in self.siblings():
            md_siblings += f"[[{sibling.display_name}]]\n"

        md_siblings += "\n\n"

        # Sections
        md_representation = ""
        for section, data in self._sections.items():
            md_representation += f"```{section}\n"
            md_representation += json.dumps(data)
            md_representation += "\n```\n\n"

        return headers + md_siblings + md_representation


class MarkdownNodeNetwork(NodeNetwork):
    def __init__(self, storage_location: str = "data"):
        super().__init__()

        self.storage_location: str = storage_location

    def create_node(
        self, display_name: str, storage_location: str = ""
    ) -> MarkdownNode:
        node = MarkdownNode(display_name, storage_location)
        node = self.add_node(node)

        return node

    @override
    def add_node(self, new_node: MarkdownNode) -> MarkdownNode:
        for node in self.nodes:
            if node == new_node:
                # node.merge(new_node)
                return node

        self.nodes.append(new_node)
        return new_node

    @override
    def draw(self):
        for node in self.nodes:
            if node.storage_location:
                path = f"{self.storage_location}/{node.storage_location}"
                p = Path(path)
                if not p.exists():
                    os.makedirs(path)

                storage_location = f"{path}/{node.display_name}.md"
            else:
                storage_location = f"{self.storage_location}/{node.display_name}.md"
            with open(storage_location, "w") as node_fd:
                node_fd.write(node.as_markdown())

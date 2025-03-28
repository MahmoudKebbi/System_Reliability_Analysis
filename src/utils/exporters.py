"""
Functions to export reliability systems to various formats.
"""

import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Dict, Any, Optional
from src.models.system import SystemGraph


def export_to_json(system: SystemGraph, filename: str):
    """
    Export system to JSON file.

    Args:
        system: SystemGraph to export
        filename: Path to output JSON file
    """
    data = {
        "name": system.name if hasattr(system, "name") else "Reliability System",
        "components": [],
        "connections": [],
    }

    # Add components
    for comp_id, component in system.components.items():
        comp_data = {"id": comp_id, "name": component.name}

        if component.description:
            comp_data["description"] = component.description

        if component.failure_distribution is not None:
            if hasattr(component.failure_distribution, "failure_rate"):
                comp_data["failure_rate"] = component.failure_distribution.failure_rate

        data["components"].append(comp_data)

    # Add connections
    for edge in system.graph.edges():
        data["connections"].append({"from": edge[0], "to": edge[1]})

    # Write to file
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def export_to_xml(system: SystemGraph, filename: str):
    """
    Export system to XML file.

    Args:
        system: SystemGraph to export
        filename: Path to output XML file
    """
    root = ET.Element("system")
    root.set("name", system.name if hasattr(system, "name") else "Reliability System")

    # Add components
    components_elem = ET.SubElement(root, "components")

    for comp_id, component in system.components.items():
        comp_elem = ET.SubElement(components_elem, "component")
        comp_elem.set("id", comp_id)
        comp_elem.set("name", component.name)

        if component.failure_distribution is not None:
            if hasattr(component.failure_distribution, "failure_rate"):
                comp_elem.set(
                    "failure_rate", str(component.failure_distribution.failure_rate)
                )

        if component.description:
            desc_elem = ET.SubElement(comp_elem, "description")
            desc_elem.text = component.description

    # Add connections
    connections_elem = ET.SubElement(root, "connections")

    for edge in system.graph.edges():
        conn_elem = ET.SubElement(connections_elem, "connection")
        conn_elem.set("from", edge[0])
        conn_elem.set("to", edge[1])

    # Format and write to file
    rough_string = ET.tostring(root, "utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open(filename, "w") as f:
        f.write(pretty_xml)

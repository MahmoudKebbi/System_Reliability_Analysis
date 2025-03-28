"""
Functions to import reliability systems from various formats.
"""

import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from src.models.system import SystemGraph
from src.models.components import Component, ExponentialDistribution


def import_from_json(filename: str) -> SystemGraph:
    """
    Import system from JSON file.

    JSON format:
    {
        "name": "System Name",
        "components": [
            {
                "id": "C1",
                "name": "Component 1",
                "description": "Description",
                "failure_rate": 0.01
            },
            ...
        ],
        "connections": [
            {
                "from": "source",
                "to": "C1"
            },
            ...
        ]
    }

    Args:
        filename: Path to JSON file

    Returns:
        Imported SystemGraph
    """
    with open(filename, "r") as f:
        data = json.load(f)

    system = SystemGraph()

    # Set system name if provided
    if "name" in data:
        system.name = data["name"]

    # Add components
    for comp_data in data.get("components", []):
        failure_rate = comp_data.get("failure_rate", 0.01)
        component = Component(
            id=comp_data.get("id"),
            name=comp_data.get("name"),
            description=comp_data.get("description"),
            failure_distribution=ExponentialDistribution(failure_rate),
        )
        system.add_component(component)

    # Add connections
    for conn in data.get("connections", []):
        from_id = conn.get("from")
        to_id = conn.get("to")
        system.add_connection(from_id, to_id)

    return system


def import_from_xml(filename: str) -> SystemGraph:
    """
    Import system from XML file.

    XML format:
    <system name="System Name">
        <components>
            <component id="C1" name="Component 1" failure_rate="0.01">
                <description>Description</description>
            </component>
            ...
        </components>
        <connections>
            <connection from="source" to="C1" />
            ...
        </connections>
    </system>

    Args:
        filename: Path to XML file

    Returns:
        Imported SystemGraph
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    system = SystemGraph()

    # Set system name if provided
    if "name" in root.attrib:
        system.name = root.attrib["name"]

    # Add components
    for comp_elem in root.findall("./components/component"):
        comp_id = comp_elem.attrib.get("id")
        comp_name = comp_elem.attrib.get("name")
        failure_rate = float(comp_elem.attrib.get("failure_rate", 0.01))

        # Get description if available
        desc_elem = comp_elem.find("description")
        description = desc_elem.text if desc_elem is not None else None

        component = Component(
            id=comp_id,
            name=comp_name,
            description=description,
            failure_distribution=ExponentialDistribution(failure_rate),
        )
        system.add_component(component)

    # Add connections
    for conn_elem in root.findall("./connections/connection"):
        from_id = conn_elem.attrib.get("from")
        to_id = conn_elem.attrib.get("to")
        system.add_connection(from_id, to_id)

    return system

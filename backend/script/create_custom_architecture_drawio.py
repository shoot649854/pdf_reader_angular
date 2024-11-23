import xml.dom.minidom
import xml.etree.ElementTree as ET


def create_drawio_diagram():
    # Create root element
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2023-10-10T12:00:00.000Z",
            "agent": "python-script",
            "etag": "abcd1234",
            "version": "16.0.0",
            "type": "device",
        },
    )

    # Add diagram
    diagram = ET.SubElement(mxfile, "diagram", {"id": "diagram-id", "name": "Page-1"})

    # Add mxGraphModel
    mxGraphModel = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1422",
            "dy": "794",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "850",
            "pageHeight": "1100",
        },
    )

    # Add root
    root = ET.SubElement(mxGraphModel, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # Add first rectangle
    rect1 = ET.SubElement(
        root,
        "mxCell",
        {
            "id": "2",
            "value": "Rectangle 1",
            "style": "rounded=0;whiteSpace=wrap;html=1;",
            "vertex": "1",
            "parent": "1",
        },
    )
    geom1 = ET.SubElement(
        rect1,
        "mxGeometry",
        {"x": "100", "y": "100", "width": "120", "height": "60", "as": "geometry"},
    )
    geom1.set("relative", "0")

    # Add second rectangle
    rect2 = ET.SubElement(
        root,
        "mxCell",
        {
            "id": "3",
            "value": "Rectangle 2",
            "style": "rounded=0;whiteSpace=wrap;html=1;",
            "vertex": "1",
            "parent": "1",
        },
    )
    geom2 = ET.SubElement(
        rect2,
        "mxGeometry",
        {"x": "300", "y": "100", "width": "120", "height": "60", "as": "geometry"},
    )
    geom2.set("relative", "0")

    # Add connector
    connector = ET.SubElement(
        root,
        "mxCell",
        {
            "id": "4",
            "value": "",
            "style": "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;loopDirection=0;",
            "edge": "1",
            "parent": "1",
            "source": "2",
            "target": "3",
        },
    )
    geom_conn = ET.SubElement(
        connector, "mxGeometry", {"relative": "1", "as": "geometry"}
    )

    # Convert to string
    xml_str = ET.tostring(mxfile, encoding="utf-8")
    parsed_xml = xml.dom.minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    # Save to file
    with open("diagram.drawio", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print("diagram.drawio has been created successfully.")


if __name__ == "__main__":
    create_drawio_diagram()

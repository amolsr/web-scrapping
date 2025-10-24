import csv
import json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import os

class OutputManager:
    def __init__(self, output_dir='output'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_to_csv(self, data, filename):
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        print(f"Data saved to {path}")

    def save_to_json(self, data, filename):
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {path}")

    def save_to_xml(self, data, filename):
        root = ET.Element("items")
        for item in data:
            item_elem = ET.SubElement(root, "item")
            for key, val in item.items():
                child = ET.SubElement(item_elem, key.replace(" ", "_"))
                child.text = str(val)
        
        # Pretty print
        xml_str = ET.tostring(root, 'utf-8')
        dom = parseString(xml_str)
        pretty_xml_str = dom.toprettyxml(indent="  ")

        path = os.path.join(self.output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(pretty_xml_str)
        print(f"Data saved to {path}")

    def save(self, data, filename_base, format='csv'):
        if not data:
            print("No data to save.")
            return

        format = format.lower()
        if format == 'csv':
            self.save_to_csv(data, f"{filename_base}.csv")
        elif format == 'json':
            self.save_to_json(data, f"{filename_base}.json")
        elif format == 'xml':
            self.save_to_xml(data, f"{filename_base}.xml")
        else:
            print(f"Unsupported format: {format}")


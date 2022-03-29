import sys
import json

def build_db_row_from_block(block_json_path):
    """
    Given a JSON file of Textract blocks, add a row to the database.
    """

    with open(block_json_path) as f:
        block_json = json.load(f)

    pdf_features = []
    for i, page in enumerate(block_json):
        for block in page:
            block_geometry = block.pop('Geometry')
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": []
                },
                "properties": block
            }

            feature['properties']['page_num'] = i
            feature['properties']['file_name'] = block_json_path

            coords = [[p["X"], p["Y"]] for p in block_geometry['Polygon']]
            ring = coords + [ coords[0] ]

            feature['geometry']['coordinates'] = [ring]
            pdf_features.append(feature)

    return pdf_features

def main():
    json_blocks_file = sys.argv[1]

    with open(json_blocks_file) as f:
        json_paths = [line.strip() for line in f.readlines()]

    geojson = { "type": "FeatureCollection",
               "features": []
               }

    for json_path in json_paths:
        geojson['features'] += build_db_row_from_block(json_path)

    json.dump(geojson, sys.stdout)

if __name__ == '__main__':
    main()

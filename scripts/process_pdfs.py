import sys
import os
import json
import boto3
from pdf2image import convert_from_path
from textract import Textract


def main():
    """
    Command line argument is the location of the PDF.
    """
    pdf_path = sys.argv[1]
    pdf_file_name = os.path.basename(pdf_path)
    pdf_name, _ = os.path.splitext(pdf_file_name)

    client = boto3.client('textract')
    textract = Textract(client)

    # pdf2image will produce one image for every page of the PDF
    page_paths = []
    print('\nConverting PDF to images...')
    pages = convert_from_path(pdf_path, fmt='png', output_folder='raw', output_file=pdf_name)
    for page in pages:
        page_paths.append(page.filename)

    # combine Textract's output for each of the images associated
    # with a PDF file
    all_blocks = []
    print('Fetching Textract blocks...')
    for path in page_paths:
        blocks = textract.detect_file_text(document_file_name=path)['Blocks']
        for block in blocks:
            all_blocks.append(block)

    # get the key value pairs for the form data in the PDF
    results = []
    key_map, value_map, block_map = textract.get_kv_map(all_blocks)
    kvs = textract.get_kv_relationship(key_map, value_map, block_map)
    results.append(kvs)

    print('Writing output...')
    with open(f'final/{pdf_name}.json', 'w') as output:
        output.write(json.dumps(results))

    print('Done!\n')

if __name__ == '__main__':
    main()

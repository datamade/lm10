import sys
import json
import boto3
from pathlib import PurePath
from pdf2image import convert_from_path
from textract import Textract


def main():
    """
    Command line argument is the location of the PDF.
    """
    pdf_path = sys.argv[1]
    pdf_name = PurePath(pdf_path).stem

    client = boto3.client('textract')
    textract = Textract(client)

    # pdf2image will produce one image for every page of the PDF
    print('\nConverting PDF to images...')
    pages = convert_from_path(pdf_path, fmt='png', output_folder='raw', output_file=pdf_name)

    # combine Textract's output for each of the images associated
    # with a PDF file
    all_blocks = []
    print('Fetching Textract blocks...')
    for page in pages:
        blocks = textract.detect_file_text(document_file_name=page.filename)['Blocks']
        all_blocks.extend(blocks)

    # get the key value pairs for the form data in the PDF
    key_map, value_map, block_map = textract.get_kv_map(all_blocks)
    form_key_values = textract.get_kv_relationship(key_map, value_map, block_map)

    print('Writing output...')
    with open(f'final/{pdf_name}.json', 'w') as output:
        output.write(json.dumps(form_key_values))

    print('Done!\n')

if __name__ == '__main__':
    main()

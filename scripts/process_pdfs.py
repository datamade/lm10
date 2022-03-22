import sys
import json
import boto3
from tqdm import tqdm
from pathlib import PurePath
from pdf2image import convert_from_path
from textract import Textract


def main():
    """
    Command line argument is the location of the PDF.
    """
    pdf_paths_file_name = sys.argv[1]

    client = boto3.client('textract')
    textract = Textract(client)

    with open(pdf_paths_file_name) as f:
        pdf_paths = [line.strip() for line in f.readlines()]

    for pdf_path in tqdm(pdf_paths):
        print(f'\nProcessing {pdf_path}')
        pdf_name = PurePath(pdf_path).stem

        # pdf2image will produce one image for every page of the PDF
        print('Converting PDF to images...')
        pages = convert_from_path(pdf_path, fmt='png', output_folder='images', output_file=pdf_name)

        # combine Textract's output for each of the images associated
        # with a PDF file
        page_blocks = []
        page_key_values = []
        print('Fetching Textract blocks...')
        for i, page in enumerate(pages):
            blocks = textract.detect_file_text(document_file_name=page.filename)['Blocks']
            page_blocks.append(blocks)

            # get the key value pairs for the form data in the page
            key_map, value_map, block_map = textract.get_kv_map(blocks)
            page_key_values.append(textract.get_kv_relationship(key_map, value_map, block_map))

        print('Writing output...')
        with open(f'textract_responses/{pdf_name}.json', 'w') as raw_output:
            json.dump(page_blocks, raw_output, indent=4)

        with open(f'final/{pdf_name}.json', 'w') as processed_output:
            json.dump(page_key_values, processed_output, indent=4)

    print('Done!\n')

if __name__ == '__main__':
    main()

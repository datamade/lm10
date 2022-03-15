import logging
from botocore.exceptions import ClientError


class Textract:
    """Encapsulates Textract functions."""
    def __init__(self, textract_client):
        """
        :param textract_client: A Boto3 Textract client.
        """
        self.textract_client = textract_client

    def detect_file_text(self, *, document_file_name=None, document_bytes=None):
        """
        Detects form elements in a local image file or from in-memory byte data.
        The image must be in PNG or JPG format.

        :param document_file_name: The name of a document image file.
        :param document_bytes: In-memory byte data of a document image.
        :return: The response from Amazon Textract, including a list of blocks
                 that describe elements detected in the image.
        """
        logger = logging.getLogger()
        if document_file_name is not None:
            with open(document_file_name, 'rb') as document_file:
                document_bytes = document_file.read()
        try:
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS'])
            logger.info(
                "Detected %s blocks.", len(response['Blocks']))
        except ClientError:
            logger.exception("Couldn't detect text.")
            raise
        else:
            return response

    def get_kv_map(self, blocks):
        """
        Creates dictionaries that will be used by find_value_block and
        get_text.

        :param blocks: Blocks returned by Amazon Textract
        :return: Three dictionaries: one that maps keys to their blocks,
        one that maps values to their block IDs, and one that maps blocks to
        their block IDs.
        """
        key_map = {}
        value_map = {}
        block_map = {}
        for block in blocks:
            block_id = block['Id']
            block_map[block_id] = block
            if block['BlockType'] == "KEY_VALUE_SET":
                if 'KEY' in block['EntityTypes']:
                    key_map[block_id] = block
                else:
                    value_map[block_id] = block

        return key_map, value_map, block_map

    def find_value_block(self, key_block, value_map):
        """
        Finds the the value block associated with a given key block.

        :param key_block: A key block.
        :param value_map: Dictionary returned by get_kv_map that maps values
        to their blocks.
        :return: The value block associated to the given key.
        """
        value_block = {}
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = value_map[value_id]

        return value_block

    def get_text(self, result, blocks_map):
        """
        Gets the text of a block.

        :param result: The block.
        :param blocks_map: Dictionary that maps blocks to their IDs.
        :return: The text of the given block.
        """
        text = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] == 'SELECTED':
                                text += 'X '

        return text

    def get_kv_relationship(self, key_map, value_map, block_map):
        """
        Finds the key-value pairs in the Textract response.

        :param key_map: Dictionary returned by get_kv_map that maps keys
        to blocks.
        :param value_map: Dictionary returned by get_kv_map that maps values
        to blocks.
        :param block_map: Dictionary returned by get_kv_map that maps blocks
        to block IDs.
        :return: The final key value dictionary that maps form keys to their values.
        """
        kvs = {}
        for block_id, key_block in key_map.items():
            value_block = self.find_value_block(key_block, value_map)
            key = self.get_text(key_block, block_map).strip().replace(':', '')
            val = self.get_text(value_block, block_map).strip()
            kvs[key] = val
        return kvs

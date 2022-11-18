import copy
import csv
import logging
from typing import Dict, List, Tuple

from .schemas import SCHEMAS


logger = logging.getLogger('IIF File Genrator')


class QBOIIFGenerator:
    """
    Generates IIF File for QBD
    """
    def __init__(self, file_path):
        self.filepath = file_path
    
    @staticmethod
    def __get_header(header_tuple: Tuple):
        """
        Remove ! from the first item of the header
        """
        header_copy = copy.deepcopy(header_tuple)
        header_copy[0] = header_tuple[0][1:]
        return header_copy
    
    def __write_list_of_tuples_to_iif(self, data: List(Tuple)):
        """
        Write list of tuples to csv file
        :param data: list of tuples
        :return: None
        """
        with open(self.file_path, 'w+') as csv_file:
            writer = csv.writer(csv_file, delimiter="\t", lineterminator="\r\n")
            writer.writerows(data)
        return
    
    def __create_split_lines(split_lines: List[Dict]):
        """
        Create tuples for split lines
        :param split_lines: Split lines array
        """
        lines = []
        for split_line in split_lines:
            lines.append(tuple(split_line.values))
        return lines

    def generate_iif_file(self, transactions: List[Dict], transaction_type: str) -> str:
        """
        Generate iif file for the given transaction type
        """
        schema = SCHEMAS[transaction_type]

        headers = {
            'transaction_header': self.__get_header(schema[0]),
            'split_line_header': self.__get_header(schema[1]),
            'end_transaction_header': self.__get_header(schema[2])
        }
        txns = []
        txns.extend(schema)

        for transaction in transactions:
            txns.append(tuple(transaction.values))

            split_lines: List[Dict] = transaction['split_lines']

            txns.extend(self.__create_split_lines(split_lines))

            txns.append(headers['end_transaction_header'])
        
        transactions = self.__write_list_of_tuples_to_iif(txns)

        return self.filepath

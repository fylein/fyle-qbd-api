import csv
import logging
from typing import Dict, List, Tuple

from .schemas import SCHEMAS


logger = logging.getLogger('IIF File Generator')


class QBDIIFGenerator:
    """
    Generates IIF File for QBD
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __write_list_of_tuples_to_iif(self, data: List[Tuple]):
        """
        Write list of tuples to csv file
        :param data: list of tuples
        :return: None
        """
        with open(self.file_path, 'w+') as csv_file:
            writer = csv.writer(csv_file, delimiter="\t", lineterminator="\r\n")
            writer.writerows(data)
    
    @staticmethod
    def __create_split_lines(split_lines: List[Dict]):
        """
        Create tuples for split lines
        :param split_lines: Split lines array
        """
        lines = []
        for split_line in split_lines:
            lines.append(tuple(split_line.values()))
        return lines

    def generate_iif_file(self, transactions: List[Dict], transaction_type: str) -> str:
        """
        Generate iif file for the given transaction type
        """
        schema = SCHEMAS[transaction_type]

        generated_transactions = []
        generated_transactions.extend(schema)

        for transaction in transactions:
            split_lines: List[Dict] = transaction['split_lines']
            
            del transaction['split_lines']

            generated_transactions.append(tuple(transaction.values()))

            generated_transactions.extend(self.__create_split_lines(split_lines))
            generated_transactions.append(('ENDTRNS',))
        
        self.__write_list_of_tuples_to_iif(generated_transactions)

        return generated_transactions

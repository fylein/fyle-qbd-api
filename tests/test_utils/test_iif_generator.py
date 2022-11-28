"""
Tests for all the functions in apps.utils.iif_generator.IIFGenerator
"""
from csv import reader
from apps.utils.iif_generator import QBDIIFGenerator

from .fixtures import fixtures


def test_constructor():
    """
    Initiatlise IIFGenerator class and check if the object is created with proper attributes
    """
    iif_generator = QBDIIFGenerator('/tmp/test.iif')

    assert iif_generator.file_path == '/tmp/test.iif'


def test_generate_iif_file_bills():
    """
    Test the generate_iif_file function
    """
    file_path = '/tmp/test_generator.csv'
    transactions = fixtures['bills']

    iif_generator = QBDIIFGenerator(file_path)

    generated_lines = iif_generator.generate_iif_file(transactions, 'BILL')

    with open(file_path, 'r') as iif_file:
        lines = list(reader(iif_file, delimiter='\t'))

        assert len(lines) == len(generated_lines)

        for index in range(0, len(lines)):
            generated_lines[index] = [str(element) for element in generated_lines[index]]
            assert lines[index] == generated_lines[index]

"""
Tests for all the functions in apps.utils.iif_generator.IIFGenerator
"""
from apps.utils.iif_generator import QBDIIFGenerator


def test_constructor():
    """
    Initiatlise IIFGenerator class and check if the object is created with proper attributes
    """
    iif_generator = QBDIIFGenerator('/tmp/test.iif')

    assert iif_generator.file_path == '/tmp/test.iif'

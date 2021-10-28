import pytest
from unittest import TestCase
from unittest.mock import Mock
from src.service import file_storage_service
from src.service.exception.file_exception import FileUploadEmpty

MOCK_OBJECT = Mock()


class TestFileStorageService(TestCase):

    def test_throw_file_upload_exception_on_empty_files(self):
        with pytest.raises(FileUploadEmpty):
            file_storage_service.validate_file([])

    def test_throw_file_upload_exception_on_invalid_files(self):
        with pytest.raises(FileUploadEmpty):
            file_storage_service.validate_file({'some': 'thing'})

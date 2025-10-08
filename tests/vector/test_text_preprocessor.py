import unittest
from typing import List

from api.vector.store import ContextEntry

from givenpy import given, when, then
from paths import TEST_DATA_DIR
from hamcrest import assert_that, instance_of, has_length, equal_to

from tests.vector.steps import prepare_mock_raw_data_preprocessor


class TestRawDataPreprocessor(unittest.TestCase):
    TEST_DATA_JSON = TEST_DATA_DIR / "test_data.json"

    def test_when_data_is_correct_then_a_list_of_context_entries_is_returned(self):
        with given([prepare_mock_raw_data_preprocessor()]) as context:
            preprocessor = context.preprocessor

        with when():
            text_entries: List[ContextEntry] = preprocessor.process_json_file(self.TEST_DATA_JSON)

        with then():
            assert_that(text_entries, instance_of(list))
            assert_that(text_entries, has_length(13))
            assert_that(text_entries[0], instance_of(ContextEntry))
            assert_that(text_entries[0].content.split("\n")[0], equal_to("<Integration Guides>"))

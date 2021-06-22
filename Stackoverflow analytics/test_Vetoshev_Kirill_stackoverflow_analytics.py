"""Unit-tests for task_Vetoshev_Kirill_stackoverflow_analytics.py"""

import pytest
from argparse import Namespace
from unittest.mock import patch
import task_Vetoshev_Kirill_stackoverflow_analytics as stack


DATASET_TINY = "./stack_overflow_posts_tiny.xml"
DATASET_TINY_STR = "after refactoring always some bugs will be appear"
TEST_DATE_YEAR_START = "2008"
TEST_DATE_YEAR_END = "2008"
TEST_RATING = {'sql': 3, 'computer': 35, 'vision': 36, 'hello': 197, 'world': 93}


def test_load_xml_file():
    """test load_file function"""
    document = stack.load_file(stack.DEFAULT_DATASET)
    assert len(document) == 325, (
        "failed to load xml file"
    )


def test_load_stop_words():
    """can load stopwords file"""
    stopwords = stack.load_stopwords_file(stack.DEFAULT_STOPWORDS_DATASET)
    assert len(stopwords) == 319, (
        "failed to load file with stopwords"
    )


@pytest.fixture
def remove_stopwords_tiny_dataset():
    """fixture to create document from default tiny dataset"""
    document = stack.load_file(DATASET_TINY)
    return document


@pytest.fixture
def stopwords_list_fixture():
    """fixture to load stopwords from default file"""
    stopwords = stack.load_stopwords_file(stack.DEFAULT_STOPWORDS_DATASET)
    return stopwords


@pytest.fixture
def cleaned_tiny_dataset(stopwords_list_fixture):
    """fixture, which generates cleaned default tiny dataset"""
    document = stack.load_file(DATASET_TINY)
    stack.remove_stopwords(document, stopwords_list_fixture)
    return document


@pytest.mark.parametrize(
    "reference_answer",
    [
        pytest.param(['setting', 'style', 'visible', 'tabitem', 'tabcontrol'], id="1"),
        pytest.param(
            ['distinguish', 'file', 'directory', 'perl'], id="2"),
        pytest.param(['file', 'path', 'size', 'c'], id="3"),
        pytest.param(['using', 'linq', 'concatenate', 'strings'], id="4"),
    ],
)
def test_remove_stopwords(remove_stopwords_tiny_dataset, stopwords_list_fixture, reference_answer):
    """test for function to remove stopwords from title's text"""
    stack.remove_stopwords(remove_stopwords_tiny_dataset, stopwords_list_fixture)
    answers = []
    for key in remove_stopwords_tiny_dataset.keys():
        answers.append(sorted(remove_stopwords_tiny_dataset[key][2]))
    assert sorted(reference_answer) in answers, (
        "stopwords are present in given title"
    )


def test_filter_data(cleaned_tiny_dataset):
    """test for function to remove outdated posts"""
    test_object = stack.StackOverflow(cleaned_tiny_dataset)
    test_object_filtered = test_object.filter_data_by_date(
        TEST_DATE_YEAR_START, TEST_DATE_YEAR_END)
    assert len(test_object_filtered) == 4, (
        "data wasn't filtered by start and end year"
    )


def test_build_rating_on_filtered_data(cleaned_tiny_dataset):
    """test for function to build rating field"""
    reference_answer = [('concatenate', 243), ('linq', 243), ('strings', 243), ('using', 243),
                        ('file', 14), ('directory', 13), ('distinguish', 13), ('perl', 13),
                        ('setting', 5), ('style', 5), ('tabcontrol', 5), ('tabitem', 5), ('visible', 5),
                        ('c', 1), ('path', 1), ('size', 1)]
    test_object = stack.StackOverflow(cleaned_tiny_dataset)
    test_object_filtered = test_object.filter_data_by_date(TEST_DATE_YEAR_START, TEST_DATE_YEAR_END)
    assert reference_answer == stack.top(test_object_filtered), (
        "rating was build incorrectly"
    )


@pytest.fixture
def stack_overflow_posts_tiny_object(cleaned_tiny_dataset):
    test_object = stack.StackOverflow(cleaned_tiny_dataset)
    test_object_filtered = test_object.filter_data_by_date(TEST_DATE_YEAR_START, TEST_DATE_YEAR_END)

    return test_object_filtered


@pytest.mark.parametrize(
    "start_year, end_year, top_n, reference_answer",
    [
        pytest.param(2008, 2008, 4, [('concatenate', 243), ('linq', 243),
                                     ('strings', 243), ('using', 243)], id="top 4"),
        pytest.param(2008, 2008, 5, [('concatenate', 243), ('linq', 243),
                                     ('strings', 243), ('using', 243), ('file', 14)], id="top 5"),
        pytest.param(2008, 2008, 10, [('concatenate', 243), ('linq', 243), ('strings', 243),
                                      ('using', 243), ('file', 14), ('directory', 13),
                                      ('distinguish', 13), ('perl', 13), ('setting', 5), ('style', 5)], id="top 10"),
    ],
)
def test_top_n(stack_overflow_posts_tiny_object, start_year, end_year, top_n, reference_answer):
    """test for function to yield top N words from rating"""
    answer = stack.top(stack_overflow_posts_tiny_object, top_n)
    assert reference_answer == answer, (
        f"incorrectly found {top_n} most rated words"
    )


def test_load_csv_file():
    """test for function to load csv file with queries"""
    reference_answer = [["2008", "2008", '4'],
                        ["2008", "2008", '1'],
                        ["2008", "2008", '5'],
                        ["2008", "2008", '10'],
                        ["2008", "2016", '4'],
                        ["2008", "2016", '5'],
                        ["1999", "1999", '5'],
                        ["2008", "2008", '1'],
                        ]
    queries = stack.load_csv_file(stack.TEST_CSV_FILE)
    assert reference_answer == queries, (
        "csv file loaded incorrectly"
    )


@patch("task_Vetoshev_Kirill_stackoverflow_analytics.load_file")
def test_callback_query(mock_load_file):
    arguments = Namespace(
        questions=DATASET_TINY,
        stop_words=stack.DEFAULT_STOPWORDS_DATASET,
        queries=stack.TEST_CSV_FILE,
    )
    stack.callback_query(arguments)
    assert 1 == mock_load_file.call_count


@patch("task_Vetoshev_Kirill_stackoverflow_analytics.load_stopwords_file")
def test_callback_query_2(mock_load_stopwords_file):
    arguments = Namespace(
        questions=DATASET_TINY,
        stop_words=stack.DEFAULT_STOPWORDS_DATASET,
        queries=stack.TEST_CSV_FILE,
    )
    stack.callback_query(arguments)
    assert 1 == mock_load_stopwords_file.call_count

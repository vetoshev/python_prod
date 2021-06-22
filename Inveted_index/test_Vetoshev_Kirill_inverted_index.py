import pytest
from textwrap import dedent
from task_Vetoshev_Kirill_inverted_index import InvertedIndex, build_inverted_index, load_documents

DATASET_BIG_FILE_PATH = './wikipedia_sample.txt'
DATASET_TINY_STR = dedent('''\
        123     some words A_word and nothing
        2       some word B_word in this dataset
        5       famous_phrases to be or not to be
        37      all words such A_word and B_word are here
    ''')


@pytest.fixture()
def tiny_dataset_fio(tmpdir):
    dataset_fio = tmpdir.join('dataset.txt')
    dataset_fio.write(DATASET_TINY_STR)
    return dataset_fio


def test_can_load_documents(tiny_dataset_fio):
    documents = load_documents(tiny_dataset_fio)
    reference_docs = {
        '123': 'some words A_word and nothing',
        '2': 'some word B_word in this dataset',
        '5': 'famous_phrases to be or not to be',
        '37': 'all words such A_word and B_word are here',
    }
    assert reference_docs == documents, (
        'load_documents incorrectly loaded dataset'
    )


@pytest.mark.parametrize(
    'query, reference_answer',
    [
        pytest.param(['A_word'], ['123', '37'], id='A_word'),
        pytest.param(['B_word'], ['2', '37'], id='B_word'),
        pytest.param(['A_word', 'B_word'], ['37'], id='both words'),
        pytest.param(['word_does_not_exist'], [], id='word does not exist'),
    ]
)
def test_query_inverted_index_interest_results(tiny_dataset_fio, query, reference_answer):
    documents = load_documents(tiny_dataset_fio)
    tiny_inverted_index = build_inverted_index(documents)
    answer = tiny_inverted_index.query(query)
    assert sorted(answer) == sorted(reference_answer), (
        f'Expected answer id {reference_answer}, got {answer}'
    )


@pytest.fixture()
def wikipedia_documents():
    documents = load_documents(DATASET_BIG_FILE_PATH)
    return documents


def test_can_load_wikipedia_sample(wikipedia_documents):
    doc = wikipedia_documents
    assert len(doc) == 4100, (
        'you incorrectly loaded Wikipedia sample'
    )


def test_can_dump_and_load_inverted_index(tmpdir, wikipedia_documents):
    index_fio = tmpdir.join('index.dump')
    inverted_index = build_inverted_index(wikipedia_documents)
    inverted_index.dump(index_fio)
    loaded_inverted_index = InvertedIndex.load(index_fio)
    assert inverted_index == loaded_inverted_index, (
        'load should return same inverted index'
    )


def test_can_built_and_query_inverted_index(wikipedia_documents):
    inverted_index = build_inverted_index(wikipedia_documents)
    doc_ids = inverted_index.query(['wikipedia'])
    assert isinstance(doc_ids, list), 'inverted index should be list'







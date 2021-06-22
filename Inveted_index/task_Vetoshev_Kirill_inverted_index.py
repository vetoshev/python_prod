"""Build, dump, load inverted index from documents"""
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import struct
import sys
from io import TextIOWrapper

DATASET_DEFAULT = "./wikipedia_sample.txt"
INDEX_DEFAULT = "./inverted.index"


class InvertedIndex:
    """Class for operations with index"""
    def __init__(self, data=None):
        self.index = data

    def __eq__(self, other):
        """equations of index"""
        return other.index == self.index

    def query(self, words, code='utf-8') -> list:
        """List of answer index"""
        answer = []
        if code == 'CP-1251':
            for i in range(len(words)):
                words[i] = words[i].decode('CP-1251').encode('UTF-8')
        for word in words:
            if not self.index.get(word):
                return []
            elif not answer:
                answer = list(self.index[word])
            else:
                prev = answer
                answer = []
                for i in self.index[word]:
                    if prev.count(i) != 0:
                        answer.append(i)
        return answer

    def dump(self, filepath: str, code='utf-8'):
        """Dump index"""
        with open(filepath, 'wb') as file:
            file.write(struct.pack('>i', len(self.index)))
            for word in self.index:
                key = word.encode(code)
                length = len(key)
                file.write(struct.pack('>B', length))
                file.write(struct.pack('>' + str(length) + 's', key))
                file.write(struct.pack('>H', len(self.index[word])))
                for i in self.index[word]:
                    file.write(struct.pack('>H', int(i)))

    @classmethod
    def load(cls, filepath: str, code='utf-8'):
        """Load index"""
        with open(filepath, 'rb') as file:
            index = dict()
            for _ in range(struct.unpack('>i', file.read(4))[0]):
                length = struct.unpack('>B', file.read(1))[0]
                word = (struct.unpack('>' + str(length) + 's', file.read(length))[0]).decode(code)
                number = struct.unpack('>H', file.read(2))[0]
                index[word] = set()
                for _ in range(number):
                    index[word].add(str(struct.unpack('>H', file.read(2))[0]))
        return cls(index)


def load_documents(filepath: str):
    """Load document for building index"""
    with open(filepath, 'r', encoding='utf-8') as file:
        out = {}
        file = file.read().split('\n')
        for i in file[:len(file) - 1]:
            part = i.split(maxsplit=1)
            out[part[0]] = part[1]
        return out


def build_inverted_index(documents):
    """Build inverted index"""
    reader = {}
    for file in documents:
        words = documents[file].split()
        for word in words:
            if word not in reader.keys():
                reader[word] = set()
            reader[word].add(file)
    return InvertedIndex(reader)


def call_build(res):
    """Make parser build"""
    documents = load_documents(res.data)
    inverted_index = build_inverted_index(documents)
    inverted_index.dump(res.out)


def call_query(res):
    """Make parser query"""
    inverted_index = InvertedIndex(res.inverted_index_filepath)
    question = []
    if res.query_file_utf8:
        if res.query_file_cp1251:
            return
        else:
            code = "utf-8"
    else:
        code = "cp1251"
    with open(res.q_file, encoding=code) as file:
        for line in file:
            line.strip()
            question.append(line)
    for quest in question:
        answer = inverted_index.query(quest, code)
        sys.stdout.write(",".join(answer))


def setup_parser(parser):
    """Build parser"""
    subparsers = parser.add_subparsers(
        help='choose command'
    )
    build = subparsers.add_parser(
        'build', help='build and store',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    query = subparsers.add_parser(
        'query', help='query',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    build.set_defaults(callback=call_build)
    query.set_defaults(callback=call_query)

    build.add_argument(
        '--dataset',
        dest='data',
        default=DATASET_DEFAULT,
        help='path to dataset',
    )
    build.add_argument(
        '--output',
        dest='out',
        default=INDEX_DEFAULT,
        help='path to dump inverted index',
    )
    query.add_argument(
        '--index',
        dest='index',
        default=INDEX_DEFAULT,
        help='path to load inverted index',
    )
    code = query.add_mutually_exclusive_group(required=True)
    code.add_argument(
        '--query-file-utf8',
        help='data with encode type',
        dest='q_file',
        default=TextIOWrapper(sys.stdin.buffer, encoding="utf-8"),
    )
    code.add_argument(
        '--query-file-cp1251',
        help='data with encode type',
        dest='q_file',
        default=TextIOWrapper(sys.stdin.buffer, encoding="cp1251")
    )
    query.add_argument(
        '--query',
        nargs='+',
        help='query for inverted index'
    )


def main():
    """Main function"""
    parser = ArgumentParser(
        prog='invert-index',
        description='tool to build, dump, load and query inverted index',
    )
    setup_parser(parser)
    res = parser.parse_args()
    res.callback(res)


if __name__ == "__main__":
    main()

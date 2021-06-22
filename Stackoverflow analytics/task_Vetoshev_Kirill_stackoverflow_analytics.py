#!/usr/bin/env python3
"""App for analyze StackOverflow posts popularity"""

import sys
import re
import csv
import json
import logging
import logging.config
from argparse import ArgumentParser
import yaml
from lxml import etree

LOG = "./stackoverflow_analytics.log"
WARNING_LOG = "./stackoverflow_analytics.warn"
DEFAULT_DATASET = "./stackoverflow_posts_sample.xml"
DEFAULT_STOPWORDS_DATASET = "./stop_words_en.txt"
TEST_CSV_FILE = "./test_queries.csv"
DEFAULT_LOGGING_CONF = "./logging_conf.yml"

logger = logging.getLogger('task_Vetoshev_Kirill_stackoverflow_analytics')


class StackOverflow:
    """class for store rating"""
    def __init__(self, data):
        self.data = data

    def filter_data_by_date(self, start, end):
        """filter data by year"""
        start = int(start)
        end = int(end)
        data = {}
        for key in self.data.keys():
            if start <= self.data[key][0] <= end:
                data[key] = self.data[key]
        return data


def top(data, top_n=None):
    """Return top N words from rating in list format"""
    rat = dict()
    for key in data.keys():
        for word in data[key][2]:
            if word in rat.keys():
                rat[word] += data[key][1]
            else:
                rat[word] = data[key][1]
    rat = sorted(rat.items(), key=lambda item: (-item[1], item[0]))[:top_n]
    return rat


def load_file(filepath):
    """load xml file"""
    document = {}
    post_id = 0
    with open(filepath, encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            root = etree.fromstring(line)
            post_type_id = root.get("PostTypeId")
            if post_type_id == '1':
                creation_date = int(root.get("CreationDate")[:4])
                post_id += 1
                score = int(root.get("Score"))
                title = list(set(re.findall(r"\w+", root.get("Title").lower())))
                document[post_id] = [creation_date, score, title]
    return document


def load_stopwords_file(filepath):
    """load file with stopwords in given encoding"""
    with open(filepath, encoding="koi8-r") as file:
        content = file.read()
        stop = content.split('\n')[:-1]
    return stop


def remove_stopwords(document, stopwords):
    """removing stopwords from titles"""
    for id_docs in document.keys():
        title = document[id_docs][2]
        document[id_docs][2] = [word for word in title if word not in stopwords]


def load_csv_file(filepath):
    """load csv file with queries"""
    queries = []
    with open(filepath, 'r', newline='') as file:
        file_read = csv.reader(file)
        for line in file_read:
            queries.append(line)
    return queries


def callback_query(arguments):
    """callback for argument parser"""
    document = load_file(arguments.questions)
    stopwords_list = load_stopwords_file(arguments.stop_words)
    remove_stopwords(document, stopwords_list)
    so_document = StackOverflow(document)
    logger.info("process XML dataset, ready to serve queries")
    queries = load_csv_file(arguments.queries)
    for query in queries:
        query = list(map(int, query))
        logger.debug('got query "%i,%i,%i"', query[0], query[1], query[2])
        filtered_so_document = so_document.filter_data_by_date(query[0], query[1])
        answer = dict()
        answer["start"] = query[0]
        answer["end"] = query[1]
        answer["top"] = top(filtered_so_document, query[2])
        top_k = len(answer["top"])
        if top_k < query[2]:
            logger.warning(
                'not enough data to answer, found %i words out of %i for period "%s,%s"',
                top_k, query[2], query[0], query[1])
        json.dump(answer, sys.stdout)
        sys.stdout.write("\n")


def setup_logger():
    """function to setup logger"""
    with open(DEFAULT_LOGGING_CONF) as file:
        logging.config.dictConfig(yaml.safe_load(file))


def setup_parser(parser):
    """function to setup parser"""
    parser.set_defaults(callback=callback_query)
    parser.add_argument(
        "--questions",
        default=DEFAULT_DATASET,
        help="path to xml posts"
    )
    parser.add_argument(
        "--stop-words",
        default=DEFAULT_STOPWORDS_DATASET,
        help="path to stopwords"
    )
    parser.add_argument(
        "--queries",
        default=TEST_CSV_FILE,
        help="path to csv queries"
    )


def main():
    """main function"""
    parser = ArgumentParser(
        prog="stackoverflow-analytics",
    )
    setup_parser(parser)
    setup_logger()
    arguments = parser.parse_args()
    arguments.callback(arguments)
    logger.info("finish processing queries")


if __name__ == "__main__":
    main()

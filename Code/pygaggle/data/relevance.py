from dataclasses import dataclass
from functools import lru_cache
import logging
from pygaggle.rerank.bm25 import Bm25Reranker
from typing import List, Optional
import json
import re

from pyserini.search import SimpleSearcher

from pygaggle.rerank.base import Query, Text

__all__ = ['RelevanceExample', 'Cord19DocumentLoader', 'Cord19AbstractLoader']


@dataclass
class RelevanceExample:
    query: Query
    documents: List[Text]
    labels: List[bool]


@dataclass
class Cord19Document:
    body_text: str
    ref_entries: str
    abstract: Optional[str] = ''

    @property
    def all_text(self):
        return '\n'.join((self.abstract, self.body_text, self.ref_entries))


@dataclass
class Cord19Abstract:
    title: str
    abstract: str

    def all_text(self):
        return '\n'.join((self.title, self.abstract))


@dataclass
class MsMarcoPassage:
    para_text: str

    @property
    def all_text(self):
        return self.para_text


class Cord19DocumentLoader:
    double_space_pattern = re.compile(r'\s\s+')

    def __init__(self, index_path: str):
        self.searcher = SimpleSearcher(index_path)

    @lru_cache(maxsize=1024)
    def load_document(self, id: str) -> Cord19Document:
        def unfold(entries):
            return '\n'.join(x['text'] for x in entries)
        try:
            article = json.loads(
                self.searcher.doc(id).lucene_document().get('raw'))
        except json.decoder.JSONDecodeError:
            raise ValueError('article not found')
        except AttributeError:
            raise ValueError('document unretrievable')
        ref_entries = article['ref_entries'].values()
        return Cord19Document(unfold(article['body_text']),
                              unfold(ref_entries),
                              abstract=unfold(article['abstract']) if 'abstract' in article else '')


class Cord19AbstractLoader:
    double_space_pattern = re.compile(r'\s\s+')

    def __init__(self, index_path: str):
        self.searcher = SimpleSearcher(index_path)

    @lru_cache(maxsize=1024)
    def load_document(self, id: str) -> Cord19Document:
        try:
            article = json.loads(
                self.searcher.doc(id).lucene_document().get('raw'))
        except json.decoder.JSONDecodeError:
            raise ValueError('article not found')
        except AttributeError as e:
            logging.error(e)
            raise ValueError('document unretrievable')
        return Cord19Abstract(article['csv_metadata']['title'],
                              abstract=article['csv_metadata']['abstract'] if 'abstract' in article else '')


class MsMarcoPassageLoader:
    def __init__(self, index_path: str):
        self.searcher = SimpleSearcher(index_path)

    def get_most_relevant_paragraph(self, query, passage):
        bm25_reranker = Bm25Reranker()
        passages = passage.split('**PARAGRAPH**')
        passages = passages[1:]
        passages_textobj = [Text(passage) for passage in passages]
        query_queryobj = Query(query)
        texts_with_scores = bm25_reranker.rerank(query_queryobj, passages_textobj)
        most_relevant_paragraph = max(texts_with_scores, key=lambda text: text.score)
        return most_relevant_paragraph.text

    def load_passage(self, id: str, query: str) -> MsMarcoPassage:
        try:
            passage = self.searcher.doc(id).lucene_document().get('raw')
            most_relevant_paragraph = self.get_most_relevant_paragraph(query, passage)
        except AttributeError as e:
            try:
                passage = self.searcher.doc(id).raw()
                most_relevant_paragraph = self.get_most_relevant_paragraph(query, passage)
            except AttributeError as e:
                most_relevant_paragraph = ""
                #raise ValueError(f'skipping {id} passage unretrievable because {e}')
        return MsMarcoPassage(most_relevant_paragraph)

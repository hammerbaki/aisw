# -*- coding: utf-8 -*-
"""검색기 고정 테스트. 고치지 않는다(TDD에서 동결한 테스트와 같은 역할).

embed_search.py의 cosine_similarity와 search를 확인한다.
임베딩 서버와 API 없이 돈다. search 테스트는 embed를 정해 둔 벡터로 바꿔 끼운다.
"""
import pytest

import embed_search


def test_같은_방향이면_유사도는_1이다():
    assert embed_search.cosine_similarity([1.0, 2.0], [2.0, 4.0]) == pytest.approx(1.0)


def test_직각이면_유사도는_0이다():
    assert embed_search.cosine_similarity([1.0, 0.0], [0.0, 3.0]) == pytest.approx(0.0)


def test_search는_가까운_순으로_TOP_K개를_돌려준다(monkeypatch):
    monkeypatch.setattr(embed_search, "embed", lambda text: [1.0, 0.0])
    index = [
        {"text": "직각", "vector": [0.0, 1.0]},
        {"text": "거의 같은 방향", "vector": [1.0, 0.1]},
        {"text": "45도", "vector": [1.0, 1.0]},
        {"text": "반대 방향", "vector": [-1.0, 0.0]},
    ]
    result = embed_search.search("아무 질문", index)
    assert len(result) == embed_search.TOP_K
    assert [text for _, text in result] == ["거의 같은 방향", "45도", "직각"]
    assert result[0][0] >= result[1][0] >= result[2][0]

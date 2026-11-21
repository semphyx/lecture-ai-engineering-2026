"""宿題（実装）: 前後ページを付ける処理のテスト（APIを呼ばない）。"""

from app.retrieval import add_neighbors, load_pages


def _hit(page_id):
    page = next(p for p in load_pages() if p["page_id"] == page_id)
    return {**page, "distance": 0.1}


def _ids(results):
    return [r["page_id"] for r in results]


def test_window_zero_returns_hits_unchanged():
    hits = [_hit("lec02-main-p010")]
    assert add_neighbors(hits, window=0) == hits


def test_adds_previous_and_next_page():
    results = add_neighbors([_hit("lec02-main-p010")], window=1)
    assert _ids(results) == ["lec02-main-p009", "lec02-main-p010", "lec02-main-p011"]
    assert [r["role"] for r in results] == ["neighbor", "hit", "neighbor"]


def test_does_not_cross_documents():
    last = max((p for p in load_pages() if p["document_id"] == "lec01-main"), key=lambda p: p["page"])
    results = add_neighbors([_hit(last["page_id"])], window=1)
    assert all(r["document_id"] == "lec01-main" for r in results)
    assert len(results) == 2  # 前のページと自分だけ。次の資料の1ページ目は付けない


def test_no_duplicates_when_hits_are_adjacent():
    results = add_neighbors([_hit("lec02-main-p010"), _hit("lec02-main-p011")], window=1)
    ids = _ids(results)
    assert len(ids) == len(set(ids))
    assert ids == ["lec02-main-p009", "lec02-main-p010", "lec02-main-p011", "lec02-main-p012"]
    assert {r["page_id"]: r["role"] for r in results}["lec02-main-p011"] == "hit"

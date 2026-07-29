from outline_sage_api.fusion import reciprocal_rank_fusion


def test_document_in_both_lists_ranks_higher_than_single_list():
    dense = ["a", "b", "c"]
    sparse = ["b", "a", "d"]

    result = reciprocal_rank_fusion([dense, sparse])
    ranked_ids = [doc_id for doc_id, _ in result]

    # "a" dan "b" muncul di kedua list, harus di atas "c" dan "d" yang cuma muncul sekali
    assert ranked_ids.index("a") < ranked_ids.index("c")
    assert ranked_ids.index("b") < ranked_ids.index("d")


def test_document_only_in_one_list_still_included():
    dense = ["a"]
    sparse = ["z"]

    result = reciprocal_rank_fusion([dense, sparse])
    ranked_ids = {doc_id for doc_id, _ in result}

    assert ranked_ids == {"a", "z"}


def test_higher_rank_in_single_list_scores_higher():
    dense = ["a", "b", "c"]

    result = reciprocal_rank_fusion([dense])
    ranked_ids = [doc_id for doc_id, _ in result]

    assert ranked_ids == ["a", "b", "c"]


def test_empty_lists_return_empty_result():
    assert reciprocal_rank_fusion([[], []]) == []

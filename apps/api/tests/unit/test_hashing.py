from outline_sage_api.hashing import content_hash, diff_chunks


def test_content_hash_is_deterministic_and_sensitive_to_change():
    h1 = content_hash("halo dunia")
    h2 = content_hash("halo dunia")
    h3 = content_hash("halo dunia!")

    assert h1 == h2
    assert h1 != h3


def test_diff_chunks_detects_new_chunk():
    old_hashes: dict[int, str] = {}
    new_chunks = {0: "isi baru"}

    to_embed, to_delete = diff_chunks(old_hashes, new_chunks)

    assert 0 in to_embed
    assert to_delete == []


def test_diff_chunks_skips_unchanged_chunk():
    old_hashes = {0: content_hash("isi sama")}
    new_chunks = {0: "isi sama"}

    to_embed, to_delete = diff_chunks(old_hashes, new_chunks)

    assert to_embed == {}
    assert to_delete == []


def test_diff_chunks_detects_changed_chunk():
    old_hashes = {0: content_hash("isi lama")}
    new_chunks = {0: "isi baru"}

    to_embed, to_delete = diff_chunks(old_hashes, new_chunks)

    assert 0 in to_embed
    assert to_delete == []


def test_diff_chunks_detects_removed_chunk():
    old_hashes = {0: content_hash("isi a"), 1: content_hash("isi b")}
    new_chunks = {0: "isi a"}

    to_embed, to_delete = diff_chunks(old_hashes, new_chunks)

    assert to_embed == {}
    assert to_delete == [1]


def test_diff_chunks_mixed_scenario():
    old_hashes = {
        0: content_hash("tetap sama"),
        1: content_hash("akan berubah"),
        2: content_hash("akan dihapus"),
    }
    new_chunks = {
        0: "tetap sama",
        1: "sudah berubah",
        3: "chunk baru",
    }

    to_embed, to_delete = diff_chunks(old_hashes, new_chunks)

    assert set(to_embed.keys()) == {1, 3}
    assert to_delete == [2]

"""Storage adapters and signed download links."""

import io

import pytest

from adapters.storage import LocalStorage, S3Storage, make_storage
from app import links

SECRET = "s" * 40


def test_local_storage_roundtrip(tmp_path):
    st = LocalStorage(tmp_path)
    st.put("orders/a/1/model.xlsx", b"data", "x")
    assert st.exists("orders/a/1/model.xlsx") and st.get("orders/a/1/model.xlsx") == b"data"
    st.delete("orders/a/1/model.xlsx")
    assert not st.exists("orders/a/1/model.xlsx")
    assert not list(tmp_path.rglob("*.part"))


@pytest.mark.parametrize("key", ["../etc/passwd", "orders/../../x", "/abs", "", "a\\b"])
def test_local_storage_rejects_bad_keys(tmp_path, key):
    with pytest.raises(ValueError):
        LocalStorage(tmp_path).put(key, b"x", "x")


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.objects[(Bucket, Key)] = Body

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.objects[(Bucket, Key)])}

    def head_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            err = Exception("404")
            err.response = {"Error": {"Code": "404"}}
            raise err

    def delete_object(self, Bucket, Key):
        self.objects.pop((Bucket, Key), None)


def test_s3_storage_with_fake_client():
    st = S3Storage("bucket", FakeS3())
    assert not st.exists("k/model.xlsx")
    st.put("k/model.xlsx", b"abc", "x")
    assert st.exists("k/model.xlsx") and st.get("k/model.xlsx") == b"abc"
    st.delete("k/model.xlsx")
    assert not st.exists("k/model.xlsx")


def test_make_storage(tmp_path):
    assert isinstance(make_storage("local", str(tmp_path)), LocalStorage)
    with pytest.raises(RuntimeError):
        make_storage("s3", str(tmp_path))
    with pytest.raises(RuntimeError):
        make_storage("ftp", str(tmp_path))


def test_signed_link_roundtrip_and_expiry():
    tok = links.sign(SECRET, "abc123", 60, now=1000)
    assert links.verify(SECRET, tok, now=1059) == "abc123"
    with pytest.raises(links.LinkError, match="expired"):
        links.verify(SECRET, tok, now=1061)


@pytest.mark.parametrize("mutate", [lambda t: t[:-2] + "xx", lambda t: "zzz" + t[3:], lambda t: t.replace(".", "", 1)])
def test_tampered_links_are_rejected(mutate):
    tok = links.sign(SECRET, "abc123", 60, now=1000)
    with pytest.raises(links.LinkError):
        links.verify(SECRET, mutate(tok), now=1001)


def test_other_secret_or_longer_expiry_rejected():
    tok = links.sign(SECRET, "abc123", 60, now=1000)
    with pytest.raises(links.LinkError):
        links.verify("t" * 40, tok, now=1001)
    aid, exp, sig = tok.split(".")
    with pytest.raises(links.LinkError):
        links.verify(SECRET, f"{aid}.{int(exp) + 10**6}.{sig}", now=1001)

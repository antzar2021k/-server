import hashlib
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.x509.oid import NameOID

V2_ID = 0x7109871A
SIG_ALG_RSA_PKCS1_SHA256 = 0x0103
CHUNK_SIZE = 1024 * 1024
EOCD_SIG = b"\x50\x4b\x05\x06"
MAGIC = b"APK Sig Block 42"


def le32(value):
    return struct.pack("<I", value)


def le64(value):
    return struct.pack("<Q", value)


def lp(data):
    return le32(len(data)) + data


def find_eocd(data):
    start = max(0, len(data) - (22 + 0xFFFF))
    offset = data.rfind(EOCD_SIG, start)
    if offset < 0:
        raise ValueError("EOCD not found")
    comment_len = struct.unpack_from("<H", data, offset + 20)[0]
    if offset + 22 + comment_len != len(data):
        raise ValueError("EOCD comment length mismatch")
    return offset


def set_cd_offset(eocd, offset):
    out = bytearray(eocd)
    struct.pack_into("<I", out, 16, offset)
    return bytes(out)


def content_digest(sections):
    chunk_digests = []
    for section in sections:
        for pos in range(0, len(section), CHUNK_SIZE):
            chunk = section[pos : pos + CHUNK_SIZE]
            h = hashlib.sha256()
            h.update(b"\xa5")
            h.update(le32(len(chunk)))
            h.update(chunk)
            chunk_digests.append(h.digest())

    h = hashlib.sha256()
    h.update(b"\x5a")
    h.update(le32(len(chunk_digests)))
    for digest in chunk_digests:
        h.update(digest)
    return h.digest()


def make_cert_and_key():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, "android@android.com"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Android"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Android"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Android"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mountain View"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime(2020, 1, 1, tzinfo=timezone.utc))
        .not_valid_after(datetime(2074, 10, 4, tzinfo=timezone.utc))
        .sign(key, hashes.SHA256())
    )
    return key, cert.public_bytes(Encoding.DER)


def make_v2_block(digest, key, cert_der):
    public_key_der = key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

    digest_record = lp(le32(SIG_ALG_RSA_PKCS1_SHA256) + lp(digest))
    digests = lp(digest_record)
    certificates = lp(lp(cert_der))
    additional_attrs = lp(b"")
    signed_data = digests + certificates + additional_attrs

    signature = key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    sig_record = lp(le32(SIG_ALG_RSA_PKCS1_SHA256) + lp(signature))
    signatures = lp(sig_record)

    signer = lp(signed_data) + signatures + lp(public_key_der)

    # APK Signature Scheme v2 pair value is a length-prefixed sequence of
    # length-prefixed signer blocks. The previous implementation missed the
    # outer sequence length, which made Android report the APK as damaged.
    signers_sequence = lp(signer)
    v2_value = lp(signers_sequence)

    pair = le64(4 + len(v2_value)) + le32(V2_ID) + v2_value
    size = len(pair) + 24
    return le64(size) + pair + le64(size) + MAGIC


def sign_apk(input_path, output_path):
    data = Path(input_path).read_bytes()
    eocd_offset = find_eocd(data)
    cd_size = struct.unpack_from("<I", data, eocd_offset + 12)[0]
    cd_offset = struct.unpack_from("<I", data, eocd_offset + 16)[0]
    if cd_offset + cd_size != eocd_offset:
        raise ValueError(
            f"Unexpected ZIP layout: cd_offset={cd_offset}, cd_size={cd_size}, eocd={eocd_offset}"
        )

    before_cd = data[:cd_offset]
    central_directory = data[cd_offset:eocd_offset]
    eocd = data[eocd_offset:]

    digest = content_digest([before_cd, central_directory, set_cd_offset(eocd, cd_offset)])
    key, cert_der = make_cert_and_key()
    signing_block = make_v2_block(digest, key, cert_der)
    final_eocd = set_cd_offset(eocd, cd_offset + len(signing_block))

    out = before_cd + signing_block + central_directory + final_eocd
    Path(output_path).write_bytes(out)
    print(f"Wrote {output_path}")
    print(f"SHA-256: {hashlib.sha256(out).hexdigest()}")


if __name__ == "__main__":
    sign_apk(sys.argv[1], sys.argv[2])

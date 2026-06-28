import json
import hashlib
import struct
import time
import zipfile
from pathlib import Path

SRC = Path('KABAN RUSSIA (1).apk')
OUT_UNSIGNED = Path('KABAN_RUSSIA_16.26.7.1_patched_unsigned.apk')

RES_STRING_POOL_TYPE = 0x0001
RES_XML_START_ELEMENT_TYPE = 0x0102
TYPE_INT_DEC = 0x10


def u16(b, o):
    return struct.unpack_from('<H', b, o)[0]


def u32(b, o):
    return struct.unpack_from('<I', b, o)[0]


def w32(b, o, v):
    struct.pack_into('<I', b, o, v & 0xFFFFFFFF)


def read_utf8_len(b, o):
    x = b[o]
    o += 1
    if x & 0x80:
        x = ((x & 0x7F) << 8) | b[o]
        o += 1
    return x, o


def read_utf16_len(b, o):
    x = u16(b, o)
    o += 2
    if x & 0x8000:
        x = ((x & 0x7FFF) << 16) | u16(b, o)
        o += 2
    return x, o


def parse_string_pool_values(data, off):
    string_count = u32(data, off + 8)
    flags = u32(data, off + 16)
    strings_start = u32(data, off + 20)
    header = u16(data, off + 2)
    is_utf8 = bool(flags & 0x100)
    base = off + strings_start
    out = []
    for i in range(string_count):
        so = u32(data, off + header + i * 4)
        p = base + so
        if is_utf8:
            _, p = read_utf8_len(data, p)
            byte_len, p = read_utf8_len(data, p)
            out.append(bytes(data[p:p + byte_len]).decode('utf-8', 'replace'))
        else:
            chars, p = read_utf16_len(data, p)
            out.append(bytes(data[p:p + chars * 2]).decode('utf-16le', 'replace'))
    return out


def patch_string_pool(data, off, replacements):
    header = u16(data, off + 2)
    string_count = u32(data, off + 8)
    flags = u32(data, off + 16)
    strings_start = u32(data, off + 20)
    is_utf8 = bool(flags & 0x100)
    base = off + strings_start
    changed = []
    for i in range(string_count):
        so = u32(data, off + header + i * 4)
        p = base + so
        if is_utf8:
            chars, p1 = read_utf8_len(data, p)
            byte_len, p2 = read_utf8_len(data, p1)
            old = bytes(data[p2:p2 + byte_len]).decode('utf-8', 'replace')
            if old in replacements:
                new = replacements[old]
                nb = new.encode('utf-8')
                if len(new) != chars or len(nb) != byte_len:
                    raise ValueError(f'Length mismatch: {old!r} -> {new!r}')
                data[p2:p2 + byte_len] = nb
                changed.append((i, old, new))
        else:
            chars, p1 = read_utf16_len(data, p)
            old = bytes(data[p1:p1 + chars * 2]).decode('utf-16le', 'replace')
            if old in replacements:
                new = replacements[old]
                nb = new.encode('utf-16le')
                if len(new) != chars or len(nb) != chars * 2:
                    raise ValueError(f'Length mismatch: {old!r} -> {new!r}')
                data[p1:p1 + chars * 2] = nb
                changed.append((i, old, new))
    return changed


def walk_and_patch_string_pools(blob, replacements):
    data = bytearray(blob)
    changes = []

    def walk(start, end):
        off = start
        while off + 8 <= end:
            typ = u16(data, off)
            header = u16(data, off + 2)
            size = u32(data, off + 4)
            if size <= 0 or off + size > len(data):
                break
            if typ == RES_STRING_POOL_TYPE:
                changes.extend(patch_string_pool(data, off, replacements))
            if typ in (0x0002, 0x0200):
                walk(off + header, off + size)
            off += size

    walk(0, len(data))
    return bytes(data), changes


def patch_manifest(blob):
    data = bytearray(blob)
    off = u16(data, 2)
    strings = []
    string_changes = []
    while off + 8 <= len(data):
        typ, size = u16(data, off), u32(data, off + 4)
        if typ == RES_STRING_POOL_TYPE:
            string_changes = patch_string_pool(data, off, {'16.26.7.0': '16.26.7.1'})
            strings = parse_string_pool_values(data, off)
            break
        off += size

    attr_changes = []
    off = u16(data, 2)
    while off + 8 <= len(data):
        typ, size = u16(data, off), u32(data, off + 4)
        if size <= 0:
            break
        if typ == RES_XML_START_ELEMENT_TYPE:
            elem_name_index = u32(data, off + 20)
            elem = strings[elem_name_index] if elem_name_index < len(strings) else ''
            attr_start = u16(data, off + 24)
            attr_size = u16(data, off + 26)
            attr_count = u16(data, off + 28)
            aoff = off + 16 + attr_start
            for _ in range(attr_count):
                name_index = u32(data, aoff + 4)
                name = strings[name_index] if name_index < len(strings) else ''
                dtype = data[aoff + 15]
                value = u32(data, aoff + 16)
                if elem == 'manifest' and name == 'versionCode' and dtype == TYPE_INT_DEC:
                    w32(data, aoff + 16, 1184)
                    attr_changes.append(('versionCode', value, 1184))
                aoff += attr_size
        off += size
    return bytes(data), string_changes, attr_changes


def main():
    resource_replacements = {
        'Играть': 'ЗАПУСК',
        'Настройки': 'ПАРАМЕТРЫ',
        'Сервер': 'ОНЛАЙН',
    }
    report = {}
    with zipfile.ZipFile(SRC, 'r') as zin, zipfile.ZipFile(OUT_UNSIGNED, 'w') as zout:
        for info in zin.infolist():
            if info.filename.startswith('META-INF/'):
                continue
            data = zin.read(info.filename)
            if info.filename == 'AndroidManifest.xml':
                data, string_changes, attr_changes = patch_manifest(data)
                report['manifest'] = {'string_changes': string_changes, 'attr_changes': attr_changes}
            elif info.filename == 'resources.arsc':
                data, string_changes = walk_and_patch_string_pools(data, resource_replacements)
                report['resources'] = {'string_changes': string_changes}
            zi = zipfile.ZipInfo(info.filename, info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zout.writestr(zi, data)

        patch_manifest_data = {
            'base_apk_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
            'patched_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'versionName': '16.26.7.1',
            'versionCode': 1184,
            'package': 'com.break.russia',
            'changes': [
                'Version bumped to 16.26.7.1 / 1184.',
                'UI strings polished: Играть -> ЗАПУСК, Настройки -> ПАРАМЕТРЫ, Сервер -> ОНЛАЙН.',
                'Original signature removed before re-signing.',
            ],
            'patch_report': report,
        }
        zi = zipfile.ZipInfo('assets/launcher_patch/patch_manifest.json')
        zi.compress_type = zipfile.ZIP_DEFLATED
        zout.writestr(zi, json.dumps(patch_manifest_data, ensure_ascii=False, indent=2).encode('utf-8'))

    print(json.dumps({
        'unsigned_apk': str(OUT_UNSIGNED),
        'sha256': hashlib.sha256(OUT_UNSIGNED.read_bytes()).hexdigest(),
        'report': report,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

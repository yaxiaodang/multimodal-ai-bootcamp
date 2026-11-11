"""Read-only W&B v0 log framing; protobuf decoding uses the installed SDK.

Format reference: wandb/wandb v0.24.0 wandb/sdk/internal/datastore.py.
SDK 0.31.0 no longer ships that Python reader. This helper never edits a spool.
"""
import struct
import zlib


def records(path):
    with path.open('rb') as stream:
        assert stream.read(7) == struct.pack('<4sHB', b':W&B', 0xBEE1, 0), 'Unknown W&B log format'
        fragments = []
        while True:
            remaining = 32768 - stream.tell() % 32768
            if remaining < 7:
                assert stream.read(remaining) == b'\0' * remaining, 'Invalid block trailer'
            header = stream.read(7)
            if not header:
                assert not fragments, 'Incomplete fragmented record'
                return
            assert len(header) == 7, 'Incomplete record header'
            checksum, length, kind = struct.unpack('<IHB', header)
            assert kind in {1, 2, 3, 4}, 'Unsupported fragment type'
            data = stream.read(length)
            assert len(data) == length, 'Truncated record'
            assert zlib.crc32(data, zlib.crc32(bytes([kind]))) & 0xffffffff == checksum, 'CRC mismatch'
            if kind == 1:
                assert not fragments
                yield data
            elif kind == 2:
                assert not fragments
                fragments = [data]
            elif kind == 3:
                assert fragments
                fragments.append(data)
            else:
                assert fragments
                yield b''.join(fragments + [data])
                fragments = []

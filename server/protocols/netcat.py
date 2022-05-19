import socket

from server import app
from server.models import FlagStatus, SubmitResult

RESPONSES = {
    FlagStatus.ACCEPTED: ['[OK]'],
    FlagStatus.REJECTED: [
        '[ERR] Invalid format',
        '[ERR] Invalid flag',
        '[ERR] Expired',
        "[ERR] Can't submit flag from NOP team",
        '[OFFLINE] CTF not running'
    ],
    FlagStatus.SKIPPED: [
        '[ERR] Already submitted',
        '[ERR] This is your own flag'
    ]
}


def submit_flags(flags, config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((config['SYSTEM_HOST'], config['SYSTEM_PORT']))
        for item in flags:
            sock.send(item.flag.encode())
            response = sock.recv(4096).decode(errors="ignore").lower()

            for status, substrings in RESPONSES.items():
                if any(s in response for s in substrings):
                    found_status = status
                    break
            else:
                found_status = FlagStatus.QUEUED
                app.logger.warning(
                    'Unknown checksystem response (flag will be resent): %s',
                    response)

            yield SubmitResult(item.flag, found_status, response)

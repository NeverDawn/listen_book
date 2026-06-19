import sys
import urllib.request
import uuid
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: upload_sample.py <path>")

    path = Path(sys.argv[1])
    boundary = f"----listenbook{uuid.uuid4().hex}"
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        "Content-Type: text/plain\r\n"
        "\r\n"
    ).encode("utf-8")
    footer = f"\r\n--{boundary}--\r\n".encode("utf-8")
    body = header + path.read_bytes() + footer

    request = urllib.request.Request(
        "http://127.0.0.1:8000/api/books",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(response.status)
        print(response.read().decode("utf-8"))


if __name__ == "__main__":
    main()

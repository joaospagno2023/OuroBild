from pathlib import Path
import re


AIP_PATH = Path(
    r"C:\DvpLocal\WorkSpaceTFS"
    r"\Transferencia de Arquivo"
    r"\TransferenciaDeArquivos"
    r"\Setups"
    r"\Installers"
    r"\Projects"
    r"\OuroNet.WinServiceLinkPagamento.aip"
)


content = AIP_PATH.read_text(
    encoding="utf-8",
)


print("=" * 80)
print("AIP")
print("=" * 80)
print(AIP_PATH)
print()


patterns = [
    r"<ROW\b.*?/>",
    r"<ROW\b.*?\>",
    r"SourcePath=",
    r"Component=",
    r"Destination=",
]


for pattern in patterns:

    matches = re.findall(
        pattern,
        content,
        re.IGNORECASE | re.DOTALL,
    )

    print(
        f"PATTERN: {pattern}"
    )

    print(
        f"TOTAL: {len(matches)}"
    )

    print()


print("=" * 80)
print("PRIMEIRAS OCORRÊNCIAS DE <ROW")
print("=" * 80)

matches = list(
    re.finditer(
        r"<ROW\b",
        content,
        re.IGNORECASE,
    )
)

print(
    f"TOTAL <ROW: {len(matches)}"
)

print()


for index, match in enumerate(
    matches[:10],
    start=1,
):

    start = match.start()

    end = content.find(
        "/>",
        start,
    )

    if end < 0:

        end = min(
            start + 3000,
            len(content),
        )

    else:

        end += 2

    print(
        f"--- ROW {index} ---"
    )

    print(
        content[start:end]
    )

    print()


print("=" * 80)
print("OCORRÊNCIAS DE SourcePath")
print("=" * 80)

source_matches = list(
    re.finditer(
        r"SourcePath=",
        content,
        re.IGNORECASE,
    )
)

print(
    f"TOTAL SourcePath: {len(source_matches)}"
)

print()

for index, match in enumerate(
    source_matches[:20],
    start=1,
):

    start = max(
        0,
        match.start() - 300,
    )

    end = min(
        len(content),
        match.start() + 700,
    )

    print(
        f"--- SourcePath {index} ---"
    )

    print(
        content[start:end]
    )

    print()
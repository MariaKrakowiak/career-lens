import io

from pypdf import PdfReader


def extract_pdf_text(
    uploaded_file,
) -> str:

    data = uploaded_file.getvalue()

    reader = PdfReader(
        io.BytesIO(data)
    )

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(
        pages
    ).strip()


def clean_text(
    text: str,
    max_chars: int = 50000,
) -> str:

    text = text.replace(
        "\x00",
        " ",
    )

    lines = []

    for line in text.splitlines():

        lines.append(
            line.rstrip()
        )

    text = "\n".join(
        lines
    )

    return text[
        :max_chars
    ].strip()
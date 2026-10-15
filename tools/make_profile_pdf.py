#!/usr/bin/env python3
"""Generate a placeholder corporate-profile.pdf for the UCCL website.

The produced file is a valid single-page PDF so the site's
"Download Corporate Profile" button works out of the box.
Replace it with the final designed PDF when available.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "corporate-profile.pdf"

NAVY = "0.039 0.106 0.180"
GOLD = "0.722 0.576 0.247"
INK = "0.137 0.165 0.192"
MUTED = "0.353 0.400 0.447"

PAGE_W, PAGE_H = 595.28, 841.89  # A4 in points


def esc(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build_content() -> str:
    ops: list[str] = []

    def text(x, y, size, font, color, string):
        ops.append(
            f"BT /{font} {size} Tf {color} rg 1 0 0 1 {x} {y} Tm ({esc(string)}) Tj ET"
        )

    def rect(x, y, w, h, color):
        ops.append(f"{color} rg {x} {y} {w} {h} re f")

    # --- Header band ---
    rect(0, PAGE_H - 120, PAGE_W, 120, NAVY)
    rect(56, PAGE_H - 132, 120, 4, GOLD)
    text(56, PAGE_H - 78, 26, "F2", "1 1 1", "UCCL")
    text(56, PAGE_H - 100, 10, "F1", "0.847 0.737 0.478",
         "UNIQUE CONSULTANCY & COLLECTION LTD.")
    text(330, PAGE_H - 78, 10, "F1", "1 1 1",
         "Recovery | Collection | Consultancy | CPV")
    text(330, PAGE_H - 96, 9, "F1", "0.847 0.737 0.478", "Dhaka, Bangladesh")

    y = PAGE_H - 180
    text(56, y, 15, "F2", NAVY, "Corporate Profile 2026")
    text(56, y - 18, 9, "F1", GOLD, "PLACEHOLDER DOCUMENT - TO BE REPLACED WITH FINAL PDF")

    # --- About ---
    y -= 56
    text(56, y, 12, "F2", NAVY, "About UCCL")
    y -= 8
    for line in [
        "UCCL is a Bangladesh-based specialist provider of recovery, collection, consultancy",
        "and outsourced field-support services for banks, NBFIs, telecom companies and",
        "multinational corporates. Founded by three partners with direct hands-on experience",
        "inside leading commercial banks.",
    ]:
        y -= 15
        text(56, y, 10, "F1", INK, line)

    # --- Key figures ---
    y -= 34
    text(56, y, 12, "F2", NAVY, "Key Figures")
    y -= 8
    for line in [
        "67+ team members   |   10,000+ cases handled   |   17+ districts covered",
        "15+ bank & NBFI partnerships   |   12+ years of direct banking sector experience",
    ]:
        y -= 15
        text(56, y, 10, "F1", INK, line)

    # --- Services ---
    y -= 34
    text(56, y, 12, "F2", NAVY, "Service Lines")
    y -= 8
    for line in [
        "1. Recovery & Corporate Collection (bad and non-performing loans)",
        "2. Consultancy Services for financial and non-financial institutions",
        "3. Contact Point Verification (CPV)",
        "4. Auto Repossession Services",
        "5. Contractual Staff Support (banks, FIs, telecoms)",
        "6. Office Stationery Supply",
        "7. Sales & Direct-Selling Training Programs (upcoming)",
    ]:
        y -= 15
        text(56, y, 10, "F1", INK, line)

    # --- Leadership ---
    y -= 34
    text(56, y, 12, "F2", NAVY, "Board of Directors")
    y -= 8
    for line in [
        "Mr. Khan Ahasan Reza - Chairman",
        "Mr. Zqardar Mamunur Rashid - Managing Director",
        "Mr. Gilhaj Uddin - Director, Field Administration",
        "Md. Hasnain Talukder Shujon - Legal Advisor",
    ]:
        y -= 15
        text(56, y, 10, "F1", INK, line)

    # --- Compliance ---
    y -= 34
    text(56, y, 12, "F2", NAVY, "Code of Conduct")
    y -= 8
    for line in [
        "Fair competition. Confidentiality of client and borrower data.",
        "Zero tolerance for corruption and extortion in any form.",
    ]:
        y -= 15
        text(56, y, 10, "F1", INK, line)

    # --- Footer ---
    rect(0, 72, PAGE_W, 2, GOLD)
    text(56, 50, 9, "F1", MUTED,
         "Unique Consultancy & Collection Ltd.  |  Dhaka, Bangladesh  |  info@uccl.com.bd")
    text(56, 36, 8, "F1", MUTED,
         "This is a placeholder document generated for website development.")

    return "\n".join(ops)


def main() -> None:
    content = build_content()
    content_bytes = content.encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            "/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>"
        ).encode("latin-1"),
        b"<< /Length " + str(len(content_bytes)).encode() + b" >>\nstream\n"
        + content_bytes
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
    ]

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("latin-1") + body + b"\nendobj\n"

    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("latin-1")
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("latin-1")

    OUT.write_bytes(bytes(out))
    print(f"Wrote {OUT} ({len(out)} bytes)")


if __name__ == "__main__":
    main()

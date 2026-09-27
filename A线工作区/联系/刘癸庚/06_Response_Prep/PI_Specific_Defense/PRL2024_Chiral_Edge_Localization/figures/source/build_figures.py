"""Rebuild study crops. Never edits the source paper or research simulations."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
REPO = next(p for p in ROOT.parents if (p / 'A线_工作台.md').exists())
sys.path.insert(0, str(REPO / 'A线工作区/核验/a4_runtime'))
import pymupdf

out = ROOT / 'figures/output'
out.mkdir(exist_ok=True, parents=True)
paper = pymupdf.open(ROOT / 'sources/paper_published.pdf')
# Coordinates in PDF points, include each original caption.
clips = {2: (1, (311, 272, 565, 725)),
         3: (2, (311, 468, 565, 725)),
         4: (3, (311, 44, 565, 389))}
for number, (page_number, coordinates) in clips.items():
    rect = pymupdf.Rect(coordinates)
    pdf = pymupdf.open()
    page = pdf.new_page(width=rect.width, height=rect.height)
    page.show_pdf_page(page.rect, paper, page_number, clip=rect)
    pdf.save(out / f'figure_{number}.pdf', garbage=4, deflate=True)
    page.get_pixmap(dpi=300).save(out / f'figure_{number}.png')
    print(f'Fig. {number}: original PDF page {page_number + 1}; {rect}')

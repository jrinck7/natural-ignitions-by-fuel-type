#!/usr/bin/env bash
# build_pdf.sh - turn Project2.ipynb into a PDF.
#
# Same workflow as Project 1 (rebuild_pdf_zero_margins + fix_title):
#   nbconvert -> LaTeX -> set page margins -> fix the title -> xelatex x3
#
# Run from anywhere:   bash build_pdf.sh
# Output:              pdfs/Project2.pdf
#
# Notes:
# - nbconvert does NOT re-run your notebook. It uses the outputs saved in
#   Project2.ipynb, so run the notebook and save it (Ctrl+S) first.
# - Needs xelatex (TeX Live) on whatever machine/container you run this in.

set -euo pipefail

# ---- Settings you might want to change ----
NOTEBOOK="Project2"                                                  # notebook name, no extension
MARGIN="0.5in"                                                       # page margin on all four sides
TITLE="Project 2: Natural Wildfire Ignitions by Ecoregion and Fuel Type"
OUTDIR="pdfs"                                                        # where the .tex / .pdf are written
HEADING_ID="project-2-launch"                                        # id of the notebook's first "# ..." heading (removed so it isn't repeated under the title)
# --------------------------------------------

cd "$(dirname "$0")"

# Checks
command -v jupyter  >/dev/null || { echo "jupyter not found."; exit 1; }
command -v xelatex  >/dev/null || { echo "xelatex not found. Install TeX Live, or run this where Project 1 was built."; exit 1; }
if [ ! -f "${NOTEBOOK}.ipynb" ]; then
  echo "${NOTEBOOK}.ipynb not found. Regenerate it with: jupytext --to notebook ${NOTEBOOK}.py"
  exit 1
fi

mkdir -p "$OUTDIR"

# 1) Notebook -> LaTeX (figures are extracted to ${OUTDIR}/${NOTEBOOK}_files/)
jupyter nbconvert --to latex "${NOTEBOOK}.ipynb" --output-dir "$OUTDIR"

cd "$OUTDIR"

# 2) Page margins
sed -i "s/\\\\geometry{verbose,tmargin=[^}]*}/\\\\geometry{verbose,tmargin=${MARGIN},bmargin=${MARGIN},lmargin=${MARGIN},rmargin=${MARGIN}}/" "${NOTEBOOK}.tex"
grep -q "tmargin=${MARGIN}" "${NOTEBOOK}.tex" || echo "Warning: margin line not found in the .tex, margins were not changed."

# 3) Title: real title instead of the filename, and drop the duplicate numbered heading
python3 - "${NOTEBOOK}.tex" "$TITLE" "$HEADING_ID" <<'PY'
import re, sys

path, title, heading_id = sys.argv[1], sys.argv[2], sys.argv[3]
tex = open(path, encoding="utf-8").read()

# Replace the auto-generated \title{Project2}
tex = tex.replace(r"\title{Project2}", "\\title{" + title + "}")

# Remove the numbered heading pandoc built from the notebook's first "# ..." cell
pattern = re.compile(
    r"\\hypertarget\{" + re.escape(heading_id) + r"\}\{%.*?\\label\{" + re.escape(heading_id) + r"\}\}\n?",
    re.DOTALL,
)
tex, n = pattern.subn("", tex)
if n == 0:
    print("Warning: first-heading block not found. If you renamed the notebook's "
          "top heading, update HEADING_ID in build_pdf.sh.", file=sys.stderr)

# The .tex is compiled inside pdfs/, but markdown images in the notebook point
# at images/... relative to the repo root. Search the parent folder too so
# those figures are found (cell-output figures in pdfs/Project2_files/ still
# resolve from ./).
tex = tex.replace("\\begin{document}", "\\graphicspath{{./}{../}}\n\\begin{document}", 1)

open(path, "w", encoding="utf-8").write(tex)
PY

# 4) Compile (3 passes so links and the table of contents settle)
rm -f "${NOTEBOOK}.aux" "${NOTEBOOK}.out" "${NOTEBOOK}.toc"
for pass in 1 2 3; do
  xelatex -interaction=nonstopmode "${NOTEBOOK}.tex" > "xelatex_pass${pass}.log" 2>&1 || true
done

if [ -f "${NOTEBOOK}.pdf" ]; then
  echo "Done: $(pwd)/${NOTEBOOK}.pdf (margins ${MARGIN})"
else
  echo "PDF was not created. Last lines of the LaTeX log:"
  tail -30 "xelatex_pass3.log"
  exit 1
fi

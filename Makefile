.PHONY: all clean dataset figures pdf

all: dataset figures pdf

dataset:
	python3 scripts/generate_unified_dataset.py

figures:
	python3 scripts/generate_unified_figures.py

pdf:
	cd manuscript && pdflatex -interaction=nonstopmode main.tex
	cd manuscript && bibtex main
	cd manuscript && pdflatex -interaction=nonstopmode main.tex
	cd manuscript && pdflatex -interaction=nonstopmode main.tex

clean:
	rm -rf manuscript/*.aux manuscript/*.log manuscript/*.out manuscript/*.bbl manuscript/*.blg manuscript/*.toc manuscript/*.pdf

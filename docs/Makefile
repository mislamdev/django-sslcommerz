# Makefile for Django SSLCOMMERZ Documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Custom targets for Django SSLCOMMERZ

install:
	@echo "Installing documentation dependencies..."
	pip install sphinx sphinx-rtd-theme myst-parser sphinxcontrib-httpdomain

clean:
	@echo "Cleaning documentation build..."
	rm -rf $(BUILDDIR)/
	rm -rf _autosummary/

html:
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo "Documentation built. Open _build/html/index.html to view."

serve: html
	@echo "Serving documentation at http://localhost:8080"
	@cd $(BUILDDIR)/html && python -m http.server 8080

linkcheck:
	@echo "Checking external links..."
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

spelling:
	@echo "Checking spelling..."
	@$(SPHINXBUILD) -b spelling "$(SOURCEDIR)" "$(BUILDDIR)/spelling" $(SPHINXOPTS) $(O)

api:
	@echo "Generating API documentation..."
	sphinx-apidoc -o . ../sslcommerz --force --module-first

livehtml:
	@echo "Starting live reload server..."
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" --host 0.0.0.0 --port 8080

deploy: html
	@echo "Deploying to GitHub Pages..."
	@../scripts/build-docs.sh deploy

all: clean api html linkcheck
	@echo "Complete documentation build finished."

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

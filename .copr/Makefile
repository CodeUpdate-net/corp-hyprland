.PHONY: srpm

# COPR invokes this target from the configured package subdirectory. Source
# preparation is the only networked stage; binary Mock builds stay offline.
srpm:
	dnf -y install rpm-build rpmdevtools
	spectool -g "$(spec)"
	sha256sum --check sources
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(outdir)" \
		"$(spec)"

# Operations runbook

## Prepare a stable update

1. Read upstream release notes for Hyprland and all changed first-party
   dependencies.
2. Update `package-set.yaml`, source checksums, specs, patches, and package notes.
3. Recompute the dependency graph. Any library ABI change expands the release
   set to all downstream packages, even if their upstream versions did not
   change.
4. Run local validation and a clean Mock build of the affected graph.
5. Create a release manifest with status `candidate`, the Git commit, previous
   release-set ID, package versions, and empty COPR build-ID fields.
6. Merge only after review and CI success.

## Build in COPR

1. Confirm production repository metadata is still at the previous known-good
   release.
2. Submit packages in dependency waves. Use COPR build batches or wait for each
   dependency wave before starting its consumers.
3. Record build IDs and chroot results in the release manifest.
4. On failure, fix the candidate in Git and rebuild the affected package and
   every ABI-sensitive downstream consumer.
5. Do not waive a required stable chroot merely because Rawhide succeeds.

## Validate a candidate

For each stable Fedora target:

- run repository closure checks;
- perform a clean install in a disposable root or VM;
- upgrade a system containing Fedora's Hyprland packages;
- verify expected EVRs with `rpm -q` and `dnf repoquery`;
- run command-level smoke tests;
- launch a Hyprland session in a VM/nested test and exercise the portal, locker,
  idle daemon, wallpaper daemon, and a matching official plugin;
- inspect logs for unresolved symbols, plugin ABI errors, portal selection
  conflicts, and missing shared libraries.

Record test evidence in the release manifest.

## Publish

1. Confirm every required build and test is green.
2. Record the current public release as the rollback target.
3. Regenerate the COPR repositories once, promoting the development results.
4. Install from the public repository on clean systems for both stable Fedora
   versions.
5. Mark the manifest `published` with its timestamp and publish release notes.

## Roll back

Prefer a forward-fix package release when a narrow packaging error can be
corrected quickly. For a release-set regression:

1. stop further candidate builds and announce the affected targets;
2. identify the last known-good build set from the prior release manifest;
3. rebuild the known-good sources with a newer RPM Release when necessary—COPR
   cannot safely “undo” an already consumed NEVR by merely exposing an older
   package;
4. validate the rebuilt set with the normal gates;
5. regenerate repository metadata and publish explicit recovery commands;
6. keep the failed manifest and document the cause rather than deleting its
   history.

If only one optional application is broken and removing it does not break
closure, retire that package from the candidate and publish the rest with the
exception documented.

## Fedora branching and EOL

The project follows Fedora branching, but automatic chroot creation is not the
same as support readiness.

After Fedora branches:

1. verify COPR created both architecture chroots;
2. rebuild the complete release set rather than relying indefinitely on copied
   Rawhide results;
3. run install and upgrade tests on the branched release;
4. add it to the documented support matrix only after tests pass.

When Fedora reaches EOL:

1. announce the removal date;
2. stop promising fixes for that target;
3. disable its COPR chroots after the announced window;
4. update docs and CI; do not let an EOL failure block supported releases.

## Dependency overlay retirement

At every Fedora release and at least monthly:

1. compare Fedora's dependency EVRs and ABI requirements to the package set;
2. test the release set without each conditional overlay candidate;
3. remove a dependency package when all stable targets satisfy consumers from
   Fedora;
4. verify `dnf distro-sync` before publishing the retirement.

Smaller overlays reduce conflicts and maintenance burden.

## Incident checklist

- Freeze publication; leave build logs and manifests intact.
- Capture affected Fedora version, architecture, package NEVRs, COPR build IDs,
  reproduction steps, and relevant journal output.
- Reproduce in a clean environment before changing specs.
- Classify the failure: packaging, upstream, Fedora dependency, architecture,
  repository consistency, or user configuration.
- Fix only in the candidate/development repository, run downstream rebuilds,
  and promote through the standard gates.
- Publish a short incident note and any user recovery command.

Never ask users to disable signature checks, replace arbitrary system
libraries, or erase RPM database state as a workaround.

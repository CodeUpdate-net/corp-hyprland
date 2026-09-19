# Build, test and publish runbook

Project: `dtutila/hyprland`. Current targets: Fedora 44 and 45, x86_64 only.
libsecret is maintained separately in `dtutila/utils`.

## Prepare and validate an update

1. Read upstream release notes and review source provenance, licenses, patches
   and security changes. Update `package-set.yaml`, specs and checksums together.
2. Increment RPM Release for packaging changes. Rebuild all ABI-sensitive
   consumers of changed libraries. Keep `hyprland-plugins` BuildRequires and
   Requires pinned to the exact Hyprland Version-Release; `scripts/check` enforces
   this. A new Hyprland build needs a new plugin release even without a plugin
   source update.
3. Run `./scripts/check`, then build **every package** with Podman for both
   targets as documented in [build-and-test.md](build-and-test.md). Run the
   [security audit](security-audit.md), and keep the results.
4. Record the candidate release ID, immutable Git commit, previous release,
   package NEVRAs, local gate logs, COPR build IDs and per-chroot outcomes in a
   release record. A successful source build alone is insufficient.
5. Review the diff and CI results, then commit to `release-set/<id>` and push.

Assign a new `release_set` before submitting a new candidate. The audit-fix
candidate is `2026-09-19.1`, following public release `2026-09-18.1`. Track its
source commit, build IDs and publication state in `releases/`.

## GitHub identity

Read access to this repository was verified with `id_ed25519_dtutila` on
2026-09-18. The repository-local SSH command is pinned to that key:

```bash
git config --local core.sshCommand 'ssh -i ~/.ssh/id_ed25519_dtutila -o IdentitiesOnly=yes'
git ls-remote origin HEAD
git push -u origin HEAD
```

The `git push` command is for the release operator after review. A read-only
`ls-remote` test does not prove write permission. A repository-local setting
avoids changing the identity for unrelated GitHub repositories. Do not copy
private keys into Git or containers. The old session note's `.pub` path may work
only when the matching private key is held by an agent; the verified command
above uses the identity path directly.

## Submit COPR builds

Check that manual publication is on and binary networking is off:

```bash
copr-cli whoami
curl -fsSL 'https://copr.fedorainfracloud.org/api_3/project?ownername=dtutila&projectname=hyprland' | python3 -m json.tool
./scripts/render-build-order
```

Do not submit if `devel_mode` is false, `enable_net` is true, or the target matrix
unexpectedly differs. If necessary, restore the reviewed project settings:

```bash
copr-cli modify dtutila/hyprland --disable_createrepo true --enable-net off
```

Build the reviewed and pushed commit in dependency order. A sequential loop is
slower but easy to audit; `buildscm` waits unless `--nowait` is supplied:

```bash
set -euo pipefail
candidate_commit=$(git rev-parse HEAD)
python3 scripts/package_set.py --format order > /tmp/hyprland-build-order
while read -r package; do
  copr-cli buildscm dtutila/hyprland \
    --clone-url https://github.com/CodeUpdate-net/corp-hyprland.git \
    --commit "$candidate_commit" \
    --subdir "packages/$package" --spec "$package.spec" \
    --type git --method make_srpm --enable-net off
done < /tmp/hyprland-build-order
```

Capture the output/build IDs in the release record. Confirm each build succeeded
on both chroots. `--after-build-id` and `--with-build-id` can organize parallel
waves, but a failed wave blocks its consumers and publication. Never submit
against a moving branch name when recording a candidate.

## Test the candidate

Freeze submissions and identify the exact candidate repository/builds before
testing. COPR distinguishes public and development metadata; testing the public
repository while a new candidate is withheld tests the previous release. Use
COPR's displayed development repository URL for the configured storage backend,
or download the exact signed build artifacts by recorded build ID. Do not guess
a development URL for Pulp storage.

For each target, in disposable roots or VMs:

- Check complete repository dependency closure and run `dnf check` after install.
- Install every produced runtime and devel package; compare `rpm -q` NEVRAs to
  the release record so Fedora or an older COPR build cannot mask a missing RPM.
- Upgrade from Fedora's Hyprland packages and from the previous public release.
  Inspect the transaction for unintended removals or downgrades.
- Review RPM Provides, Requires, file permissions, scripts and licenses. Keep
  COPR signature checks enabled.
- Run safe version/help commands. Launch a nested/VM Hyprland session and test
  a matching plugin, screen sharing, lock/unlock, idle, wallpaper and polkit
  authentication, including cancellation and failed authentication.
- Check logs for missing libraries, unresolved symbols, plugin ABI errors,
  portal conflicts and crashes. Container install success does not cover this.

For reproducible nested coverage and its limits, see
[runtime-testing.md](runtime-testing.md). Record the release-specific scope; a
maintenance update must not claim that unchanged desktop services received full
VM/hardware qualification when only the nested checks ran.

Useful inspection commands (with the candidate RPM path selected explicitly):

```bash
rpm -K candidate.rpm
rpm -qp --requires candidate.rpm
rpm -qp --provides candidate.rpm
rpm -qp --scripts candidate.rpm
rpm -qplv candidate.rpm
```

## Publish manually

Once every required gate passes, record the previous public release and confirm
that the candidate has not changed. Regeneration publishes project repositories,
so inspect all pending successful builds, including unrelated submissions.

The following command is the publication step and must be run intentionally by
the release operator after reviewing the candidate evidence:

```bash
copr-cli regenerate-repos dtutila/hyprland
```

Wait for public metadata regeneration, then test a fresh install on both targets:

```bash
sudo dnf copr enable dtutila/hyprland
sudo dnf install hyprland
rpm -q hyprland
```

Record publication time, metadata/build IDs and public install results. Merge
or fast-forward the tested candidate into `main` without changing its content.
Manual mode remains on for future builds. It does not make a release transaction
atomic across machines or guarantee that an already-running compositor has
reloaded its libraries; users should restart their session after stack updates.

## Rollback, branching and incidents

Freeze publication on regressions. Prefer a forward fix. If reverting source,
produce a newer RPM Release, rebuild affected consumers, repeat the same gates,
and publish explicit recovery instructions. Merely exposing older RPMs does not
undo versions already installed by users. Preserve failed build evidence.

When Fedora branches, check the actual project matrix, rebuild the entire stack,
and add support only after installation, upgrade and session tests. aarch64 is
currently deferred. At EOL, retire targets deliberately and update docs and CI.
Review the dependency overlay monthly and remove packages Fedora can satisfy,
after testing `dnf distro-sync` and repository closure.

Never advise disabling signature checking or replacing arbitrary system
libraries to bypass a broken release. See [security-audit.md](security-audit.md)
for security incidents and audit evidence.

## Retrieve exact builds for candidate or upgrade testing

The installed CLI can fetch artifacts by build ID without rebuilding or
publishing. For example:

```bash
copr-cli download-build --rpms -r fedora-45-x86_64 \
  --dest results/candidate 11002509
```

Replace the example with each build ID from the selected release record. The
command can download source RPMs as well as binary RPMs: exclude `*.src.rpm`,
`*debuginfo*` and `*debugsource*` from runtime-install lists. Generate a local
repository from the selected binaries with `createrepo_c`, configure the COPR
public key and `gpgcheck=1`, and test in a disposable Fedora root. For upgrade
tests, install the recorded previous set first, then switch to the candidate
set and verify all resulting NEVRAs. Never mix build IDs from different release
sets simply because their downloads succeeded.

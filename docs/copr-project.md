# COPR project definition

## Intended state

This is the human-readable, reviewable definition of the production project.
The implementation should turn it into an idempotent bootstrap/check script
after the owner and repository URL are known.

```yaml
owner: <FAS_USERNAME>
name: hyprland
homepage: <PUBLIC_GIT_REPOSITORY_URL>
contact: <ISSUE_TRACKER_OR_CONTACT_URL>
description: >-
  Stable Hyprland, first-party Hyprland ecosystem packages, and only the
  dependency overlay required to keep the stack compatible on Fedora.
instructions: |-
  Enable and install:
    sudo dnf copr enable <FAS_USERNAME>/hyprland
    sudo dnf install hyprland

  This repository intentionally does not provide Noctalia or a complete
  desktop configuration. Report packaging issues at <ISSUE_TRACKER_URL>.
settings:
  persistent: false
  auto_prune: true
  follow_fedora_branching: true
  build_network: false
  appstream: true
  fedora_review: true
  module_hotfixes: false
  unlisted: false
  repo_priority: null
  manual_repository_publication: true
architectures:
  - x86_64
  - aarch64
chroot_policy:
  required:
    - current stable Fedora
    - previous stable Fedora
  pre_release:
    - Fedora Branched
    - Fedora Rawhide
```

`persistent: false` means normal COPR pruning policy applies; it does **not**
make the project temporary. `manual_repository_publication: true` corresponds
to COPR's “Create repositories manually” setting, called `devel_mode` by the
API and `--disable-createrepo` by `copr-cli`.

## Chroot snapshot

On 2026-09-01, the reference project exposed Fedora 43, 44, 45, and Rawhide for
both `x86_64` and `aarch64`. Chroot availability is time-sensitive. At project
creation, resolve “current”, “previous”, “Branched”, and “Rawhide” to the chroot
names COPR actually offers; do not copy this snapshot blindly.

The intended initial matrix, if all remain active, is:

```text
fedora-43-x86_64       fedora-43-aarch64
fedora-44-x86_64       fedora-44-aarch64
fedora-45-x86_64       fedora-45-aarch64
fedora-rawhide-x86_64  fedora-rawhide-aarch64
```

Stable chroots are required. Branched and Rawhide should initially be treated
as required build signals but are not promoted as end-user support promises.

## Bootstrap checklist

1. Install `copr-cli` and obtain the token from the authenticated COPR API page:

   ```bash
   sudo dnf install copr-cli
   install -d -m 0700 ~/.config
   $EDITOR ~/.config/copr
   chmod 0600 ~/.config/copr
   copr-cli whoami
   ```

2. Check the CLI's current option spelling before running the create command:

   ```bash
   copr-cli create --help
   copr-cli modify --help
   copr-cli list-chroots
   ```

3. Create the project with the resolved chroots. A representative command is
   shown below; reconcile it with the installed CLI because COPR option names
   can change:

   ```bash
   copr-cli create hyprland \
     --chroot fedora-43-x86_64 \
     --chroot fedora-43-aarch64 \
     --chroot fedora-44-x86_64 \
     --chroot fedora-44-aarch64 \
     --chroot fedora-45-x86_64 \
     --chroot fedora-45-aarch64 \
     --chroot fedora-rawhide-x86_64 \
     --chroot fedora-rawhide-aarch64 \
     --fedora-review \
     --appstream on \
     --disable-createrepo
   ```

4. In the web settings or via `copr-cli modify`, enable “Follow Fedora
   branching”, enable automatic pruning, disable build networking, and fill in
   the description, instructions, homepage, and contact fields.

5. Compare the API response to the intended state:

   ```bash
   curl -fsSL \
     'https://copr.fedorainfracloud.org/api_3/project?ownername=<FAS_USERNAME>&projectname=hyprland' \
     | jq
   ```

6. Add one SCM package per entry in `package-set.yaml`. For example:

   ```bash
   copr-cli add-package-scm hyprland \
     --name hyprutils \
     --clone-url <PUBLIC_GIT_REPOSITORY_URL> \
     --subdir packages/hyprutils \
     --spec hyprutils.spec \
     --type git \
     --method make_srpm
   ```

   Run `copr-cli add-package-scm --help` first and adjust spelling to the
   installed client. Leave production auto-rebuild disabled.

7. Build a bootstrap wave, verify it, then proceed through the dependency waves
   in [package-scope.md](package-scope.md). Do not regenerate public repository
   metadata until the complete release set passes.

## User-facing installation text

Publish this only after the first release is promoted:

```bash
sudo dnf copr enable <FAS_USERNAME>/hyprland
sudo dnf install hyprland
```

Optional first-party utilities remain explicit so the repository does not
force an opinionated desktop:

```bash
sudo dnf install \
  hypridle hyprlock hyprpaper hyprpicker hyprsunset \
  xdg-desktop-portal-hyprland
```

Document the removal path beside the install instructions:

```bash
sudo dnf copr disable <FAS_USERNAME>/hyprland
sudo dnf distro-sync --refresh
```

Users should review the proposed transaction before confirming `distro-sync`.

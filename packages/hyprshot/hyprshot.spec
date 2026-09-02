Name:           hyprshot
Version:        1.3.0
Release:        2%{?dist}
Summary:        Interactive screenshot utility for Hyprland
License:        GPL-3.0-only
URL:            https://github.com/Gustash/hyprshot
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch0:         0001-harden-command-geometry-and-picker-handling.patch

BuildArch:      noarch
BuildRequires:  bash
BuildRequires:  ShellCheck
BuildRequires:  util-linux

Requires:       bash
Requires:       grim
Requires:       hyprland
Requires:       jq
Requires:       /usr/bin/notify-send
Requires:       slurp
Requires:       util-linux
Requires:       wl-clipboard
Recommends:     hyprpicker
Recommends:     xdg-user-dirs

%description
Hyprshot is an interactive screenshot utility for Hyprland. It captures
windows, outputs, and selected regions, saves PNG files, and copies captures
to the Wayland clipboard.

%prep
%autosetup -n Hyprshot-%{version} -p1

%build

%install
install -Dpm 0755 hyprshot %{buildroot}%{_bindir}/hyprshot

%check
bash -n hyprshot
shellcheck --severity=warning hyprshot
bash hyprshot -r -h | grep -F "Usage: hyprshot"

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprshot

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 1.3.0-2
- Remove trailing whitespace from the downstream hardening patch

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 1.3.0-1
- Initial package with hardened argument, geometry, and process handling

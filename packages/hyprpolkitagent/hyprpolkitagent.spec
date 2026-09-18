Name:           hyprpolkitagent
Version:        0.2.0
Release:        1%{?dist}
Summary:        Polkit authentication agent for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpolkitagent
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(hyprgraphics)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(sdbus-c++) >= 2
BuildRequires:  systemd-rpm-macros

Requires:       polkit

%description
Hyprpolkitagent provides graphical PolicyKit authentication prompts.

%prep
%autosetup -p1

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libexecdir}/hyprpolkitagent
%{_datadir}/dbus-1/services/org.hyprland.hyprpolkitagent.service
%{_userunitdir}/hyprpolkitagent.service

%changelog
* Fri Sep 18 2026 COPR Maintainer <noreply@example.invalid> - 0.2.0-1
- Update to 0.2.0 (frontend ported from Qt/QML to hyprtoolkit)
- Replace the Qt6 and polkit-qt6 build dependencies with hyprtoolkit, hyprgraphics, hyprlang, and sdbus-c++
- Require polkit at runtime; the agent now speaks to polkitd over D-Bus instead of linking libpolkit-agent-1
- Pick up the PAM re-dispatch loop fix and the hidden password field while a fingerprint or key is pending

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.3-1
- Initial package

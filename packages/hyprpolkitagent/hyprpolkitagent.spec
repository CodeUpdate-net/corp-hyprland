Name:           hyprpolkitagent
Version:        0.1.3
Release:        1%{?dist}
Summary:        Polkit authentication agent for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprpolkitagent
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickControls2)
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  pkgconfig(hyprutils)
BuildRequires:  pkgconfig(polkit-agent-1)
BuildRequires:  pkgconfig(polkit-qt6-1)
BuildRequires:  systemd-rpm-macros

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
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.3-1
- Initial package

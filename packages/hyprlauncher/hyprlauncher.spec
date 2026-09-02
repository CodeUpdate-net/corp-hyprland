Name:           hyprlauncher
Version:        0.1.6
Release:        1%{?dist}
Summary:        Application launcher for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprlauncher
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils) >= 0.10.2
BuildRequires:  pkgconfig(hyprwire)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libqalculate)
BuildRequires:  pkgconfig(pixman-1)

%description
Hyprlauncher is a multipurpose application launcher and picker for Hyprland.

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
%{_bindir}/hyprlauncher

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.6-1
- Initial package

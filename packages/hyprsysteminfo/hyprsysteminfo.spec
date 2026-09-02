Name:           hyprsysteminfo
Version:        0.2.0
Release:        1%{?dist}
Summary:        System information utility for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprsysteminfo
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  glaze-devel
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils) >= 0.10.2
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpci)
BuildRequires:  pkgconfig(pixman-1)

%description
Hyprsysteminfo displays compositor, graphics, and system information.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprsysteminfo
%{_datadir}/applications/hyprsysteminfo.desktop

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.2.0-1
- Initial package

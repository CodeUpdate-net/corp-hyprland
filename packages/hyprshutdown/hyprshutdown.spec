Name:           hyprshutdown
Version:        0.1.1
Release:        1%{?dist}
Summary:        Graceful shutdown utility for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprshutdown
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  glaze-devel
BuildRequires:  pkgconfig(hyprtoolkit)
BuildRequires:  pkgconfig(hyprutils) >= 0.11.0
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(pixman-1)

%description
Hyprshutdown presents a graceful logout and shutdown interface for Hyprland.

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
%{_bindir}/hyprshutdown

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.1-1
- Initial package

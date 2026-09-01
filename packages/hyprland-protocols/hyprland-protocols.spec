Name:           hyprland-protocols
Version:        0.7.0
Release:        1%{?dist}
Summary:        Wayland protocol extensions for Hyprland

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-protocols
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  meson

%description
Wayland protocol extensions used by Hyprland and applications integrating
with the compositor.

%package devel
Summary:        Development files for Hyprland protocol extensions

%description devel
Protocol XML files and pkg-config metadata for building software that uses
Hyprland-specific Wayland protocols.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

%check
%meson_test

%files devel
%license LICENSE
%doc README.md
%{_datadir}/hyprland-protocols/
%{_datadir}/pkgconfig/hyprland-protocols.pc

%changelog
* Tue Sep 01 2026 Hyprland COPR maintainers - 0.7.0-1
- Initial package for the coherent Hyprland stack

Name:           hyprqt6engine
Version:        0.1.0
Release:        1%{?dist}
Summary:        Qt 6 platform theme and style for Hyprland
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprqt6engine
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Patch0:         0001-find-Qt6GuiPrivate.patch

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  qt6-qtbase-private-devel >= 6.9
BuildRequires:  pkgconfig(hyprlang)
BuildRequires:  pkgconfig(hyprutils)

%description
Hyprqt6engine integrates Hyprland colors and settings into Qt 6 applications.

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
%{_libdir}/libhyprqt6engine-common.so*
%{_libdir}/qt6/plugins/platformthemes/libhyprqt6engine.so
%{_libdir}/qt6/plugins/styles/libhypr-style.so

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.0-1
- Initial package

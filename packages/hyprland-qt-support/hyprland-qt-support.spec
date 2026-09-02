Name:           hyprland-qt-support
Version:        0.1.0
Release:        1%{?dist}
Summary:        Shared Qt Quick style for Hyprland applications
License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-qt-support
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExcludeArch:    %{ix86}
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  cmake(Qt6Qml) >= 6.6
BuildRequires:  cmake(Qt6Quick) >= 6.6
BuildRequires:  cmake(Qt6QuickControls2) >= 6.6
BuildRequires:  pkgconfig(hyprlang) >= 0.6.0

%description
Reusable Qt Quick styling modules for applications in the Hyprland ecosystem.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=%{_lib} \
  -DBUILD_TESTER=OFF \
  -DINSTALL_QMLDIR=%{_libdir}/qt6/qml
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprland-quick-style*.so*
%{_libdir}/qt6/qml/org/hyprland/style/

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 0.1.0-1
- Initial package

Name:           glaze
Version:        7.2.0
Release:        1%{?dist}
Summary:        Extremely fast JSON and interface library for modern C++
License:        MIT
URL:            https://github.com/stephenberry/glaze
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
Glaze is a high-performance JSON and reflection library for modern C++.

%package devel
Summary:        Development files for %{name}

%description devel
Header-only development files and CMake metadata for %{name}.

%prep
%autosetup -p1

%build
%cmake \
  -Dglaze_DEVELOPER_MODE=OFF \
  -Dglaze_BUILD_EXAMPLES=OFF \
  -Dglaze_ENABLE_SSL=OFF
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_includedir}/glaze/
%{_datadir}/glaze/

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 7.2.0-1
- Initial package

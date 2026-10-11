Name:           glaze
Version:        7.9.1
Release:        1%{?dist}
Summary:        Extremely fast JSON and interface library for modern C++
License:        MIT AND BSD-3-Clause
URL:            https://github.com/stephenberry/glaze
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        consumer-smoke.cpp
Source2:        cmake-LICENSE.rst
Source3:        zmij-LICENSE
Patch0:         0001-disable-bundled-asio.patch
BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
Glaze is a high-performance JSON and reflection library for modern C++.

%package devel
Summary:        Development files for %{name}
Provides:       bundled(fast_float)
Provides:       bundled(zmij)

%description devel
Header-only development files and CMake metadata for %{name}.

%prep
%autosetup -p1
cp -p %{SOURCE2} %{SOURCE3} .

%build
%cmake \
  -Dglaze_DEVELOPER_MODE=OFF \
  -Dglaze_BUILD_EXAMPLES=OFF \
  -Dglaze_ENABLE_SSL=OFF \
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON
%cmake_build

%install
%cmake_install

%check
%{__cxx} %{build_cxxflags} -std=c++23 -Iinclude %{SOURCE1} \
  %{build_ldflags} -o consumer-smoke
./consumer-smoke

%files devel
%license LICENSE cmake-LICENSE.rst zmij-LICENSE
%doc README.md
%{_includedir}/glaze/
%{_datadir}/glaze/

%changelog
* Sun Oct 11 2026 COPR Maintainer <noreply@example.invalid> - 7.9.1-1
- Update to the newest compatible Glaze 7 release with upstream parser and file I/O fixes
- Disable optional Asio downloads by default and check JSON consumer APIs
- Preserve BSD CMake and MIT formatter notices; declare bundled parser/formatter code

* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 7.2.0-1
- Initial package

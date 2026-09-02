Name:           lua55
Version:        5.5.0
Release:        1%{?dist}
Summary:        Parallel-installable Lua 5.5 runtime for Hyprland
License:        MIT
URL:            https://github.com/lua/lua
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        lua55.pc.in
Source2:        lua.hpp
Source3:        LICENSE

BuildRequires:  gcc
BuildRequires:  make

%description
Lua 5.5 runtime packaged under a versioned library name for Fedora releases
whose system Lua is older. This package does not replace the system Lua.

%package devel
Summary:        Development files for the parallel Lua 5.5 runtime
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and pkg-config metadata for embedding the parallel Lua 5.5 runtime.

%prep
%autosetup -n lua-%{version} -p1
cp -p %{SOURCE3} LICENSE

%build
%make_build -f makefile \
  CC="%{__cc}" \
  CFLAGS="%{build_cflags} -fPIC -std=c99 -DLUA_USE_LINUX" \
  MYLDFLAGS="%{build_ldflags} -Wl,-E" \
  MYLIBS="-ldl"

ar d liblua.a ltests.o
%{__cc} %{build_ldflags} -shared \
  -Wl,-soname,liblua5.5.so.0 \
  -Wl,--whole-archive liblua.a -Wl,--no-whole-archive \
  -lm -ldl -o liblua5.5.so.0.0.0

%install
install -Dpm0755 liblua5.5.so.0.0.0 \
  %{buildroot}%{_libdir}/liblua5.5.so.0.0.0
ln -s liblua5.5.so.0.0.0 %{buildroot}%{_libdir}/liblua5.5.so.0
ln -s liblua5.5.so.0 %{buildroot}%{_libdir}/liblua5.5.so

for header in lua.h luaconf.h lualib.h lauxlib.h; do
  install -Dpm0644 "$header" "%{buildroot}%{_includedir}/lua5.5/$header"
done
install -Dpm0644 %{SOURCE2} %{buildroot}%{_includedir}/lua5.5/lua.hpp

install -d %{buildroot}%{_libdir}/pkgconfig
sed -e 's|@LIBDIR@|%{_libdir}|g' \
    -e 's|@VERSION@|%{version}|g' \
    %{SOURCE1} > %{buildroot}%{_libdir}/pkgconfig/lua55.pc

%check
./lua -e 'assert(_VERSION == "Lua 5.5")'

%files
%license LICENSE
%{_libdir}/liblua5.5.so.0
%{_libdir}/liblua5.5.so.0.0.0

%files devel
%{_includedir}/lua5.5/
%{_libdir}/liblua5.5.so
%{_libdir}/pkgconfig/lua55.pc

%changelog
* Tue Sep 01 2026 COPR Maintainer <noreply@example.invalid> - 5.5.0-1
- Add a parallel Lua 5.5 runtime for Fedora 44

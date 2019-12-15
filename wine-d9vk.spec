%global debug_package %{nil}

%ifarch x86_64
%global target_x86_type 64
%else
%global target_x86_type 32
%endif

Name:           wine-d9vk
Version:        0.40.1
Release:        1%{?dist}
Summary:        A Direct3D9 to Vulkan layer using the DXVK backend

License:        zlib
URL:            https://github.com/Joshua-Ashton/d9vk
Source0:        %{url}/archive/%{version}/d9vk-%{version}.tar.gz
Source1:        wine-d3dx9-and-d3dcompiler.txt

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  glslang
BuildRequires:  meson
BuildRequires:  wine-devel

%ifarch x86_64
BuildRequires:  mingw64-filesystem
BuildRequires:  mingw64-binutils
BuildRequires:  mingw64-headers
BuildRequires:  mingw64-cpp
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-gcc-c++
BuildRequires:  mingw64-winpthreads-static
%else
BuildRequires:  mingw32-filesystem
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-headers
BuildRequires:  mingw32-cpp
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw32-winpthreads-static
%endif

Requires:       wine >= 4.13
Requires:       vulkan-loader%{?_isa}

# We want x86_64 users to always have also 32 bit lib, it's the same what wine does
%ifarch x86_64
Requires:       wine-d9vk(x86-32) = %{version}-%{release}
%endif

Requires(posttrans):   %{_sbindir}/alternatives
Requires(preun):       %{_sbindir}/alternatives

Recommends: winetricks

ExclusiveArch:  %{ix86} x86_64

%description
%{summary}

%prep
%setup -q -n d9vk-%{version}

%build
/usr/bin/meson \
  --buildtype=plain \
  --wrap-mode=nodownload \
  --auto-features=enabled \
  --cross-file build-wine%{target_x86_type}.txt \
  --buildtype release \
  --prefix / \
  -Denable_dxgi=false \
  -Denable_d3d10=false \
  -Denable_d3d11=false \
  . %{_vpath_builddir}
%meson_build
DESTDIR=%{_builddir}/install /usr/bin/ninja -C %{_vpath_builddir} -v install

/usr/bin/meson \
  --wipe \
  --buildtype=plain \
  --wrap-mode=nodownload \
  --auto-features=enabled \
  --cross-file build-win%{target_x86_type}.txt \
  --buildtype release \
  --prefix / \
  -Denable_dxgi=false \
  -Denable_d3d10=false \
  -Denable_d3d11=false \
  . %{_vpath_builddir}
%meson_build
DESTDIR=%{_builddir}/install /usr/bin/ninja -C %{_vpath_builddir} -v install

cp -v %{SOURCE1} %{_builddir}/%{buildsubdir}/

%install
mkdir -p %{buildroot}%{_libdir}/wine/
install -p -m 755 %{_builddir}/install/lib/d3d9.dll.so %{buildroot}%{_libdir}/wine/
install -p -m 755 %{_builddir}/install/bin/d3d9.dll %{buildroot}%{_libdir}/wine/d9vk-d3d9.dll

%post
echo "Please read %{_docdir}/%{name}/wine-d3dx9-and-d3dcompiler.txt" >&2

%posttrans
%{_sbindir}/alternatives --install %{_libdir}/wine/d3d9.dll 'wine-d3d9%{?_isa}' %{_libdir}/wine/d9vk-d3d9.dll 20

%postun
%{_sbindir}/alternatives --remove 'wine-d3d9%{?_isa}' %{_libdir}/wine/d9vk-d3d9.dll

%files
%license LICENSE
%doc README.md
%doc wine-d3dx9-and-d3dcompiler.txt
%{_libdir}/wine/d9vk-d3d9.dll
%{_libdir}/wine/d3d9.dll.so

%changelog
* Sun Dec 15 2019 Ivan Mironov <mironov.ivan@gmail.com> - 0.40.1-1
- Bump to upstream version 0.40.1

* Wed Dec 11 2019 Ivan Mironov <mironov.ivan@gmail.com> - 0.30-1
- Initial version of the package

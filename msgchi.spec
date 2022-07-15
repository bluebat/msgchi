Name:		msgchi
Version:	@VERSION@
Release:	1
Summary:	Translating messages from template files to chinese
License:	GPL, PD
Group:		Development/Tools
URL:		https://github.com/bluebat/msgchi
Source0:	https://github.com/bluebat/msgchi/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python3-devel
Requires:	python3, gettext

%description
msgchi is a Python3 script to help translators of chinese locales
by processing messages in .pot or other chinese .po files into
pre-translated chinese.

%prep
%setup -q

%build
make

%install
make DESTDIR=%{buildroot} install

%files
%license LICENSE
%doc README.md ChangeLog
%{_bindir}/*
%{_datadir}/%{name}
%{_datadir}/locale/*/LC_MESSAGES/*
%{_mandir}/man1/*

%clean
rm -rf %{buildroot}

%changelog
* Sun Jul 10 2022 Wei-Lun Chao <bluebat@member.fsf.org> - 2.2
- Update to 2.1
* Wed Jun 07 2017 Wei-Lun Chao <bluebat@member.fsf.org> - 1.0
- First release

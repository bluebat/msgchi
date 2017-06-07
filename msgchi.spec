Name:		msgchi
Version:	1.0
Release:	1
Summary:	Translating messages from template files to chinese
Summary(zh_TW):	將模板檔案中的軟體訊息翻譯為漢語
License:	GPL, PD
Group:		Development/Tools
URL:		https://github.com/bluebat/msgchi
Source0:	https://github.com/bluebat/msgchi/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python3-tools
Requires:	python3, gettext

%description
msgchi is a Python3 script to help translators of chinese locales
by processing messages in .pot or other chinese .po files
into pre-translated chinese.

%description -l cmn
msgchi 是一個以 Python3 編寫的命令稿，用來協助漢語語區的翻譯者，
將位於 .pot、.po 或其他模板檔案中的軟體訊息，預先翻譯為本地的語言。

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

%changelog
* Wed Jun 07 2017 Wei-Lun Chao <bluebat@member.fsf.org> - 1.0
- First release

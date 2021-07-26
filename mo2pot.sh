#!/bin/sh
# mo2pot, GPL (c) Wei-Lun Chao <bluebat@member.fsf.org>, 2020.

export TEXTDOMAIN=mo2pot
if [ "$1" == "" -o "$1" == "-h" -o "$1" == "--help" ] ; then
  echo $"usage": $0 $"DOMAIN-NAME" [$"LOCALE-DIR"]
  exit
fi
if [ "$2" == "" ] ; then
  _LOCALEDIR=/usr/share/locale
else
  _LOCALEDIR="$2"
fi
_PWDIR=$PWD
_TMPDIR=`mktemp -d`

mkdir -p $_TMPDIR/$1
rm -f $_TMPDIR/$1/*.po

cd $_LOCALEDIR
for _LOCALE in * ; do
  mo=$_LOCALEDIR/$_LOCALE/LC_MESSAGES/$1.mo
  if [ -e $mo ] ; then
    msgunfmt $mo | msgconv -t UTF-8 -o $_TMPDIR/$1/$_LOCALE.po
  fi
done

cd $_TMPDIR
rmdir --ignore-fail-on-non-empty $1
if [ -d $1 ] ; then
  msgcat --use-first $1/*.po -o $1.po
  msghack --empty $1.po -o $_PWDIR/$1.pot
else
  echo $"DOMAIN-NAME" $1 $"not found!"
fi
cd $_PWDIR

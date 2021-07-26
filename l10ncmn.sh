#!/bin/sh
# l10ncmn, GPL (c) Wei-Lun Chao <bluebat@member.fsf.org>, 2017.

export TEXTDOMAIN=l10ncmn
if [ "$1" == "" -o "$1" == "-h" -o "$1" == "--help" ] ; then
  echo $"usage": $0 $"DOMAIN-NAME" [$"LOCALE-DIR"]
  exit
fi
if [ "$2" == "" ] ; then
  _LOCALEDIR=/usr/share/locale
else
  _LOCALEDIR="$2"
fi
_LANG=cmn
_PWDIR=$PWD
_TMPDIR=`mktemp -d`
echo $_TMPDIR
mkdir -p $_TMPDIR/$1
rm -f $_TMPDIR/$1/*.po

cd $_LOCALEDIR
for _LOCALE in * ; do
  cd $_PWDIR
  mo=$_LOCALEDIR/$_LOCALE/LC_MESSAGES/$1.mo
  if [ -e $mo ] ; then
    case $_LOCALE in
      cmn ) msgunfmt $mo | msgconv -t UTF-8 -o $_TMPDIR/$1/0.po ;;
      zh_TW ) msgunfmt $mo | msgconv -t UTF-8 | msgchi -l zht2cmn -o $_TMPDIR/$1/1.po ;;
      zh_CN ) msgunfmt $mo | msgconv -t UTF-8 | msgchi -l zhc2cmn -o $_TMPDIR/$1/2.po ;;
      * ) msgunfmt $mo | msgconv -t UTF-8 -o $_TMPDIR/$1/$_LOCALE.po ;;
    esac
  fi
  cd $_LOCALEDIR
done

cd $_TMPDIR
rmdir --ignore-fail-on-non-empty $1
if [ -d $1 ] ; then
  msgcat --use-first $1/[a-z]*.po | msgchi -F -l eng2cmn -o $1/A.po
  msgcat --use-first -o $1.po $1/[012A].po
  msgattrib --clear-fuzzy $1.po | msgfmt - -o $1.mo
  if [ $(id -u) == 0 ] ; then
    cp -i $1.mo $_LOCALEDIR/$_LANG/LC_MESSAGES/$1.mo
  else
    cp -i $1.po $_PWDIR/$1.po
  fi
else
  echo $"DOMAIN-NAME" $1 $"not found!"
fi
cd $_PWDIR

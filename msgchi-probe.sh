#!/bin/sh
# msgchi-probe, GPL (c) Wei-Lun Chao <bluebat@member.fsf.org>, 2024.

export TEXTDOMAIN=msgchi-probe
if [ "$1" = "" -o "$1" = "-h" -o "$1" = "--help" ] ; then
  echo $"usage": $0 $"DOMAIN-NAME" [$"LOCALE-DIR"]
  exit
fi
_NAME="$1"
if [ "$2" = "" ] ; then
  _LOCALEDIR=/usr/share/locale
else
  _LOCALEDIR="$2"
fi
_LANG=cmn
_PWDIR=$PWD
_TMPDIR=`mktemp -d`
echo $_TMPDIR
mkdir -p $_TMPDIR/${_NAME}

cd $_LOCALEDIR
for _LOCALE in * ; do
  cd $_PWDIR
  _MO=$_LOCALEDIR/$_LOCALE/LC_MESSAGES/${_NAME}.mo
  if [ ${_NAME%_qt} = ${_NAME} ] ; then
    _QM=$_LOCALEDIR/'*'.qm
  else
    _QM=$_LOCALEDIR/$_LOCALE/LC_MESSAGES/${_NAME}.qm
  fi
  if [ -e "${_MO}" ] ; then
    case $_LOCALE in
      cmn ) msgunfmt ${_MO} | msgconv -t UTF-8 -o $_TMPDIR/${_NAME}/0.po ;;
      zh_TW ) msgunfmt ${_MO} | msgconv -t UTF-8 | msgchi -l zht2cmn -o $_TMPDIR/${_NAME}/1.po ;;
      zh_CN ) msgunfmt ${_MO} | msgconv -t UTF-8 | msgchi -l zhc2cmn -o $_TMPDIR/${_NAME}/2.po ;;
      * ) msgunfmt ${_MO} | msgconv -t UTF-8 -o $_TMPDIR/${_NAME}/$_LOCALE.po ;;
    esac
  elif ls ${_QM} &> /dev/null ; then
    if [ ${_NAME%_qt} = ${_NAME} ] ; then
      if [ ${_LOCALE##*.} = qm ] && [ ${_LOCALE#${_NAME}.} != ${_LOCALE} -o ${_LOCALE#${_NAME}_} != ${_LOCALE} -o ${#_LOCALE} -le 8 ] ; then
        lconvert $_LOCALEDIR/$_LOCALE -o $_TMPDIR/tmp.ts
        case $_LOCALE in
          *cmn.qm ) ts2po --progress none $_TMPDIR/tmp.ts -o $_TMPDIR/${_NAME}/0.po ;;
          *zh_TW.qm ) ts2po --progress none $_TMPDIR/tmp.ts | msgchi -l zht2cmn -o $_TMPDIR/${_NAME}/1.po ;;
          *zh_CN.qm ) ts2po --progress none $_TMPDIR/tmp.ts | msgchi -l zhc2cmn -o $_TMPDIR/${_NAME}/2.po ;;
          *.qm ) ts2po --progress none $_TMPDIR/tmp.ts -o $_TMPDIR/${_NAME}/${_LOCALE#*_}.po ;;
        esac
      fi
    else
      lconvert ${_QM} -o $_TMPDIR/tmp.ts
      case $_LOCALE in
        cmn ) ts2po --progress none $_TMPDIR/tmp.ts -o $_TMPDIR/${_NAME}/0.po ;;
        zh_TW ) ts2po --progress none $_TMPDIR/tmp.ts | msgchi -l zht2cmn -o $_TMPDIR/${_NAME}/1.po ;;
        zh_CN ) ts2po --progress none $_TMPDIR/tmp.ts | msgchi -l zhc2cmn -o $_TMPDIR/${_NAME}/2.po ;;
        * ) ts2po --progress none $_TMPDIR/tmp.ts -o $_TMPDIR/${_NAME}/$_LOCALE.po ;;
      esac
    fi
  fi
  cd $_LOCALEDIR
done

cd $_TMPDIR
rmdir --ignore-fail-on-non-empty ${_NAME}
if [ -d ${_NAME} ] ; then
  if ls ${_NAME}/[a-zA-Z]*.po &> /dev/null ; then
    msgcat --use-first ${_NAME}/[a-zA-Z]*.po | msgchi -F -l eng2cmn -o ${_NAME}/_.po
  fi
  msgcat --use-first ${_NAME}/[012_].po | msguniq -o ${_NAME}.po
  if [ -f tmp.ts ] ; then
    rm -f tmp.ts
    po2ts --progress none ${_NAME}.po ${_NAME}_cmn.ts
    if [ $(id -u) = 0 ] ; then
      lrelease-qt5 -silent ${_NAME}.ts
      cp -i ${_NAME}.ts ${_NAME}.qm $_PWDIR/
    else
     lconvert --drop-translations ${_NAME}_cmn.ts -o ${_NAME}.ts
      cp -i ${_NAME}_cmn.ts ${_NAME}.ts $_PWDIR/
    fi
  else
    if [ $(id -u) = 0 ] ; then
      msgattrib --clear-fuzzy ${_NAME}.po | msgfmt - -o ${_NAME}.mo
      cp -i ${_NAME}.po ${_NAME}.mo $_PWDIR/
    else
      msghack --empty -o ${_NAME}.pot ${_NAME}.po
      cp -i ${_NAME}.po ${_NAME}.pot $_PWDIR/
#    fi
  fi
else
  echo $"DOMAIN-NAME" ${_NAME} $"not found!"
fi
cd $_PWDIR

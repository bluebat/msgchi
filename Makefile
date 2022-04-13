VERSION = 2.0
DESTDIR =
PREFIX = /usr
PACKAGE = msgchi

LBITS := $(shell getconf LONG_BIT)
ifeq ($(LBITS), 64)
  LIBDIR = $(PREFIX)/lib64
else
  LIBDIR = $(PREFIX)/lib
endif

build:
	pygettext3.py -o $(PACKAGE).pot $(PACKAGE).py $(LIBDIR)/python3.*/optparse.py
	for i in *.po ; do msgfmt $$i -o $${i%.po}.gmo ; done

clean:
	rm -f *.gmo

install: build
	install -Dm755 $(PACKAGE).py $(DESTDIR)$(PREFIX)/bin/$(PACKAGE)
	for i in *.dic ; do install -Dm644 $$i $(DESTDIR)$(PREFIX)/share/$(PACKAGE)/$$i ; done
	install -Dm644 $(PACKAGE).1 $(DESTDIR)$(PREFIX)/share/man/man1/$(PACKAGE).1
	for i in *.gmo ; do install -Dm644 $$i $(DESTDIR)$(PREFIX)/share/locale/$${i%.gmo}/LC_MESSAGES/$(PACKAGE).mo ; done

uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PACKAGE)
	rm -rf $(DESTDIR)$(PREFIX)/share/$(PACKAGE)
	rm -f $(DESTDIR)$(PREFIX)/share/man/man1/$(PACKAGE).1
	rm -f $(DESTDIR)$(PREFIX)/share/locale/*/LC_MESSAGES/$(PACKAGE).mo

rpm: $(PACKAGE).spec
	rm -rf $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)
	mkdir -p $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)
	for f in eng2cmn.dic zht2cmn.dic zhc2cmn.dic cmn2yue.dic; do LANG=C sort $$f > $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)/$$f; done
	grep -v '#TEST' $(PACKAGE).py > $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)/$(PACKAGE).py
	cp {Makefile,$(PACKAGE).spec,README.md,LICENSE,ChangeLog} $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)
	sed -i 's/@VERSION@/$(VERSION)/' $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)/$(PACKAGE).py $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)/$(PACKAGE).spec
	cp *.po *.1 $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)
	sed -i '/rpm:/,$$d' $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION)/Makefile
	tar czf $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION).tar.gz -C $(HOME)/rpmbuild/SOURCES $(PACKAGE)-$(VERSION)
	rpmbuild -ta $(HOME)/rpmbuild/SOURCES/$(PACKAGE)-$(VERSION).tar.gz

test:
	LANG=C ./lensort-dic eng2cmn.dic > eng2cmn.sort ; mv -f eng2cmn.sort eng2cmn.dic ; ./msgchi.py -T -l eng2cmn test-eng.pot
#	LANG=C ./lensort-dic zhc2cmn.dic > zhc2cmn.sort ; mv -f zhc2cmn.sort zhc2cmn.dic ; ./msgchi.py -T -l zhc2cmn test-cmn.pot
#	LANG=C ./lensort-dic zht2cmn.dic > zht2cmn.sort ; mv -f zht2cmn.sort zht2cmn.dic ; ./msgchi.py -T -l zht2cmn test-cmn.pot
#	LANG=C ./lensort-dic cmn2yue.dic > cmn2yue.sort ; mv -f cmn2yue.sort cmn2yue.dic ; ./msgchi.py -T -l cmn2yue test-cmn.pot
#	LANG=C ./lensort-dic cmn2nan.dic > cmn2nan.sort ; mv -f cmn2nan.sort cmn2nan.dic ; ./msgchi.py -T -l cmn2nan test-cmn.pot

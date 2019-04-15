VERSION = 1.3
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


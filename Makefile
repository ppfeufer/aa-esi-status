appname = aa-esi-status
package = esistatus

help:
	@echo "Makefile for $(appname)"

translationfiles:
	cd $(package) && \
	django-admin makemessages \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l ru \
		-l zh_Hans \
		--keep-pot \
		--ignore 'build/*'

compiletranslationfiles:
	cd $(package) && \
	django-admin compilemessages \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l ru \
		-l zh_Hans

coverage:
	rm -rfv htmlcov && \
	coverage run ../myauth/manage.py test $(package) --keepdb --failfast && coverage html && coverage report

build_test:
	rm -rfv dist && \
	python3 -m build

tox_tests:
	export USE_MYSQL=False && \
	tox

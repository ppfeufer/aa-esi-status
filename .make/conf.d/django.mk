# Make targets for Django projects

# Translation files
.PHONY: translations
translations:
	@echo "Creating or updating translation files"
	@django-admin makemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans \
		--keep-pot \
		--ignore 'build/*'
	@current_app_version=$$(pip show $(appname) | grep 'Version: ' | awk '{print $$NF}'); \
	sed -i "/\"Project-Id-Version: /c\\\"Project-Id-Version: $(appname_verbose) $$current_app_version\\\n\"" $(translation_template); \
	sed -i "/\"Report-Msgid-Bugs-To: /c\\\"Report-Msgid-Bugs-To: $(git_repository_issues)\\\n\"" $(translation_template); \
	subdircount=$$(find $(translation_directory) -mindepth 1 -maxdepth 1 -type d | wc -l); \
	if [[ $$subdircount -gt 1 ]]; then \
		for path in $(translation_directory)/*/; do \
			[ -d "$$path/LC_MESSAGES" ] || continue; \
			if [[ -f "$$path/LC_MESSAGES/django.po" ]] \
				then \
					sed -i "/\"Project-Id-Version: /c\\\"Project-Id-Version: $(appname_verbose) $$current_app_version\\\n\"" $$path/LC_MESSAGES/django.po; \
					sed -i "/\"Report-Msgid-Bugs-To: /c\\\"Report-Msgid-Bugs-To: $(git_repository_issues)\\\n\"" $$path/LC_MESSAGES/django.po; \
			fi; \
		done; \
	fi;

# Compile translation files
.PHONY: compile_translations
compile_translations:
	@echo "Compiling translation files"
	@django-admin compilemessages \
		-l cs_CZ \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l nl_NL \
		-l pl_PL \
		-l ru \
		-l sk \
		-l uk \
		-l zh_Hans

# Migrate all database changes
.PHONY: migrate
migrate:
	@echo "Migrating the database"
	@python ../myauth/manage.py migrate $(package)

# Make migrations for the app
.PHONY: migrations
migrations:
	@echo "Creating or updating migrations"
	@python ../myauth/manage.py makemigrations $(package)

# Help message
.PHONY: help
help::
	@echo "  $(TEXT_UNDERLINE)Django:$(TEXT_UNDERLINE_END)"
	@echo "    migrate                   Migrate all database changes"
	@echo "    migrations                Create or update migrations"
	@echo "    translations              Create or update translation files"
	@echo "    compile_translations      Compile translation files"
	@echo ""

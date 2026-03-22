SV_NOTES_DIR := domains/b737/anki/notes/systems_verification
SV_BUILD_DIR := build

SV_SYSTEMS := \
	general \
	adverse \
	flight_warning \
	gpws \
	air_conditioning \
	pressurization \
	autoflight \
	communications \
	acars \
	electrical \
	emergency_equipment \
	fire_protection \
	flight_controls \
	fuel \
	hydraulics \
	ice_and_rain_protection \
	flight_instrumentation \
	hud \
	landing_gear \
	lighting \
	navigation \
	fms \
	weather_radar \
	atc_tcas_trans \
	oxygen \
	pneumatics \
	apu \
	engines \
	performance

SV_TSVS := $(foreach s,$(SV_SYSTEMS),$(SV_BUILD_DIR)/sv-$(s).tsv)

.PHONY: sv sv-check sv-import $(addprefix sv-,$(SV_SYSTEMS))
sv:
	mkdir -p $(SV_BUILD_DIR)
	python tools/anki/cnsf_canonicalize.py --write $(SV_NOTES_DIR)/*/*.md
	$(MAKE) $(SV_TSVS)
	for f in $(SV_TSVS); do \
		if [ -f "$$f" ]; then \
			python tools/anki/export/sv_import_to_anki.py "$$f"; \
		fi; \
	done

sv-check:
	python tools/anki/cnsf_canonicalize.py --check $(SV_NOTES_DIR)/*/*.md

sv-import:
	for f in $(SV_TSVS); do \
		if [ -f "$$f" ]; then \
			python tools/anki/export/sv_import_to_anki.py "$$f"; \
		fi; \
	done

$(SV_BUILD_DIR)/sv-%.tsv:
	mkdir -p $(SV_BUILD_DIR)
	if [ -d "$(SV_NOTES_DIR)/$*" ]; then \
		python tools/anki/export/sv_md_to_tsv.py --in $(SV_NOTES_DIR)/$* --out $@; \
	fi

sv-init:
	mkdir -p domains/b737/anki/notes/systems_verification/{\
general,\
adverse,\
flight_warning,\
gpws,\
air_conditioning,\
pressurization,\
autoflight,\
communications,\
acars,\
electrical,\
emergency_equipment,\
fire_protection,\
flight_controls,\
fuel,\
hydraulics,\
ice_and_rain_protection,\
flight_instrumentation,\
hud,\
landing_gear,\
lighting,\
navigation,\
fms,\
weather_radar,\
atc_tcas_trans,\
oxygen,\
pneumatics,\
apu,\
engines,\
performance\
}

sv-%:
	mkdir -p $(SV_BUILD_DIR)
	python tools/anki/cnsf_canonicalize.py --write $(SV_NOTES_DIR)/$*/*.md
	python tools/anki/export/sv_md_to_tsv.py --in $(SV_NOTES_DIR)/$* --out $(SV_BUILD_DIR)/sv-$*.tsv
	python tools/anki/export/sv_import_to_anki.py $(SV_BUILD_DIR)/sv-$*.tsv
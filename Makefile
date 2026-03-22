# -------------------------------------------------------------------
# Systems Verification (SV)
# -------------------------------------------------------------------

SV_ROOT := domains/b737/anki/notes/systems_verification
SV_BUILD := build

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

SV_TSV := $(addprefix $(SV_BUILD)/sv-,$(addsuffix .tsv,$(SV_SYSTEMS)))

.PHONY: sv sv-check

sv-check:
	python tools/anki/cnsf_canonicalize.py --check $(SV_ROOT)/*/*.md

sv: sv-check $(SV_TSV)
	for f in $(SV_TSV); do \
		if [ -f "$$f" ]; then \
			python tools/anki/export/sv_import_to_anki.py "$$f"; \
		fi; \
	done

$(SV_BUILD)/sv-%.tsv:
	mkdir -p $(SV_BUILD)
	if [ -d "$(SV_ROOT)/$*" ]; then \
		python tools/anki/export/sv_md_to_tsv.py \
			--in $(SV_ROOT)/$* \
			--out $@; \
	fi
# -------------------------------------------------------------------
# Systems Verification (SV)
# -------------------------------------------------------------------
PYTHON := /Users/craig/miniforge3/envs/craigdev/bin/python
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

.PHONY: sv sv-check sv-fix sv-clean $(addprefix sv-,$(SV_SYSTEMS))

sv-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(SV_ROOT)/*/*.md

sv-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(SV_ROOT)/*/*.md

sv-clean:
	rm -f $(SV_BUILD)/sv-*.tsv

sv: sv-check
	@echo "=== Building Systems Verification decks ==="
	@set -e; \
	mkdir -p $(SV_BUILD); \
	for s in $(SV_SYSTEMS); do \
		if [ -d "$(SV_ROOT)/$$s" ]; then \
			echo "--- $$s ---"; \
			$(PYTHON) tools/anki/export/sv_md_to_tsv.py \
				--in "$(SV_ROOT)/$$s" \
				--out "$(SV_BUILD)/sv-$$s.tsv" && \
			$(PYTHON) tools/anki/export/sv_import_to_anki.py \
				"$(SV_BUILD)/sv-$$s.tsv"; \
		fi; \
	done

sv-%:
	mkdir -p $(SV_BUILD)
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(SV_ROOT)/$*/*.md
	$(PYTHON) tools/anki/export/sv_md_to_tsv.py \
		--in "$(SV_ROOT)/$*" \
		--out "$(SV_BUILD)/sv-$*.tsv"
	$(PYTHON) tools/anki/export/sv_import_to_anki.py \
		"$(SV_BUILD)/sv-$*.tsv"
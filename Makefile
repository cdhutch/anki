# -------------------------------------------------------------------
# Systems Verification (SV)
# -------------------------------------------------------------------
PYTHON := /Users/craig/miniforge3/envs/craigdev/bin/python
BUILD_DIR := build

SV_ROOT := domains/b737/anki/notes/systems_verification
SV_BUILD := $(BUILD_DIR)

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

# -------------------------------------------------------------------
# QRC Recall
# -------------------------------------------------------------------
QRC_ROOT := domains/b737/anki/notes/qrc_recall
QRC_TSV := $(BUILD_DIR)/qrc-recall.tsv

.PHONY: qrc qrc-check qrc-fix qrc-clean

qrc-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(QRC_ROOT)/*.md

qrc-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(QRC_ROOT)/*.md

qrc-clean:
	rm -f $(QRC_TSV)

qrc: qrc-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(QRC_ROOT) \
		--out $(QRC_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki --tsv $(QRC_TSV)

# -------------------------------------------------------------------
# Triggers and Flows
# -------------------------------------------------------------------
TRIGGERS_ROOT := domains/b737/anki/notes/triggers_and_flows
TRIGGERS_TSV := $(BUILD_DIR)/triggers-and-flows.tsv

.PHONY: triggers triggers-check triggers-fix triggers-clean triggers-lint triggers-fmt

triggers-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(TRIGGERS_ROOT)/*.md

triggers-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(TRIGGERS_ROOT)/*.md

triggers-clean:
	rm -f $(TRIGGERS_TSV)

triggers: triggers-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(TRIGGERS_ROOT) \
		--out $(TRIGGERS_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki --tsv $(TRIGGERS_TSV)

triggers-lint:
	$(PYTHON) tools/anki/lint_flows.py

triggers-fmt: triggers-fix triggers-lint

# -------------------------------------------------------------------
# Procedures
# -------------------------------------------------------------------
PROCEDURES_ROOT := domains/b737/anki/notes/procedures
PROCEDURES_NORMAL_ROOT := $(PROCEDURES_ROOT)/normal
PROCEDURES_NORMAL_STRUCTURED_ROOT := $(PROCEDURES_NORMAL_ROOT)/structured
PROCEDURES_NORMAL_CLOZE_ROOT := $(PROCEDURES_NORMAL_ROOT)/cloze
PROCEDURES_BUILD := $(BUILD_DIR)

.PHONY: proc-normal-check proc-normal-fix proc-normal-clean proc-normal
.PHONY: proc-normal-cloze-check proc-normal-cloze-clean proc-normal-cloze

proc-normal-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(PROCEDURES_NORMAL_STRUCTURED_ROOT)/*.md

proc-normal-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(PROCEDURES_NORMAL_STRUCTURED_ROOT)/*.md

proc-normal-clean:
	rm -f $(PROCEDURES_BUILD)/procedures-normal.tsv

proc-normal: proc-normal-check
	mkdir -p $(PROCEDURES_BUILD)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(PROCEDURES_NORMAL_STRUCTURED_ROOT) \
		--out $(PROCEDURES_BUILD)/procedures-normal.tsv \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki \
		--tsv $(PROCEDURES_BUILD)/procedures-normal.tsv

proc-normal-cloze-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(PROCEDURES_NORMAL_CLOZE_ROOT)/*.md

proc-normal-cloze-clean:
	rm -f $(PROCEDURES_BUILD)/procedures-normal-cloze.tsv

proc-normal-cloze:
	mkdir -p $(PROCEDURES_BUILD)
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(PROCEDURES_NORMAL_CLOZE_ROOT)/*.md
	$(PYTHON) tools/anki/export/cloze_md_to_tsv.py \
		--in $(PROCEDURES_NORMAL_CLOZE_ROOT) \
		--out $(PROCEDURES_BUILD)/procedures-normal-cloze.tsv
	$(PYTHON) tools/anki/export/cloze_import_to_anki.py \
		$(PROCEDURES_BUILD)/procedures-normal-cloze.tsv


# -------------------------------------------------------------------
# Limits
# -------------------------------------------------------------------
LIMITS_ROOT := domains/b737/anki/notes/limits
LIMITS_TSV := $(BUILD_DIR)/limits.tsv

.PHONY: limits-check limits-fix limits-clean limits

limits-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(LIMITS_ROOT)/*/*.md

limits-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(LIMITS_ROOT)/*/*.md

limits-clean:
	rm -f $(LIMITS_TSV)

limits: limits-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(LIMITS_ROOT) \
		--out $(LIMITS_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki \
		--tsv $(LIMITS_TSV)
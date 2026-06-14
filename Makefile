# -------------------------------------------------------------------
# Help
# -------------------------------------------------------------------
.PHONY: help

help:
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Git"
	@echo "  git-unlock          Remove stale git lock files"
	@echo ""
	@echo "Systems Verification (SV) — cloze pipeline"
	@echo "  sv                  Canonicalize, export TSV, and sync all SV systems to Anki"
	@echo "  sv-check            Check CNSF formatting for all SV notes (no changes)"
	@echo "  sv-fix              Canonicalize CNSF formatting for all SV notes"
	@echo "  sv-clean            Remove generated SV TSV files"
	@echo "  sv-<system>         Canonicalize, export, and sync a single SV system"
	@echo ""
	@echo "Systems Verification Exam (SVE) — MCQ/T/F pipeline"
	@echo "  sve                 Canonicalize, export TSV, and sync all SVE systems to Anki"
	@echo "  sve-check           Check CNSF formatting for all SVE notes (no changes)"
	@echo "  sve-fix             Canonicalize CNSF formatting for all SVE notes"
	@echo "  sve-clean           Remove generated SVE TSV files"
	@echo "  sve-<system>        Canonicalize, export, and sync a single SVE system"
	@echo "  Note: sync preserves manual suspension on existing cards."
	@echo "        New cards: suspended if status:draft, active if status:verified."
	@echo "        Existing cards: unsuspended only on draft→verified transition."
	@echo ""
	@echo "QRC Recall"
	@echo "  qrc                 Export and sync QRC Recall notes to Anki"
	@echo "  qrc-check           Check CNSF formatting for QRC notes (no changes)"
	@echo "  qrc-fix             Canonicalize CNSF formatting for QRC notes"
	@echo "  qrc-clean           Remove generated QRC TSV file"
	@echo ""
	@echo "Triggers and Flows"
	@echo "  triggers            Export and sync Triggers and Flows notes to Anki"
	@echo "  triggers-check      Check CNSF formatting for Triggers/Flows notes (no changes)"
	@echo "  triggers-fix        Canonicalize CNSF formatting for Triggers/Flows notes"
	@echo "  triggers-clean      Remove generated Triggers/Flows TSV file"
	@echo "  triggers-lint       Lint flow notes for structural issues"
	@echo "  triggers-fmt        Canonicalize and lint Triggers/Flows notes"
	@echo ""
	@echo "Procedures"
	@echo "  proc-normal         Export and sync normal procedures (structured) to Anki"
	@echo "  proc-normal-check   Check CNSF formatting for normal procedure notes"
	@echo "  proc-normal-fix     Canonicalize normal procedure notes"
	@echo "  proc-normal-clean   Remove generated normal procedures TSV"
	@echo "  proc-normal-cloze   Export and sync normal procedures (cloze) to Anki"
	@echo "  proc-non-normal     Export and sync non-normal procedures (structured) to Anki"
	@echo "  proc-non-normal-check  Check CNSF formatting for non-normal procedure notes"
	@echo "  proc-non-normal-fix    Canonicalize non-normal procedure notes"
	@echo "  proc-non-normal-clean  Remove generated non-normal procedures TSV"
	@echo "  proc-non-normal-cloze  Export and sync non-normal procedures (cloze) to Anki"
	@echo "  proc-inflight       Export and sync inflight maneuver procedures to Anki"
	@echo "  proc-inflight-check Check CNSF formatting for inflight maneuver notes"
	@echo "  proc-inflight-fix   Canonicalize inflight maneuver notes"
	@echo "  proc-inflight-clean Remove generated inflight maneuvers TSV"
	@echo ""
	@echo "Limits"
	@echo "  limits              Export and sync Limits notes to Anki"
	@echo "  limits-check        Check CNSF formatting for Limits notes (no changes)"
	@echo "  limits-fix          Canonicalize CNSF formatting for Limits notes"
	@echo "  limits-clean        Remove generated Limits TSV file"
	@echo ""
	@echo "Cats and Dogs"
	@echo "  cats                Export and sync Cats and Dogs notes to Anki"
	@echo "  cats-check          Check CNSF formatting for Cats and Dogs notes (no changes)"
	@echo "  cats-fix            Canonicalize CNSF formatting for Cats and Dogs notes"
	@echo "  cats-clean          Remove generated Cats and Dogs TSV file"
	@echo ""
	@echo "Mnemonics"
	@echo "  mnemonic            Export and sync Mnemonic notes to Anki"
	@echo "  mnemonic-check      Check CNSF formatting for Mnemonic notes (no changes)"
	@echo "  mnemonic-fix        Canonicalize CNSF formatting for Mnemonic notes"
	@echo "  mnemonic-clean      Remove generated Mnemonics TSV file"
	@echo ""
	@echo "Checklists"
	@echo "  checklists          Export and sync Checklist notes to Anki"
	@echo "  checklists-check    Check CNSF formatting for Checklist notes (no changes)"
	@echo "  checklists-fix      Canonicalize CNSF formatting for Checklist notes"
	@echo "  checklists-clean    Remove generated Checklists TSV file"
	@echo ""
	@echo "Ukrainian Lexeme (UA)"
	@echo "  ua-lexeme           Canonicalize and sync all UA lexeme notes to Anki"
	@echo "  ua-lexeme-check     Check CNSF formatting for UA lexeme notes (no changes)"
	@echo "  ua-lexeme-fix       Canonicalize CNSF formatting for UA lexeme notes"
	@echo "  ua-lexeme-<batch>   Canonicalize and sync a single batch (e.g. yabluko-l1/vstup)"
	@echo ""
	@echo "Core (aggregate)"
	@echo "  core                Export and sync all B737::Core decks to Anki"
	@echo "  core-fix            Canonicalize all B737::Core note files"
	@echo ""

# -------------------------------------------------------------------
# Git Utilities
# -------------------------------------------------------------------
.PHONY: git-unlock

git-unlock:
	@echo "Removing stale git lock files..."
	@find .git -name "*.lock" -type f -print -delete
	@echo "Done."

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
# Covers all three sub-decks in one pass (deck routing via frontmatter):
#   B737::Core::Triggers_and_Flows::Triggers
#   B737::Core::Triggers_and_Flows::Flows
#   B737::Core::Triggers_and_Flows::Supplemental  ← mnemonics, sequences, phase-recalls
# Note: Procedures notes live in domains/b737/anki/notes/procedures/ and
#       are synced via proc-normal, proc-non-normal, proc-inflight targets.
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
# Cats and Dogs
# -------------------------------------------------------------------

CATS_ROOT := domains/b737/anki/notes/cats_and_dogs
CATS_TSV  := $(BUILD_DIR)/cats-and-dogs.tsv

.PHONY: cats cats-check cats-fix cats-clean

cats-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(CATS_ROOT)/*.md

cats-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(CATS_ROOT)/*.md

cats-clean:
	rm -f $(CATS_TSV)

cats: cats-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(CATS_ROOT) \
		--out $(CATS_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki --tsv $(CATS_TSV)

# -------------------------------------------------------------------
# Mnemonics
# -------------------------------------------------------------------
MNEMONIC_ROOT := domains/b737/anki/notes/mnemonics
MNEMONIC_TSV  := $(BUILD_DIR)/mnemonics.tsv

.PHONY: mnemonic mnemonic-check mnemonic-fix mnemonic-clean

mnemonic-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(MNEMONIC_ROOT)/*.md

mnemonic-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(MNEMONIC_ROOT)/*.md

mnemonic-clean:
	rm -f $(MNEMONIC_TSV)

mnemonic: mnemonic-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(MNEMONIC_ROOT) \
		--out $(MNEMONIC_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki --tsv $(MNEMONIC_TSV)

# -------------------------------------------------------------------
# Checklists
# -------------------------------------------------------------------

CHECKLISTS_ROOT := domains/b737/anki/notes/checklists
CHECKLISTS_TSV  := $(BUILD_DIR)/checklists.tsv

.PHONY: checklists checklists-check checklists-fix checklists-clean

checklists-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(shell find $(CHECKLISTS_ROOT) -name "*.md" ! -name "_*")

checklists-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(shell find $(CHECKLISTS_ROOT) -name "*.md" ! -name "_*")

checklists-clean:
	rm -f $(CHECKLISTS_TSV)

checklists: checklists-check
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(CHECKLISTS_ROOT) \
		--out $(CHECKLISTS_TSV) \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki --tsv $(CHECKLISTS_TSV)

# -------------------------------------------------------------------
# Procedures
# -------------------------------------------------------------------
PROCEDURES_ROOT := domains/b737/anki/notes/procedures

PROCEDURES_NORMAL_ROOT := $(PROCEDURES_ROOT)/normal
PROCEDURES_NORMAL_STRUCTURED_ROOT := $(PROCEDURES_NORMAL_ROOT)/structured
PROCEDURES_NORMAL_CLOZE_ROOT := $(PROCEDURES_NORMAL_ROOT)/cloze

PROCEDURES_NON_NORMAL_ROOT := $(PROCEDURES_ROOT)/non_normal
PROCEDURES_NON_NORMAL_STRUCTURED_ROOT := $(PROCEDURES_NON_NORMAL_ROOT)/structured
PROCEDURES_NON_NORMAL_CLOZE_ROOT := $(PROCEDURES_NON_NORMAL_ROOT)/cloze

PROCEDURES_BUILD := $(BUILD_DIR)

.PHONY: proc-normal-check proc-normal-fix proc-normal-clean proc-normal
.PHONY: proc-normal-cloze-check proc-normal-cloze-clean proc-normal-cloze
.PHONY: proc-non-normal-check proc-non-normal-fix proc-non-normal-clean proc-non-normal
.PHONY: proc-non-normal-cloze-check proc-non-normal-cloze-clean proc-non-normal-cloze

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

proc-non-normal-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(PROCEDURES_NON_NORMAL_STRUCTURED_ROOT)/*.md

proc-non-normal-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(PROCEDURES_NON_NORMAL_STRUCTURED_ROOT)/*.md

proc-non-normal-clean:
	rm -f $(PROCEDURES_BUILD)/procedures-non-normal.tsv

proc-non-normal: proc-non-normal-check
	mkdir -p $(PROCEDURES_BUILD)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(PROCEDURES_NON_NORMAL_STRUCTURED_ROOT) \
		--out $(PROCEDURES_BUILD)/procedures-non-normal.tsv \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki \
		--tsv $(PROCEDURES_BUILD)/procedures-non-normal.tsv

proc-non-normal-cloze-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(PROCEDURES_NON_NORMAL_CLOZE_ROOT)/*.md

proc-non-normal-cloze-clean:
	rm -f $(PROCEDURES_BUILD)/procedures-non-normal-cloze.tsv

proc-non-normal-cloze:
	mkdir -p $(PROCEDURES_BUILD)
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(PROCEDURES_NON_NORMAL_CLOZE_ROOT)/*.md
	$(PYTHON) tools/anki/export/cloze_md_to_tsv.py \
		--in $(PROCEDURES_NON_NORMAL_CLOZE_ROOT) \
		--out $(PROCEDURES_BUILD)/procedures-non-normal-cloze.tsv
	$(PYTHON) tools/anki/export/cloze_import_to_anki.py \
		$(PROCEDURES_BUILD)/procedures-non-normal-cloze.tsv

PROCEDURES_INFLIGHT_ROOT := $(PROCEDURES_ROOT)/inflight_maneuvers

.PHONY: proc-inflight-check proc-inflight-fix proc-inflight-clean proc-inflight

proc-inflight-check:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --check $(PROCEDURES_INFLIGHT_ROOT)/*.md

proc-inflight-fix:
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(PROCEDURES_INFLIGHT_ROOT)/*.md

proc-inflight-clean:
	rm -f $(PROCEDURES_BUILD)/procedures-inflight-maneuvers.tsv

proc-inflight: proc-inflight-check
	mkdir -p $(PROCEDURES_BUILD)
	$(PYTHON) -m tools.anki.export.cnsf_to_import_tsv \
		--in $(PROCEDURES_INFLIGHT_ROOT) \
		--out $(PROCEDURES_BUILD)/procedures-inflight-maneuvers.tsv \
		--overwrite
	$(PYTHON) -m tools.anki.sync.tsv_to_anki \
		--tsv $(PROCEDURES_BUILD)/procedures-inflight-maneuvers.tsv


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

# -------------------------------------------------------------------
# Systems Verification Exam (SVE) — exam-mode MCQ / T/F pipeline
#
# Reuses SV_ROOT, SV_BUILD, and SV_SYSTEMS from the SV section above.
# sve-check and sve-fix delegate to sv-check / sv-fix (same files, same
# canonicalizer) so there is no duplication.
# -------------------------------------------------------------------
.PHONY: sve sve-check sve-fix sve-clean

sve-check: sv-check

sve-fix: sv-fix

sve-clean:
	rm -f $(SV_BUILD)/sve-*.tsv

sve: sve-check
	@echo "=== Building Systems Verification Exam decks ==="
	@set -e; \
	mkdir -p $(SV_BUILD); \
	for s in $(SV_SYSTEMS); do \
		if [ -d "$(SV_ROOT)/$$s" ]; then \
			echo "--- $$s ---"; \
			$(PYTHON) tools/anki/export/sv_exam_md_to_tsv.py \
				--in "$(SV_ROOT)/$$s" \
				--out-mcq "$(SV_BUILD)/sve-mcq-$$s.tsv" \
				--out-tf "$(SV_BUILD)/sve-tf-$$s.tsv" && \
			$(PYTHON) tools/anki/sync/sv_exam_import_to_anki.py \
				--mcq "$(SV_BUILD)/sve-mcq-$$s.tsv" \
				--tf "$(SV_BUILD)/sve-tf-$$s.tsv"; \
		fi; \
	done

# -------------------------------------------------------------------
# Core (aggregate — all B737::Core decks)
# -------------------------------------------------------------------
.PHONY: core core-fix

core-fix:
	$(MAKE) limits-fix
	$(MAKE) qrc-fix
	$(MAKE) triggers-fix
	$(MAKE) cats-fix
	$(MAKE) mnemonic-fix
	$(MAKE) checklists-fix
	$(MAKE) proc-normal-fix
	$(MAKE) proc-non-normal-fix
	$(MAKE) proc-inflight-fix

core:
	@TARGETS="limits qrc triggers cats mnemonic checklists proc-normal proc-normal-cloze proc-non-normal proc-inflight"; \
	for t in $$TARGETS; do \
		printf "\033[1;34m→ $$t...\033[0m\n"; \
		$(MAKE) $$t || { printf "\033[1;31m✗  Core sync failed at: $$t\033[0m\n"; exit 1; }; \
		printf "\033[0;32m✓  $$t\033[0m\n"; \
	done; \
	printf "\n\033[1;32m✓  All B737::Core decks synced successfully.\033[0m\n"

sve-%:
	mkdir -p $(SV_BUILD)
	$(PYTHON) tools/anki/cnsf_canonicalize.py --write $(SV_ROOT)/$*/*.md
	$(PYTHON) tools/anki/export/sv_exam_md_to_tsv.py \
		--in "$(SV_ROOT)/$*" \
		--out-mcq "$(SV_BUILD)/sve-mcq-$*.tsv" \
		--out-tf "$(SV_BUILD)/sve-tf-$*.tsv"
	$(PYTHON) tools/anki/sync/sv_exam_import_to_anki.py \
		--mcq "$(SV_BUILD)/sve-mcq-$*.tsv" \
		--tf "$(SV_BUILD)/sve-tf-$*.tsv"

# -------------------------------------------------------------------
# Ukrainian Lexeme (UA)
# -------------------------------------------------------------------
UA_LEXEME_ROOT := domains/ua/anki/notes/lexemes

.PHONY: ua-lexeme ua-lexeme-check ua-lexeme-fix

ua-lexeme-check:
	find $(UA_LEXEME_ROOT) -name "ua-lexeme-*.md" | xargs $(PYTHON) tools/anki/cnsf_canonicalize.py --check

ua-lexeme-fix:
	find $(UA_LEXEME_ROOT) -name "ua-lexeme-*.md" | xargs $(PYTHON) tools/anki/cnsf_canonicalize.py --write

ua-lexeme: ua-lexeme-fix
	$(PYTHON) tools/anki/sync/ua_lexeme_import.py $(UA_LEXEME_ROOT)/

ua-lexeme-%: ua-lexeme-fix
	$(PYTHON) tools/anki/sync/ua_lexeme_import.py $(UA_LEXEME_ROOT)/$*/
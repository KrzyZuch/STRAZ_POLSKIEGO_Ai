import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    REPO_ROOT
    / "PROJEKTY"
    / "13_baza_czesci_recykling"
    / "scripts"
    / "curate_candidates.py"
)
REPORTS_DIR = (
    REPO_ROOT
    / "PROJEKTY"
    / "13_baza_czesci_recykling"
    / "autonomous_test"
    / "reports"
)


def _load_curate_module():
    spec = importlib.util.spec_from_file_location("curate_candidates", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class TestSlugify(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_simple(self) -> None:
        self.assertEqual(self.mod.slugify("Hello World"), "hello-world")

    def test_special_chars(self) -> None:
        self.assertEqual(self.mod.slugify("A/B:C&D"), "a-b-c-d")

    def test_polish_chars(self) -> None:
        self.assertEqual(self.mod.slugify("Płyta główna"), "p-yta-g-wna")

    def test_multiple_dashes(self) -> None:
        self.assertEqual(self.mod.slugify("a---b"), "a-b")

    def test_leading_trailing_dashes(self) -> None:
        self.assertEqual(self.mod.slugify("--hello--"), "hello")

    def test_uppercase(self) -> None:
        self.assertEqual(self.mod.slugify("ABC"), "abc")

    def test_digits(self) -> None:
        self.assertEqual(self.mod.slugify("Part 123"), "part-123")

    def test_empty(self) -> None:
        self.assertEqual(self.mod.slugify(""), "")

    def test_spaces_only(self) -> None:
        self.assertEqual(self.mod.slugify("   "), "")


class TestNormalizePartNumber(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_dashes_removed(self) -> None:
        self.assertEqual(self.mod.normalize_part_number("BCM2837B0-1FSBG"), "bcm2837b01fsbg")

    def test_spaces_removed(self) -> None:
        self.assertEqual(self.mod.normalize_part_number("BD82HM55 SLGZR"), "bd82hm55slgzr")

    def test_lowercase(self) -> None:
        self.assertEqual(self.mod.normalize_part_number("TPS65994"), "tps65994")

    def test_mixed(self) -> None:
        self.assertEqual(self.mod.normalize_part_number("IT8628E-REV.C"), "it8628erevc")

    def test_already_normalized(self) -> None:
        self.assertEqual(self.mod.normalize_part_number("abc123"), "abc123")


class TestInferSpecies(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_capacitor(self) -> None:
        self.assertEqual(self.mod.infer_species("Electrolytic Capacitor", ""), "Capacitor")

    def test_resistor(self) -> None:
        self.assertEqual(self.mod.infer_species("SMD Resistor", ""), "Resistor")

    def test_mcu(self) -> None:
        self.assertEqual(self.mod.infer_species("MCU STM32", ""), "IC")

    def test_mosfet(self) -> None:
        self.assertEqual(self.mod.infer_species("N-Channel MOSFET", ""), "Transistor")

    def test_diode_led(self) -> None:
        self.assertEqual(self.mod.infer_species("LED Diode", ""), "Diode")

    def test_led_driver_is_ic(self) -> None:
        self.assertEqual(self.mod.infer_species("LED Driver", ""), "IC")

    def test_crystal(self) -> None:
        self.assertEqual(self.mod.infer_species("Crystal Oscillator 16MHz", ""), "Crystal")

    def test_connector(self) -> None:
        self.assertEqual(self.mod.infer_species("USB Connector", ""), "Connector")

    def test_fuse(self) -> None:
        self.assertEqual(self.mod.infer_species("PTC Resettable Fuse", ""), "Fuse")

    def test_switch(self) -> None:
        self.assertEqual(self.mod.infer_species("Tactile Switch", ""), "Switch")

    def test_relay(self) -> None:
        self.assertEqual(self.mod.infer_species("5V Relay Module", ""), "Relay")

    def test_sensor(self) -> None:
        self.assertEqual(self.mod.infer_species("Accelerometer Sensor", ""), "Sensor")

    def test_emi_filter(self) -> None:
        self.assertEqual(self.mod.infer_species("Ferrite Bead EMI", ""), "EMI_Filter")

    def test_pcb(self) -> None:
        self.assertEqual(self.mod.infer_species("PCB Board Module", ""), "PCB")

    def test_battery(self) -> None:
        self.assertEqual(self.mod.infer_species("Battery Cell", ""), "Battery")

    def test_unknown(self) -> None:
        self.assertEqual(self.mod.infer_species("Mystery Component", ""), "Unknown")

    def test_empty_name(self) -> None:
        self.assertEqual(self.mod.infer_species("", ""), "Unknown")

    def test_none_name(self) -> None:
        self.assertEqual(self.mod.infer_species(None, ""), "Unknown")


class TestInferGenus(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_ic_power(self) -> None:
        self.assertEqual(self.mod.infer_genus("IC"), "Power")

    def test_resistor_passive(self) -> None:
        self.assertEqual(self.mod.infer_genus("Resistor"), "Passive")

    def test_capacitor_passive(self) -> None:
        self.assertEqual(self.mod.infer_genus("Capacitor"), "Passive")

    def test_diode_semiconductor(self) -> None:
        self.assertEqual(self.mod.infer_genus("Diode"), "Semiconductor")

    def test_transistor_semiconductor(self) -> None:
        self.assertEqual(self.mod.infer_genus("Transistor"), "Semiconductor")

    def test_connector_electromechanical(self) -> None:
        self.assertEqual(self.mod.infer_genus("Connector"), "Electromechanical")

    def test_fuse_protection(self) -> None:
        self.assertEqual(self.mod.infer_genus("Fuse"), "Protection")

    def test_unknown(self) -> None:
        self.assertEqual(self.mod.infer_genus("Unknown"), "Unknown")

    def test_invalid_species(self) -> None:
        self.assertEqual(self.mod.infer_genus("NonExistentSpecies"), "Unknown")


class TestInferMounting(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_smd_name(self) -> None:
        self.assertEqual(self.mod.infer_mounting("SMD Capacitor", ""), "SMD")

    def test_qfn_package(self) -> None:
        self.assertEqual(self.mod.infer_mounting("QFN-48 IC", ""), "SMD")

    def test_soic_package(self) -> None:
        self.assertEqual(self.mod.infer_mounting("SOIC-8 Driver", ""), "SMD")

    def test_0805_size(self) -> None:
        self.assertEqual(self.mod.infer_mounting("0805 Resistor", ""), "SMD")

    def test_sot23_in_part_number(self) -> None:
        self.assertEqual(self.mod.infer_mounting("", "SOT-23 Transistor"), "SMD")

    def test_tht_name(self) -> None:
        self.assertEqual(self.mod.infer_mounting("Through-Hole Resistor", ""), "THT")

    def test_dip_package(self) -> None:
        self.assertEqual(self.mod.infer_mounting("DIP-8 IC", ""), "THT")

    def test_to220(self) -> None:
        self.assertEqual(self.mod.infer_mounting("TO-220 Voltage Regulator", ""), "THT")

    def test_unknown(self) -> None:
        self.assertEqual(self.mod.infer_mounting("Generic Part", "XYZ123"), "unknown")

    def test_both_name_and_number(self) -> None:
        self.assertEqual(self.mod.infer_mounting("SMD Component", "0603"), "SMD")

    def test_empty_both(self) -> None:
        self.assertEqual(self.mod.infer_mounting("", ""), "unknown")


class TestInferDeviceCategory(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_laptop(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Lenovo Laptop"), "laptop")

    def test_notebook(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Dell Notebook"), "laptop")

    def test_router(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Wi-Fi Router"), "router")

    def test_development_board(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Raspberry Pi development board"), "development_board")

    def test_monitor(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Samsung Monitor"), "monitor")

    def test_phone(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Samsung Phone"), "phone")

    def test_printer(self) -> None:
        self.assertEqual(self.mod.infer_device_category("HP Printer"), "printer")

    def test_industrial_pc(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Industrial Panel PC"), "industrial_pc")

    def test_precision_dell(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Dell Precision M4800"), "laptop")

    def test_unknown(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Some Random Device"), "unknown")

    def test_none(self) -> None:
        self.assertEqual(self.mod.infer_device_category(None), "unknown")

    def test_set_top_box(self) -> None:
        self.assertEqual(self.mod.infer_device_category("Set Top Box"), "set_top_box")


class TestLooksLikeValidMPN(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_valid_alphanumeric(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("BCM2837B0")
        self.assertTrue(valid)
        self.assertIsNone(reason)

    def test_empty_string(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("")
        self.assertFalse(valid)
        self.assertEqual(reason, "empty_field")

    def test_none(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn(None)
        self.assertFalse(valid)
        self.assertEqual(reason, "empty_field")

    def test_whitespace_only(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("   ")
        self.assertFalse(valid)
        self.assertEqual(reason, "empty_field")

    def test_designator_list(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("R29, C13")
        self.assertFalse(valid)
        self.assertEqual(reason, "looks_like_designator_list")

    def test_brak(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("BRAK")
        self.assertFalse(valid)
        self.assertEqual(reason, "empty_verification")

    def test_plain_text_phrase(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("WARSZTAT AUTOMATYKI")
        self.assertFalse(valid)
        self.assertEqual(reason, "looks_like_plain_text_phrase")

    def test_capacitance_value(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("1500µF")
        self.assertFalse(valid)
        self.assertEqual(reason, "looks_like_value_not_mpn")

    def test_resistance_value(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("10KΩ")
        self.assertFalse(valid)
        self.assertEqual(reason, "looks_like_value_not_mpn")

    def test_too_short(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("X")
        self.assertFalse(valid)
        self.assertEqual(reason, "too_short")

    def test_no_alphanumeric(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("---")
        self.assertFalse(valid)
        self.assertEqual(reason, "no_alphanumeric")

    def test_mpn_with_dash(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("M425R1GB4BB0-CWM0D")
        self.assertTrue(valid)

    def test_mpn_with_space(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("BD82HM55 SLGZR")
        self.assertTrue(valid)

    def test_short_but_valid(self) -> None:
        valid, reason = self.mod.looks_like_valid_mpn("AB")
        self.assertTrue(valid)


class TestAssignBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_lenovo_batch_a(self) -> None:
        self.assertEqual(self.mod.assign_batch("Lenovo Laptop"), "A")

    def test_asus_batch_a(self) -> None:
        self.assertEqual(self.mod.assign_batch("ASUS K52F"), "A")

    def test_compal_batch_a(self) -> None:
        self.assertEqual(self.mod.assign_batch("Compal LA-G021P"), "A")

    def test_samsung_batch_b(self) -> None:
        self.assertEqual(self.mod.assign_batch("Samsung UE50MU6102K"), "B")

    def test_electrolux_batch_b(self) -> None:
        self.assertEqual(self.mod.assign_batch("Electrolux EnergySaver"), "B")

    def test_vintage_batch_b(self) -> None:
        self.assertEqual(self.mod.assign_batch("Various Vintage Electronics"), "B")

    def test_designlight_batch_b(self) -> None:
        self.assertEqual(self.mod.assign_batch("DesignLight LDF-12V16W"), "B")

    def test_gigabyte_batch_b(self) -> None:
        self.assertEqual(self.mod.assign_batch("Gigabyte Graphics Card"), "B")

    def test_ewaste_batch_c(self) -> None:
        self.assertEqual(self.mod.assign_batch("Unknown Electronic Waste"), "C")

    def test_desktop_batch_c(self) -> None:
        self.assertEqual(self.mod.assign_batch("Generic Desktop Motherboard (Socket 939)"), "C")

    def test_unbatched(self) -> None:
        self.assertEqual(self.mod.assign_batch("Some Unknown Device"), "unbatched")


class TestExportGateInvariant(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_gate_packet_exists_and_valid_json(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        self.assertIn("gate_result", packet)
        self.assertIn(packet["gate_result"], ("OPEN", "BLOCKED"))
        self.assertIn("gate_checks", packet)
        self.assertIsInstance(packet["gate_checks"], list)

    def test_gate_checks_have_required_keys(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        for check in packet["gate_checks"]:
            self.assertIn("check", check, f"gate_checks entry missing 'check': {check}")
            self.assertIn("pass", check, f"gate_checks entry missing 'pass': {check}")
            self.assertIn("detail", check, f"gate_checks entry missing 'detail': {check}")

    def test_gate_result_matches_checks(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        all_pass = all(c["pass"] for c in packet["gate_checks"])
        expected = "OPEN" if all_pass else "BLOCKED"
        self.assertEqual(packet["gate_result"], expected,
                         f"gate_result={packet['gate_result']} but checks imply {expected}")

    def test_blocked_implies_blockers_nonempty(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        if packet["gate_result"] == "BLOCKED":
            self.assertGreater(len(packet.get("blockers", [])), 0,
                               "gate_result=BLOCKED but blockers list is empty")

    def test_queue_summary_present(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        qs = packet.get("queue_summary", {})
        self.assertIn("accept", qs)
        self.assertIn("defer", qs)
        self.assertIn("reject", qs)
        self.assertIn("pending_human_approval", qs)

    def test_four_gate_checks_present(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        check_names = {c["check"] for c in packet["gate_checks"]}
        required = {"no_pending_approvals", "no_unresolved_deferrals",
                    "catalog_validation_passes", "human_review_recorded"}
        self.assertEqual(check_names, required,
                         f"Missing gate checks: {required - check_names}")

    def test_pending_approvals_zero_implies_gate_open_on_other_checks(self) -> None:
        packet_path = REPORTS_DIR / "export_gate_packet.json"
        if not packet_path.exists():
            self.skipTest("export_gate_packet.json not yet generated")
        with open(packet_path, "r", encoding="utf-8") as f:
            packet = json.load(f)
        pending_check = next(
            (c for c in packet["gate_checks"] if c["check"] == "no_pending_approvals"), None
        )
        if pending_check and pending_check["pass"]:
            self.assertEqual(packet["gate_result"], "OPEN",
                             "no_pending_approvals=PASS but gate still BLOCKED")


class TestReviewQueueConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_curate_module()

    def test_review_queue_exists_and_parseable(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not queue_path.exists():
            self.skipTest("curation_review_queue.jsonl not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        self.assertGreater(len(entries), 0)

    def test_each_entry_has_required_fields(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not queue_path.exists():
            self.skipTest("curation_review_queue.jsonl not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        required = {"candidate_id", "review_status", "curation_decision", "part_number"}
        for e in entries:
            missing = required - set(e.keys())
            self.assertEqual(missing, set(),
                             f"Entry {e.get('candidate_id', '?')} missing: {missing}")

    def test_review_status_values_valid(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not queue_path.exists():
            self.skipTest("curation_review_queue.jsonl not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        valid_statuses = {"auto_approved", "pending_human_approval", "auto_rejected",
                          "approved", "deferred", "human_rejected", "unknown"}
        for e in entries:
            self.assertIn(e["review_status"], valid_statuses,
                          f"Invalid review_status={e['review_status']} for {e['candidate_id']}")

    def test_curation_decision_values_valid(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not queue_path.exists():
            self.skipTest("curation_review_queue.jsonl not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        valid_decisions = {"accept", "defer", "reject"}
        for e in entries:
            self.assertIn(e["curation_decision"], valid_decisions,
                          f"Invalid curation_decision={e['curation_decision']} for {e['candidate_id']}")

    def test_accept_count_matches_gate_packet(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        gate_path = REPORTS_DIR / "export_gate_packet.json"
        if not queue_path.exists() or not gate_path.exists():
            self.skipTest("review queue or gate packet not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        with open(gate_path, "r", encoding="utf-8") as f:
            gate = json.load(f)
        queue_accept = sum(1 for e in entries if e["curation_decision"] == "accept")
        gate_accept = gate["queue_summary"]["accept"]
        self.assertEqual(queue_accept, gate_accept,
                         f"Review queue accept={queue_accept} != gate packet accept={gate_accept}")

    def test_pending_count_matches_gate_packet(self) -> None:
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        gate_path = REPORTS_DIR / "export_gate_packet.json"
        if not queue_path.exists() or not gate_path.exists():
            self.skipTest("review queue or gate packet not yet generated")
        entries = self.mod.read_jsonl(queue_path)
        with open(gate_path, "r", encoding="utf-8") as f:
            gate = json.load(f)
        queue_pending = sum(1 for e in entries if e["review_status"] == "pending_human_approval")
        gate_pending = gate["queue_summary"]["pending_human_approval"]
        self.assertEqual(queue_pending, gate_pending,
                         f"Review queue pending={queue_pending} != gate packet pending={gate_pending}")

    def test_decisions_file_count_matches_queue(self) -> None:
        decisions_path = REPORTS_DIR / "curation_decisions.jsonl"
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not decisions_path.exists() or not queue_path.exists():
            self.skipTest("decisions or queue not yet generated")
        decisions = self.mod.read_jsonl(decisions_path)
        entries = self.mod.read_jsonl(queue_path)
        self.assertEqual(len(decisions), len(entries),
                         f"curation_decisions.jsonl has {len(decisions)} entries "
                         f"but review queue has {len(entries)}")

    def test_pending_list_matches_queue(self) -> None:
        pending_path = REPORTS_DIR / "pending_human_approval_list.json"
        queue_path = REPORTS_DIR / "curation_review_queue.jsonl"
        if not pending_path.exists() or not queue_path.exists():
            self.skipTest("pending list or queue not yet generated")
        with open(pending_path, "r", encoding="utf-8") as f:
            pending_data = json.load(f)
        entries = self.mod.read_jsonl(queue_path)
        queue_pending_ids = {e["candidate_id"] for e in entries
                             if e["review_status"] == "pending_human_approval"}
        list_pending_ids = {e["candidate_id"] for e in pending_data["pending_entries"]}
        self.assertEqual(queue_pending_ids, list_pending_ids,
                         f"Pending IDs mismatch: queue={queue_pending_ids} vs list={list_pending_ids}")


if __name__ == "__main__":
    unittest.main()

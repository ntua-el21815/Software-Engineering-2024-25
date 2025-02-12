import unittest
import subprocess
import os

CLI_COMMAND = "./se2427"

class TestFunctionalCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Εκτελείται πριν από όλα τα tests"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)

    @classmethod
    def tearDownClass(cls):
        """Εκτελείται μετά από όλα τα tests"""
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)

    def test_end_to_end_passescost(self):
        """Functional Test: Ανάκτηση κόστους διελεύσεων"""
        result = subprocess.run([
            CLI_COMMAND, "passescost", "--stationop", "AM", "--tagop", "EG",
            "--from", "20220101", "--to", "20221231", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("passesCost", result.stdout)

    def test_end_to_end_tollstationpasses(self):
        """Functional Test: Ανάκτηση διελεύσεων σταθμού"""
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "AM01",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("passIndex,passID,timestamp,tagID,tagProvider,passType,passCharge", result.stdout)

    def test_end_to_end_admin_addpasses(self):
        """Functional Test: Προσθήκη διελεύσεων από CSV"""
        test_csv = "sample-passes.csv"
        with open(test_csv, "w") as f:
            f.write("passIndex,passID,timestamp,tagID,tagProvider,passType,passCharge\n")

        result = subprocess.run([
            CLI_COMMAND, "admin", "--addpasses", "--source", test_csv
        ], capture_output=True, text=True)

        os.remove(test_csv)

        self.assertEqual(result.returncode, 0)
        self.assertIn("Passes uploaded successfully!", result.stdout)

if __name__ == "__main__":
    unittest.main()
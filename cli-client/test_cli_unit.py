import unittest
import subprocess
import sys
import os

# Use sys.executable to ensure we use the correct Python interpreter
# Use os.path.join for Windows-compatible paths
CLI_PATH = os.path.join(os.path.dirname(__file__), "se2427.py")
CLI_COMMAND = [sys.executable, CLI_PATH]

class TestCLI(unittest.TestCase):
    
    def run_command(self, args, **kwargs):
        """Helper method to run commands with proper Windows compatibility"""
        return subprocess.run(
            CLI_COMMAND + args,
            capture_output=True,
            text=True,
            shell=True,
            **kwargs
        )

    def login(self):
        """Helper method for login"""
        return self.run_command(["login", "--username", "ADMIN", "--passw", "freepasses4all"])

    def logout(self):
        """Helper method for logout"""
        return self.run_command(["logout"])

    def test_healthcheck(self):
        """Test για το healthcheck (απαιτεί authentication)"""
        self.login()
        result = self.run_command(["healthcheck"])
        self.assertEqual(result.returncode, 0, "Η εντολή healthcheck απέτυχε να εκτελεστεί")
        self.assertIn('"status": "OK"', result.stdout, "Το healthcheck API δεν επέστρεψε το αναμενόμενο αποτέλεσμα")
        self.logout()
        
        
    def test_resetpasses(self):
        """Test για resetpasses"""
        self.login()
        result = self.run_command(["resetpasses"])
        self.assertEqual(result.returncode, 0)
        self.assertIn('"status": "OK"', result.stdout)
        self.logout()
        

    def test_resetstations(self):
        """Test για το resetstations"""
        self.login()
        result = self.run_command(["resetstations"])
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            "Reset stations successful" in result.stdout or '"status": "OK"' in result.stdout
        )
        self.logout()
        

    def test_login_logout(self):
        """Test για login/logout"""

        # 1. Επιτυχημένο login
        result = self.run_command(["login", "--username", "ADMIN", "--passw", "freepasses4all"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Login successful", result.stdout)

        # 2. Logout μετά από επιτυχημένο login
        result = self.run_command(["logout"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Logout successful", result.stdout)
    
        # 3. Δοκιμή επανασύνδεσης μετά από logout
        result = self.run_command(["login", "--username", "ADMIN", "--passw", "freepasses4all"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Login successful", result.stdout)

        # 4. Αποτυχημένο login με λάθος στοιχεία
        result = self.run_command(["login", "--username", "wronguser", "--passw", "wrongpass"])
        self.assertIn("Login failed", result.stdout)

        # 🔒 5. Απόπειρα `admin --addpasses` χωρίς login
        result = self.run_command(["admin", "--addpasses", "--source", "passes-sample.csv"])

        self.assertTrue(
            "No authentication token found" in result.stdout or
            "Please login first" in result.stdout or
            "You must be logged in as ADMIN to access admin commands." in result.stdout
        )
        self.logout()
        

    def test_tollstationpasses_valid(self):
        """Test για σωστό σταθμό και σωστή ημερομηνία"""
        self.login()
        result = self.run_command([
            "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.logout()
        

    def test_tollstationpasses_invalid_station(self):
        """Test για μη έγκυρο σταθμό"""
        self.login()

        result = self.run_command([
            "tollstationpasses", "--station", "INVALID_STATION",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("TollStationID INVALID_STATION not found", result.stdout)
        self.logout()
        

    def test_tollstationpasses_invalid_format(self):
        """Test με μη υποστηριζόμενο format"""
        self.login()
        result = self.run_command([
            "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "xml"
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            "invalid choice" in result.stderr and "xml" in result.stderr
        )
        self.logout()
        

    def test_tollstationpasses_no_passes(self):
        """Test για περίοδο χωρίς διελεύσεις"""
        self.login()
        result = self.run_command([
            "tollstationpasses", "--station", "NAO04",
            "--from", "19000101", "--to", "19001231", "--format", "json"
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn('"nPasses": 0', result.stdout)
        self.logout()
        

    def test_passanalysis_valid(self):
        """Test για passanalysis με έγκυρα δεδομένα"""
        self.login()
        result = self.run_command([
            "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "json"
        ])

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertNotIn("Error", result.stdout)
        self.logout()


    def test_passanalysis_invalid_format(self):
        """Test για passanalysis με μη υποστηριζόμενο format"""
        self.login()
        result = self.run_command([
            "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "xml"
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr and "xml" in result.stderr)
        self.logout()


    def test_passanalysis_no_passes(self):
        """Test για passanalysis με 0 διελεύσεις"""
        self.login()
        result = self.run_command([
            "passanalysis", "--stationop", "NO_OP",
            "--tagop", "NO_TAG", "--from", "20220101", "--to", "20221231", "--format", "csv"
        ])
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "passIndex,passID,stationID,timestamp,tagID,passCharge")
        self.logout()
        

    def test_passescost(self):
        """Test για το passescost"""
        self.login()
        result = self.run_command(["passescost", "--stationop", "AM", "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "csv"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.logout()
        
    
    def test_passescost_no_passes(self):
        """Test για passescost με μηδενικές διελεύσεις"""
        self.login()
        result = self.run_command(["passescost", "--stationop", "XX", "--tagop", "YY", "--from", "20220101", "--to", "20221231", "--format", "csv"])
    
        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertIn(",0,", result.stdout)
        self.logout()
        
    
    def test_passescost_invalid_format(self):
        """Test για passescost με μη υποστηριζόμενο format"""
        self.login()
        result = self.run_command([
            "passescost", "--stationop", "AM", "--tagop", "EG",
            "--from", "20220101", "--to", "20221231", "--format", "xml"
        ])

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr or "invalid format" in result.stdout) 
        self.logout()
        
    
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        self.login()
        result = self.run_command([
            "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ])
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertGreaterEqual(len(lines), 1, "Η έξοδος πρέπει να περιέχει τουλάχιστον το header.")
        self.assertEqual(lines[0], "visitingOpID,nPasses,passesCost", "Το header δεν είναι σωστό.")
        self.logout()
        
        
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        self.login()
        result = self.run_command([
            "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ])
        self.assertEqual(result.returncode, 0)
        self.assertIn("visitingOpID,nPasses,passesCost", result.stdout)
        self.logout()
        
    
    def test_invalid_command(self):
        """Test για μη έγκυρη εντολή"""
        result = self.run_command(["invalidcommand"])
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("Unknown command" in result.stderr or "Unknown command" in result.stdout)

if __name__ == '__main__':
    unittest.main()
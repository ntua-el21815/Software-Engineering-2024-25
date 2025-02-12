import unittest
import subprocess

CLI_COMMAND = "./se2427" 

class TestCLI(unittest.TestCase):

    def test_healthcheck(self):
        """Test για το healthcheck (απαιτεί authentication)"""

        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([CLI_COMMAND, "healthcheck"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Η εντολή healthcheck απέτυχε να εκτελεστεί")
        self.assertIn('"status": "OK"', result.stdout, "Το healthcheck API δεν επέστρεψε το αναμενόμενο αποτέλεσμα")
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
        
    def test_resetpasses(self):
        """Test για resetpasses"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([CLI_COMMAND, "resetpasses"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('"status": "OK"', result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_resetstations(self):
        """Test για το resetstations"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([CLI_COMMAND, "resetstations"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            "Reset stations successful" in result.stdout or '"status": "OK"' in result.stdout
        )
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_login_logout(self):
        """Test για login/logout"""

        # 1. Επιτυχημένο login
        result = subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Login successful", result.stdout)

        # 2. Logout μετά από επιτυχημένο login
        result = subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Logout successful", result.stdout)
    
        # 3. Δοκιμή επανασύνδεσης μετά από logout
        result = subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Login successful", result.stdout)

        # 4. Αποτυχημένο login με λάθος στοιχεία
        result = subprocess.run([CLI_COMMAND, "login", "--username", "wronguser", "--passw", "wrongpass"], capture_output=True, text=True)
        self.assertIn("Login failed", result.stdout)

        # 🔒 5. Απόπειρα `admin --addpasses` χωρίς login
        result = subprocess.run([CLI_COMMAND, "admin", "--addpasses", "--source", "passes-sample.csv"], capture_output=True, text=True)

        self.assertTrue(
            "No authentication token found" in result.stdout or
            "Please login first" in result.stdout or
            "You must be logged in as ADMIN to access admin commands." in result.stdout
        )
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_tollstationpasses_valid(self):
        """Test για σωστό σταθμό και σωστή ημερομηνία"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_tollstationpasses_invalid_station(self):
        """Test για μη έγκυρο σταθμό"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)

        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "INVALID_STATION",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("TollStationID INVALID_STATION not found", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_tollstationpasses_invalid_format(self):
        """Test με μη υποστηριζόμενο format"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            "invalid choice" in result.stderr and "xml" in result.stderr
        )
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_tollstationpasses_no_passes(self):
        """Test για περίοδο χωρίς διελεύσεις"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "19000101", "--to", "19001231", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn('"nPasses": 0', result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_passanalysis_valid(self):
        """Test για passanalysis με έγκυρα δεδομένα"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertNotIn("Error", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)


    def test_passanalysis_invalid_format(self):
        """Test για passanalysis με μη υποστηριζόμενο format"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr and "xml" in result.stderr)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)


    def test_passanalysis_no_passes(self):
        """Test για passanalysis με 0 διελεύσεις"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "NO_OP",
            "--tagop", "NO_TAG", "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "passIndex,passID,stationID,timestamp,tagID,passCharge")
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        

    def test_passescost(self):
        """Test για το passescost"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([CLI_COMMAND, "passescost", "--stationop", "AM", "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "csv"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
    
    def test_passescost_no_passes(self):
        """Test για passescost με μηδενικές διελεύσεις"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([CLI_COMMAND, "passescost", "--stationop", "XX", "--tagop", "YY", "--from", "20220101", "--to", "20221231", "--format", "csv"], capture_output=True, text=True)
    
        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertIn(",0,", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
    
    def test_passescost_invalid_format(self):
        """Test για passescost με μη υποστηριζόμενο format"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "passescost", "--stationop", "AM", "--tagop", "EG",
            "--from", "20220101", "--to", "20221231", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr or "invalid format" in result.stdout) 
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
    
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertGreaterEqual(len(lines), 1, "Η έξοδος πρέπει να περιέχει τουλάχιστον το header.")
        self.assertEqual(lines[0], "visitingOpID,nPasses,passesCost", "Το header δεν είναι σωστό.")
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
        
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        result = subprocess.run([
            CLI_COMMAND, "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("visitingOpID,nPasses,passesCost", result.stdout)
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
    
    def test_invalid_command(self):
        """Test για μη έγκυρη εντολή"""
        result = subprocess.run([CLI_COMMAND, "invalidcommand"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("Unknown command" in result.stderr or "Unknown command" in result.stdout)

if __name__ == '__main__':
    unittest.main()
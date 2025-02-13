import unittest
import subprocess

CLI_COMMAND = "./se2427" 

class TestCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Εκτελείται πριν από όλα τα τεστ."""
        
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)
        
        result = subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        if "Login successful" not in result.stdout:
            raise RuntimeError("🚨 Failed to login as ADMIN before tests!")

        result = subprocess.run([CLI_COMMAND, "admin", "--addpasses", "--source", "passes-sample.csv"], capture_output=True, text=True)
        if "Passes uploaded successfully!" in result.stdout:
            print("Passes data successfully uploaded before tests.")
        else:
            print("⚠️ Warning: Failed to upload passes data. Tests might not work correctly.")
            print(result.stdout)

    @classmethod
    def tearDownClass(cls):
        """Εκτελείται μετά από όλα τα τεστ."""
        print("\nRunning teardown: Logout ADMIN...\n")

        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)

    def test_healthcheck(self):
        """Test για το healthcheck (απαιτεί authentication)"""

        result = subprocess.run([CLI_COMMAND, "healthcheck"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "Η εντολή healthcheck απέτυχε να εκτελεστεί")
        self.assertIn('"status": "OK"', result.stdout, "Το healthcheck API δεν επέστρεψε το αναμενόμενο αποτέλεσμα")
        
        
    def test_resetpasses(self):
        """Test για resetpasses"""
        result = subprocess.run([CLI_COMMAND, "resetpasses"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('"status": "OK"', result.stdout)
        

    def test_resetstations(self):
        """Test για το resetstations"""
        result = subprocess.run([CLI_COMMAND, "resetstations"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(
            "Reset stations successful" in result.stdout or '"status": "OK"' in result.stdout
        )
        

    def test_login_logout(self):
        """Test για login/logout"""
        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)

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

        subprocess.run([CLI_COMMAND, "logout"], capture_output=True, text=True)

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
        result = subprocess.run([CLI_COMMAND, "login", "--username", "ADMIN", "--passw", "freepasses4all"], capture_output=True, text=True)
        

    def test_tollstationpasses_valid(self):
        """Test για σωστό σταθμό και σωστή ημερομηνία"""
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        

    def test_tollstationpasses_invalid_station(self):
        """Test για μη έγκυρο σταθμό"""
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "INVALID_STATION",
            "--from", "20220522", "--to", "20220602", "--format", "json"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("TollStationID INVALID_STATION not found", result.stdout)
        

    def test_tollstationpasses_invalid_format(self):
        """Test με μη υποστηριζόμενο format"""
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "20220522", "--to", "20220602", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(
            "invalid choice" in result.stderr and "xml" in result.stderr
        )
        

    def test_tollstationpasses_no_passes(self):
        """Test για περίοδο χωρίς διελεύσεις"""
        result = subprocess.run([
            CLI_COMMAND, "tollstationpasses", "--station", "NAO04",
            "--from", "19000101", "--to", "19001231", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn('"nPasses": 0', result.stdout)
        

    def test_passanalysis_valid(self):
        """Test για passanalysis με έγκυρα δεδομένα"""
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "json"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertNotIn("Error", result.stdout)


    def test_passanalysis_invalid_format(self):
        """Test για passanalysis με μη υποστηριζόμενο format"""
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr and "xml" in result.stderr)


    def test_passanalysis_no_passes(self):
        """Test για passanalysis με 0 διελεύσεις"""
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "AM",
            "--tagop", "EG", "--from", "19000101", "--to", "19001231", "--format", "csv" 
        ], capture_output=True, text=True)
    
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "passIndex,passID,stationID,timestamp,tagID,passCharge")
        
        
    def test_passanalysis_invalid_stationop(self):
        """Test για passanalysis με μη έγκυρο stationOp"""
        result = subprocess.run([
            CLI_COMMAND, "passanalysis", "--stationop", "INVALID_OP",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0) 
        self.assertIn("stationOpID INVALID_OP does not exist", result.stdout)
        

    def test_passescost(self):
        """Test για το passescost"""
        result = subprocess.run([CLI_COMMAND, "passescost", "--stationop", "AM", "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "csv"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        
    
    def test_passescost_no_passes(self):
        """Test για passescost με μηδενικές διελεύσεις"""
        result = subprocess.run([
            CLI_COMMAND, "passescost", "--stationop", "AM",
            "--tagop", "EG", "--from", "19000101", "--to", "19001231", "--format", "csv"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("nPasses", result.stdout)
        self.assertIn(",0,", result.stdout)
        
        
    def test_passescost_invalid_stationop(self):
        """Test για passescost με μη έγκυρο stationOp"""
        result = subprocess.run([
            CLI_COMMAND, "passescost", "--stationop", "INVALID_OP",
            "--tagop", "EG", "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("tollOpID INVALID_OP does not exist", result.stdout)
        
        
    def test_passescost_invalid_format(self):
        """Test για passescost με μη υποστηριζόμενο format"""
        result = subprocess.run([
            CLI_COMMAND, "passescost", "--stationop", "AM", "--tagop", "EG",
            "--from", "20220101", "--to", "20221231", "--format", "xml"
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("invalid choice" in result.stderr or "invalid format" in result.stdout) 
        
    
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        result = subprocess.run([
            CLI_COMMAND, "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().split("\n")
        self.assertGreaterEqual(len(lines), 1, "Η έξοδος πρέπει να περιέχει τουλάχιστον το header.")
        self.assertEqual(lines[0], "visitingOpID,nPasses,passesCost", "Το header δεν είναι σωστό.")
        
        
    def test_chargesby_valid_opid(self):
        """Test για έγκυρο Operator ID στο chargesby"""
        result = subprocess.run([
            CLI_COMMAND, "chargesby", "--opid", "NAO",
            "--from", "20220101", "--to", "20221231", "--format", "csv"
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("visitingOpID,nPasses,passesCost", result.stdout)
        
    
    def test_invalid_command(self):
        """Test για μη έγκυρη εντολή"""
        result = subprocess.run([CLI_COMMAND, "invalidcommand"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("Unknown command" in result.stderr or "Unknown command" in result.stdout)

if __name__ == '__main__':
    unittest.main()

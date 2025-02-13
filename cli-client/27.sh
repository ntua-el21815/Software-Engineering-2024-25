./se2427 logout
read -p "Press any key to continue..."
read -p "Enter your username: " username
read -sp "Enter your password: " password
echo
./se2427 login --username "$username" --passw "$password"
read -p "Press any key to continue..."
./se2427 healthcheck
read -p "Press any key to continue..."
./se2427 resetpasses
read -p "Press any key to continue..."
./se2427 healthcheck
read -p "Press any key to continue..."
./se2427 resetstations
read -p "Press any key to continue..."
./se2427 healthcheck
read -p "Press any key to continue..."
./se2427 admin --addpasses --source passes27.csv
read -p "Press any key to continue..."
./se2427 healthcheck
read -p "Press any key to continue..."
./se2427 tollstationpasses --station AM08 --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
./se2427 tollstationpasses --station NAO04 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station NO01 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station OO03 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station XXX --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station OO03 --from 20220521 --to 20220604 --format YYY
read -p "Press any key to continue..."
./se2427 errorparam --station OO03 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station AM08 --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
./se2427 tollstationpasses --station NAO04 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station NO01 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station OO03 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station XXX --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 tollstationpasses --station OO03 --from 20220522 --to 20220602 --format YYY
read -p "Press any key to continue..."
./se2427 passanalysis --stationop AM --tagop NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
./se2427 passanalysis --stationop NAO --tagop AM --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop NO --tagop OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop OO --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop XXX --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop AM --tagop NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
./se2427 passanalysis --stationop NAO --tagop AM --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop NO --tagop OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop OO --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passanalysis --stationop XXX --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop AM --tagop NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
./se2427 passescost --stationop NAO --tagop AM --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop NO --tagop OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop OO --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop XXX --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop AM --tagop NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
./se2427 passescost --stationop NAO --tagop AM --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop NO --tagop OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop OO --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 passescost --stationop XXX --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
./se2427 chargesby --opid GE --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid NO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
./se2427 chargesby --opid GE --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
./se2427 chargesby --opid NO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."

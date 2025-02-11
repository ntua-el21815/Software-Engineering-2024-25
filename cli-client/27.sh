python ./se2427.py logout
read -p "Press any key to continue..."
read -p "Enter your username: " username
read -sp "Enter your password: " password
echo
python ./se2427.py login --username "$username" --passw "$password"
read -p "Press any key to continue..."
python ./se2427.py healthcheck
read -p "Press any key to continue..."
python ./se2427.py resetpasses
read -p "Press any key to continue..."
python ./se2427.py healthcheck
read -p "Press any key to continue..."
python ./se2427.py resetstations
read -p "Press any key to continue..."
python ./se2427.py healthcheck
read -p "Press any key to continue..."
python ./se2427.py admin --addpasses --source passes-sample.csv
read -p "Press any key to continue..."
python ./se2427.py healthcheck
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station AM08 --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station NAO04 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station NO01 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station OO03 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station XXX --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station OO03 --from 20220521 --to 20220604 --format YYY
read -p "Press any key to continue..."
python ./se2427.py errorparam --station OO03 --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station AM08 --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station NAO04 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station NO01 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station OO03 --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station XXX --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py tollstationpasses --station OO03 --from 20220522 --to 20220602 --format YYY
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop AM --tagop NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop NAO --tagop AM --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop NO --tagop OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop OO --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop XXX --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop AM --tagop NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop NAO --tagop AM --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop NO --tagop OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop OO --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passanalysis --stationop XXX --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop AM --tagop NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop NAO --tagop AM --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop NO --tagop OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop OO --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop XXX --tagop KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop AM --tagop NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop NAO --tagop AM --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop NO --tagop OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop OO --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py passescost --stationop XXX --tagop KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid NAO --from 20220521 --to 20220604 --format json
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid GE --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid OO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid KO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid NO --from 20220521 --to 20220604 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid NAO --from 20220522 --to 20220602 --format json
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid GE --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid OO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid KO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."
python ./se2427.py chargesby --opid NO --from 20220522 --to 20220602 --format csv
read -p "Press any key to continue..."

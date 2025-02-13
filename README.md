# TOLLIS (Toll Interoperability System)

Software Dependencies :
- Python >= 3.10 (in PATH)
- MySQL >= 8.0
- Web Browser (Chrome,Firefox,Microsoft Edge etc...) with Javascript Enabled.

- ATTENTION! If you want to deploy this project on a mac/linux (generally unix) then use MakefileForMac.Simply delete the main Makefile (it is for windows) and rename MakefileForMac to Makefile.Then proceed normally.

- To install all dependencies,create the database and generate all the needed certificates, use make scratch from the root directory of the project.
We advise against doing that however.It is better to run db_create.sql on your local database connection (localhost:3306) (located in back-end/rest_api/database) and then use make.

```console
foo@bar: softeng24-27 $ make scratch
```

```console
make scratch
```

- To do all of the above without creating the database automatically then simply use make

```console
foo@bar: softeng24-27 $ make
```

```console
make
```

- To run the api use make run_api

```console
foo@bar: softeng24-27 $ make run_api
```

```console
make run_api
```

- To run the Web Portal use make run_portal

```console
foo@bar: softeng24-27 $ make run_portal
```

```console
make run_portal
```

The address at which the API and Portal are available are displayed on the console after they have started running like this:
```console
* Running on https://{your_ip_address}:{port}
```

- To user the cli interface :
```console
foo@bar: softeng24-27 $ cd cli-client
foo@bar: cli-client $ python ./se2427.py {commands}
```

```console
cd cli-client
```

```console
python ./se2427.py {commands}
```

# TOLLIS (Toll Interoperability System)

- To install all dependencies,create the database and generate all the needed certificates, use make scratch from the root directory of the project.
We advise against doing that however.It is better to run db_create.sql on your local database connection (localhost:3306) (located in back-end/rest_api/database) and then use make.

```console
foo@bar: softeng24-27 $ make scratch
```

- To do all of the above without creating the database automatically then simply use make

```console
foo@bar: softeng24-27 $ make
```

- To run the api use make run_api

```console
foo@bar: softeng24-27 $ make run_api
```

- To run the Web Portal use make run_portal

```console
foo@bar: softeng24-27 $ make run_portal
```

The address at which the API and Portal are available are displayed on the console after they have started running like this:
```console
* Running on https://{your_ip_address}:{port}
```
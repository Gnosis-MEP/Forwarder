# Forwarder
Service responsible for sending the notification of matched events to the subscribers in the correct output format, as detailed by the inputs from the Query Register.

# Commands Stream
## Inputs
### addQuery
```json
{
    "id": "123-abc-123-abc-123-abc-123-abc-123-abc-123-abc",
    "action": "addQuery",
    "query_id": "44d7985a-e41e-4d02-a772-a8f7c1c69124",
    "subscriber_id": "44d7985a-e41e-4d02-a772-a8f7c1c69124"
}
```

### delQuery
```json
{
    "id": "123-abc-123-abc-123-abc-123-abc-123-abc-123-abc",
    "action": "delQuery",
    "query_id": "44d7985a-e41e-4d02-a772-a8f7c1c69124",
}
```

## Outputs
...
# Data Stream
## inputs
It expects events with at least this fields:
```
    "id": "123-abc-123-abc-123-abc-123-abc-123-abc-123-abc",
    "query_ids":  ['query-id1', 'query-id2']

```

## Outputs
Same as came in.

# Installation

## Configure .env
Copy the `example.env` file to `.env`, and inside it replace `SIT_PYPI_USER` and `SIT_PYPI_PASS` with the correct information.

## Installing Dependencies

### Using pipenv
Run `$ pipenv shell` to create a python virtualenv and load the .env into the environment variables in the shell.

Then run: `$ pipenv install` to install all packages, or `$ pipenv install -d` to also install the packages that help during development, eg: ipython.
This runs the installation using **pip** under the hood, but also handle the cross dependency issues between packages and checks the packages MD5s for security mesure.


### Using pip
To install using pip directly, one needs to use the `--extra-index-url` when running the `pip install` command, in order for to be able to use our private Pypi repository.

Load the environment variables from `.env` file using `source load_env.sh`.

To install from the `requirements.txt` file, run the following command:
```
$ pip install --extra-index-url https://${SIT_PYPI_USER}:${SIT_PYPI_PASS}@sit-pypi.herokuapp.com/simple -r requirements.txt
```

# Running
Enter project python environment (virtualenv or conda environment)

**ps**: It's required to have the .env variables loaded into the shell so that the project can run properly. An easy way of doing this is using `pipenv shell` to start the python environment with the `.env` file loaded or using the `source load_env.sh` command inside your preferable python environment (eg: conda).

Then, run the service with:
```
$ ./forwarder/run.py
```

# Testing
Run the script `run_tests.sh`, it will run all tests defined in the **tests** directory.

Also, there's a python script at `./forwarder/send_msgs_test.py` to do some simple manual testing, by sending msgs to the service stream key.


# Docker
## Build
Build the docker image using: `docker-compose build`

**ps**: It's required to have the .env variables loaded into the shell so that the container can build properly. An easy way of doing this is using `pipenv shell` to start the python environment with the `.env` file loaded or using the `source load_env.sh` command inside your preferable python environment (eg: conda).

## Run
Use `docker-compose run --rm service` to run the docker image


## Gitlab CI auto-build and tests

This is automatically enabled for this project (using the `.gitlab-ci.yml` present in this project root folder).

By default it will build the Dockerfile with every commit sent to the origin repository.

Afterwards, it will use this newly builty image to run the tests using the `./run_tests.sh` script.

But in order to make the automatic docker image build work, you'll need to set the `SIT_PYPI_USER` and `SIT_PYPI_PASS` variables in the Gitlab CI setting page: [Forwarder CI Setting Page](https://gitlab.insight-centre.org/sit/mps/forwarder/settings/ci_cd).

And, in order to make the automatic tests work, you should also set the rest of the environement variables required by your service, usually the same you have set in your `.env` and which allows your `./run_tests.sh` to work.


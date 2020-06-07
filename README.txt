This project is built using django and google app engine

to run locally

Moon landing 3:

Download python google cloud sdk https://cloud.google.com/sdk/docs

run:

gcloud components install app-engine-python
gcloud components install cloud-datastore-emulator

Create virtual environment:

python3 -m venv env
source env/bin/activate
cd <path to the directory you installed this code to>
pip install  -r requirements.txt

export DATASTORE_EMULATOR_HOST=localhost:8091
export GOOGLE_APPLICATION_CREDENTIALS=<PATH to Project credentials>
python manage.py runserver


You should run the datastore emulator by:

gcloud beta emulators datastore start —-data-dir=<PATH to empty folder in your local env> --host-port=localhost:8091

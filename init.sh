cd
mkdir concert-buddy
cd concert-buddy
git clone https://github.com/RootofalleviI/Concert-Buddy-aggregator .

sudo apt install -y python3-venv
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
pip freeze
sudo setcap 'cap_net_bind_service=+ep' ./venv/bin/python3

uvicorn main:app --host 0.0.0.0 --port 8000
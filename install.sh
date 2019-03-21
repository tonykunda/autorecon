# Install Masscan
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
cd ..

# Install Amass
mkdir amass
wget https://github.com/OWASP/Amass/releases/download/2.9.4/amass_2.9.4_macos_amd64.zip
unzip amass_2.9.4_macos_amd64.zip
mv amass_2.9.4_macos_amd64 amass
rm amass_2.9.4_macos_amd64.zip

# Install Webkit2png
git clone https://github.com/paulhammond/webkit2png

# Intall Python Depends
pip install -r requirements.txt

# Install Webapp Things
cd project/webapp
bower install
cd ../../

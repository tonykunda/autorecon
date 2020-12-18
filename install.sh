# Install Masscan
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
cd ..

# Install Amass
wget https://github.com/OWASP/Amass/releases/download/v3.10.5/amass_macos_amd64.zip
unzip amass_v3.4.2_macos_amd64.zip
mv amass_v3.4.2_macos_amd64 amass
rm amass_v3.4.2_macos_amd64.zip

# Install Subfinder
mkdir subfinder
cd subfinder
wget https://github.com/projectdiscovery/subfinder/releases/download/v2.3.1/subfinder-darwin-amd64.tar
tar -xvf subfinder-darwin-amd64.tar
mv subfinder-darwin-amd64 subfinder
rm subfinder-darwin-amd64.tar
cd ..

# Install Webkit2png
git clone https://github.com/tonykunda/webkit2png
cd webkit2png
mv webkit2png webkit2png.py
cd ..

# Intall Python Depends
pip install -r requirements.txt

# Install Webapp Things
cd projects/webapp
bower install
cd ../../

# Make tmp dir
mkdir tmp

# Install Masscan
git clone https://github.com/robertdavidgraham/masscan
cd masscan
make
cd ..

# Install Amass
wget https://github.com/OWASP/Amass/releases/download/2.9.4/amass_2.9.4_macos_amd64.zip
unzip amass_2.9.4_macos_amd64.zip
mv amass_2.9.4_macos_amd64 amass
rm amass_2.9.4_macos_amd64.zip

# Install Subfinder
git clone https://github.com/subfinder/subfinder
cd subfinder
go build main.go
mv main subfinder
cd ..

# Install Webkit2png
git clone https://github.com/paulhammond/webkit2png
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

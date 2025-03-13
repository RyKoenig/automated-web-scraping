#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Installing Google Chrome..."

# Download and install the latest Google Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get -f install -y
rm google-chrome-stable_current_amd64.deb

echo "Google Chrome installed successfully!"


# Determine the full Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+')

echo "Downloading ChromeDriver version ${CHROME_VERSION}..."

# Get the latest compatible ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Validate if the ChromeDriver version was retrieved successfully
if [[ -z "$CHROMEDRIVER_VERSION" ]]; then
    echo "Error: Unable to fetch ChromeDriver version for Chrome $CHROME_VERSION."
    exit 1
fi

echo "Installing ChromeDriver..."

sudo apt-get update && sudo apt-get install -y unzip

# Determine the full Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

# Construct the correct download URL
BASE_URL="https://storage.googleapis.com/chrome-for-testing-public"
PLATFORM="linux64"
CHROMEDRIVER_ZIP="chromedriver-${PLATFORM}.zip"
DOWNLOAD_URL="${BASE_URL}/${CHROME_VERSION}/${PLATFORM}/${CHROMEDRIVER_ZIP}"

# Download ChromeDriver
echo "Downloading ChromeDriver version ${CHROME_VERSION}..."
curl -O ${DOWNLOAD_URL}

# Verify if the file is a valid ZIP
if file "${CHROMEDRIVER_ZIP}" | grep -q "Zip archive data"; then
    echo "Extracting ${CHROMEDRIVER_ZIP}..."
    unzip -o ${CHROMEDRIVER_ZIP}
else
    echo "Error: Downloaded file is not a valid ZIP archive!"
    rm -f ${CHROMEDRIVER_ZIP}
    exit 1
fi

# Move ChromeDriver binary to /usr/local/bin
echo "Moving chromedriver to /usr/local/bin..."
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver


AGENT_VERSION=$(google-chrome --version | grep -oP '[0-9]+\.0')
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${AGENT_VERSION}.0.0 Safari/537.36"

NON_ROOT_USER=$(logname)

sed -i "s|'/home/yourCreatedLinuxUser/Web-Scraping-Automation/'|'/home/$NON_ROOT_USER/Web-Scraping-Automation/'|" /home/$NON_ROOT_USER/Web-Scraping-Automation/constants.py
sed -i "s|chrome_options.add_argument('user-agent=[^']*')|chrome_options.add_argument('user-agent=$USER_AGENT')|" /home/$NON_ROOT_USER/Web-Scraping-Automation/nfl_scraper/scrape_snap_counts.py
sed -i "s|chrome_options.add_argument('user-agent=[^']*')|chrome_options.add_argument('user-agent=$USER_AGENT')|" /home/$NON_ROOT_USER/Web-Scraping-Automation/nba_scraper/scrape_espn_rosters.py

# Clean up
echo "Cleaning up..."
rm -rf chromedriver-linux64 ${CHROMEDRIVER_ZIP}


# echo "ChromeDriver installed successfully!"

echo "Installing Adblock Plus extension..."

# Download Adblock Plus extension (.crx file)
wget -q -O adblocker.crx "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=$CHROME_VERSION&x=id%3Dcfhdojbkjhnklbpkdaibdccddilifddb%26uc"
sudo mv adblocker.crx /usr/local/share/adblocker.crx

echo "Adblock Plus installed at /usr/local/share/adblocker.crx"

# Verify installation
google-chrome --version
chromedriver --version

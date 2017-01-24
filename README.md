# xDripAPS
REST microservice designed to allow xDrip CGM data to be used in OpenAPS

PLEASE NOTE: the code in this repository is a work-in-progress and should be used for experimental purposes only. 

Do you use OpenAPS and xDrip? Until now, this usually means you need an internet connection to upload your CGM data to Nightscout and then have OpenAPS download it from there to use in your loop. This repository allows you to get your CGM data from xDrip into OpenAPS without the need for an internet connection.

xDripAPS is a lightweight microservice intended to be used on Raspberry Pi or Intel Edison OpenAPS rigs. Users of the xDrip Android app can use the "REST API Upload" option to send CGM data to this service. The service stores the data in a SQLite3 database. The service can be invoked from within OpenAPS to retrieve CGM data. This approach allows for offline/camping-mode looping. No internet access is required, just a local, or "personal" network between the Android phone and the OpenAPS rig (using either WiFi hotspotting or bluetooth tethering).

As of January 2017, support for xDripAPS is now included in the OpenAPS oref0-setup.sh script. Ensure that you use the dev branch, as this has not been merged with master yet. When running the oref0-setup.sh script, you will be prompted to specify a CGM type (e.g. MDT, G4). You can specify "xdrip" (without the quotes). This will install xDripAPS and all dependencies. Alternatively, manual installation instructions can be found at the bottom of this page.

## Overview
With xDripAPS, the flow of data is as follows - 

(1) CGM transmitter --> (2) xDrip/xDrip+ Android app --> (3) OpenAPS rig (e.g. Edison) --> (4) Nightscout

1. Usually a Dexcom G5, or G4 plus xDrip wireless bridge.
2. Either xDrip or xDrip+ can be used. In the app, the REST API Upload feature is normally used to upload CGM data to Nightscout. Instead, we use this feature to upload to xDripAPS on your OpenAPS rig (further details below).
3. Your OpenAPS rig - usually a Raspberry Pi or an Intel Edison.
4. The xDrip app is now uploading your data to xDripAPS on your OpenAPS rig rather than to Nightscout. OpenAPS will upload your CGM data to Nightscout instead.

## Setup Steps (using oref0-setup.sh script)

### Setting up your OpenAPS rig
Install OpenAPS as per the documentation. When running the oref0-setup script, you will be prompted to specify a CGM source. Enter "xdrip" (without the quotes).

### Connect your Android phone and your OpenAPS rig
For the xDrip app on your Android phone to be able to send CGM data to xDripAPS on your OpenAPS rig, they need to be connected to the same "personal" network. Note that an internet connection is not required - this solution allows you to loop without internet connectivity. Data which is 'missing' from Nightscout will be uploaded when you regain internet connectivity.

There are two approaches for establishing a "personal" network between your phone and your OpenAPS rig. The first is to run a WiFi hotspot on your phone and connect your OpenAPS rig to the WiFi network your phone exposes. This is the easiest option, but there are two drawbacks - it drains your phone battery quickly, and your phone cannot connect to a normal WiFi network while the WiFi hotspot is enabled (it can connect to the internet via 3G/4G when coverage is available).

The other option is to enable bluetooth tethering on your phone and have your OpenAPS rig connect to it. This does not drain the phone's battery as quickly and means that the phone can still connect to a normal WiFi network for internet access when available (and to 3G/4G networks when WiFi is not available). I use this approach 24/7 - my OpenAPS rig is permanently tethered to my Nexus 6P phone. I can get a full day of phone usage without running out of battery, unless I make a lot of calls or have a lot of screen-on time. 

Instructions on both approaches can be found in the main OpenAPS documentation.

### Configuring the xDrip Android app
First, determine your OpenAPS rig's IP address within your "personal" network. If you can open a terminal session to your rig via serial, then `ifconfig wlan0` (when using the WiFi hostpost option) or `ifconfig bnep0` (when using bluetooth tethering) will display your IP address. Alternatively, you can use an Android app - there are lots of "Network IP Scanner" apps in the Play store. The Hurricane Electric Network Tools app works with both the WiFi hotspot and BT tethering options.

Then, open xDrip or xDrip+ settings and in the REST API Upload setting, configure the following URL - 

`http://<api_secret>@<rig_ip_address>:5000/api/v1/`

Note: ensure you enter http:// (NOT https://). <api_secret> is the plain-text API secret you used when you set up OpenAPS/Nightscout and <rig_ip_address> is the IP address of your OpenAPS rig (starting 192.168). For example, this is the value I have configured (I have obscured my API secret) -

![REST API Upload setting](https://github.com/colinlennon/xDripAPS/blob/master/xDrip_REST_API_cropped.png "REST API Upload setting")

If using xDrip+ you also need to navigate to Settings > Cloud Upload > MongoDB and ensure that the "Skip LAN uploads" option is NOT selected. If you don't have this setting, update to a recent version of the xDrip+ app. (This option was added to a nightly build around December 2016).




### Manual installation steps  
#### N.B. It is recommended that you use the oref0-setup script as described above, rather than installing manually.

1. Install SQLite3 -

  a. Raspbian - 
    ```
    apt-get install sqlite3
    ```

  b. Yocto - 
    ```
    cd ~
    wget https://sqlite.org/2016/sqlite-tools-linux-x86-3150200.zip
    unzip sqlite-tools-linux-x86-3150200.zip
    mv sqlite-tools-linux-x86-3150200 sqlite
    ```

2. Get dependencies -
  ```
  pip install flask
  pip install flask-restful
  ```

3. Clone this repo -
  ```
  cd ~
  git clone https://github.com/colinlennon/xDripAPS.git .xDripAPS
  ```

4. Create directory for database file - 
  ```
  mkdir -p ~/.xDripAPS_data
  ```

5. Add cron entry to start the microservice at startup - 
  e.g. - 
  `@reboot         python /home/root/.xDripAPS/xDripAPS.py`

6. Cofigure the xDrip Android app -
   ```
  xDrip > Settings > REST API Upload > Set Enabled and enter Base URL: http://[API_SECRET]@[Pi/Edison_IP_address]:5000/api/v1/
  ```
  
  (Note: Enter your plain-text API_SECRET in the Android app, not the hashed version of it).


7. Use the microservice within OpenAPS
  e.g.
  ```
  openaps device add xdrip process 'bash -c "curl -s http://localhost:5000/api/v1/entries?count=288"'
  openaps report add monitor/glucose.json text xdrip shell
  ```

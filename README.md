# xDripAPS
REST microservice designed to allow xDrip CGM data to be used in OpenAPS

PLEASE NOTE: the code in this repository is a work-in-progress and should be used for experimental purposes only. 

xDripAPS is a lightweight microservice intended to be used on Raspberry Pi or Intel Edison OpenAPS rigs. Users of the xDrip Android app can use the "REST API Upload" option to send CGM data to this service. The service stores the data in a SQLite3 database. The service can be invoked from within OpenAPS to retrieve CGM data. This approach allows for offline/camping-mode looping. No internet access is required, just a local network between the Android phone and the OpenAPS rig (using either WiFi hotspotting or bluetooth tethering).

Setup steps (to be completed) - 

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
  git clone https://github.com/colinlennon/xDripAPS.git
  ```

4. Create directory for database file - 
  ```
  mkdir -p $HOME/.xDripAPS_data
  ```

5. Add cron entry to start the microservice at startup - 
  e.g. - 
  `@reboot         python /home/root/xDripAPS/xDripAPS.py`

6. Cofigure the xDrip Android app -
  xDrip > Settings > REST API Upload > Set Enabled and enter Base URL: http://[Pi/Edison_IP_address]:5000/api/v1/

7. Use the microservice within OpenAPS
  e.g.
  ```
  openaps device add xdrip process 'bash -c "curl -s http://localhost:5000/api/v1/entries?count=288 | json -e \"this.glucose = this.sgv\""'
  openaps report add monitor/glucose.json text xdrip shell
  ```

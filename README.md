# La Crosse To Wunderground
Upload data from your La Crosse Personal Weather Station to Wunderground (weather underground)

## HOWTO

1. Setup your La Crosse View app, note your login credentials

2. Setup your Wunderground Personal Weather Station, note the station id and key

3. Update `lacrosse_to_wunderground.py` to include the credentials from steps 1 and 2.  The credentials are listed at the top of the file.

4. Open a terminal and `cd` to the same directory as the lacrosse_to_wunderground.py file.

5. Clone the required support repos, for example

  .. code-block:: bash

    cd ~/
    mkdir myweather
    cd myweather
    git clone git@github.com:keithprickett/lacrosse_to_wunderground.git .
    git clone git@github.com:keithprickett/wunderground_uploader.git
    git clone git@github.com:keithprickett/lacrosse_weather.git

6. Create your initial starting point, which could be 0 or another UTC timestamp, for example:

  .. code-block:: bash

    cd ~/myweather
    echo 0 > myweather_ts

7. Run the program

  .. code-block:: bash
  
    cd ~/myweather && python3 ./lacrosse_to_wunderground.py `echo myweather_ts` > myweather_ts

8. Repeat step 7 as often as desired to update, or put it in a cron or other automation system.



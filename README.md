# vdr-getchannels
Python script to generate channels.conf file for VDR using KingOfSat informations.

It could use a config file to parse full list and produce custom channels.conf file with only favourites channels.

config file format is:
:[ <group name> ]
<channel name>;<bouquet name>

Can find list of available sat id and bouquets in app_params.py file. You can update it manually to extend supported KingOfSat list.

usage: getchannels.py [-h] [-u] [-c FILENAME] -l LIST_ID -o FILENAME

optional arguments:
  -h, --help            show this help message and exit
  -u, --upper           set to upper polarity digit in output
  -c FILENAME, --useconfig FILENAME
                        enable use of config file, searched in "conf"
                        subfolder, to generate output

  -l LIST_ID, --list LIST_ID
                        set KingOfSat source channels list used to generate
                        local VDR channels list. Can use one of follow values:
                        19.2E, 13.0E
  -o FILENAME, --output FILENAME
                        enable use of config file, searched in "conf"
                        subfolder, to generate output


List of all channels not founded is pushed into <FILENAME>.missing file


Examples:
$ python getchannels.py -u -c getchannels.conf -l 13.0E -o channels.conf


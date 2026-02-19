git clone https://github.com/mburger-stsci/nexoclom2.git
conda env create -f nexoclom_environment.yml

(3) Create the .nexoclom file
    (a) In your home directory create a file called .nexoclom with the
    following lines:
savepath = <fullpath>/modeloutputs
datapath = <fullpath>/ModelData
database = thesolarsystemmb
mesdatapath = <fullpath>/UVVSData
mesdatabase = messengeruvvsdb

<fullpath> does not need to be the same in all lines, but the directories all
need to be valid.

(4) Initialize the postgres server if necessary:
    (a) In your .bashrc or .bash_profile file (the file that runs when you
    start a terminal window) add the line:
        export PGDATA=/Users/mburger/.postgres/main
    (This step technically isn't needed because the environment variable gets
    set when you activate the environment).
    (b) > initdb -D $PGDATA
    (c) > pg_ctl -l $PGDATA/logfile start
    (d) > createdb <username>
        * Find <username> with > echo $USER
    (e) > createdb thesolarsystemmb
        * This needs to match database in the .nexoclom file
    (g) > createdb messengeruvvsdb
        * This needs to match mesdatabase in the .nexoclom file

(5) Configure the MESSENGER UVVS database
    (a) Download the MESSENGERdata package. Get the link from Matt.
    (b) Put the file in the mesdatapath directory and untar it.
        > tar -xvzf Level1.tar.gz
    (c) Then run:
    (nexoclom)$ ipython
    Python 3.8.13 | packaged by conda-forge | (default, Mar 25 2022, 06:06:49)
    Type 'copyright', 'credits' or 'license' for more information
    IPython 8.2.0 -- An enhanced Interactive Python. Type '?' for help.

    In [1]: from MESSENGERuvvs import initialize_MESSENGERdata

    In [2]: initialize_MESSENGERdata()

    This will take a while to run (hours probably).

(6) To install updates, run:
    (nexoclom) pip install --upgrade nexoclom
    (nexoclom) pip install --upgrade MESSENGERuvvs

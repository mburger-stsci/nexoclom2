### NexoclomConfig
* Successful runs
    1. Only savepath is given ➔ nexoclom2a
    2. savepath, database, user are given ➔ nexoclom2b
    3. savepath, extra unused value are given ➔ nexoclom2c
* Failure runs
    1. savepath not given ➔ nexoclom2d
    2. user not given and is not a environment variable ➔ nexoclom2e
        * Also contains a line that isn't read in to complete the code coverage
    3. NEXOCLOMCONFIG environment variable not set 
    4. NEXOCLOMCONFIG file does not exist ➔ nexoclom2f
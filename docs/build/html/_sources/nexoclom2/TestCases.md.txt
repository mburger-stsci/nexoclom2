# NEXOCLOM Test Cases

Documentation for all the unit, system, and regression tests performed in the nexoclom test suite.

## Utilities

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

### DatabaseOperations

* __init__
  * sets the path to the database correctly
* make_acceptable
  * Can strip the input classes into dict with only floats, strings, ints, 
    bools, and dicts.
  * One-to-one mapping between class and cleaned up version
* insert_parts
  * Only inserts records that aren't currently in the table. This won't be 
    100% foolproof since there could be multiple processes accessing the 
    database, but that's acceptable.
* query_parts
* insert outputs
* query_outputs

## Solar System

### SSObject

1. Case-insensitive object name
2. Object with NAIF ID but not in table
3. Object that doesn't exist at all
4. Object equality
5. Object length (number of satellites + 1)
6. Planets and satellites

## Initial State

### Input

* Don't need to test every configuration. That's done for the individual 
  pieces. Just need to verfiy that it parses the file correctly. 


### Geometry

1. Setting everything
   1. With modeltime
   2. Without modeltime
2. Setting only required
3. Starting from Sun, Planet, Satellite
4. Exceptions are properly raised.

### Forces
1. Basic comparisons on equality and non-equality of different settings

## Statement of Purpose
The Neutral EXOsphere and CLoud Model is a numerical model for simulating
collisionless exospheres and neutral clouds around astronomical bodies. These
bodies may be planets (in this solar system or around other stars), satellites
of planets, or small bodies. The exosphere may be surface-bounded or start at a
pre-defined (possibly spatially or time variable) exobase above the surface.
Users can use predefined or custom initial spatial and energy distributions from
the surface or exobase. Inputs to the model are defined in a plain-text `.input`
file. The documentation species the structure of the `.input` file, which
parameters are required, and default value for optional parameters. 

A full test suite with unit, integration, and regression tests is implemented to
ensure that physical processes are implemented correctly, changes in the code do
not change or break functionality, and that saved results can be retrieved
correctly.

# High Level Requirements

## Utilities
### 1 Configuration
1. Configuration file is a text file containing a set of `key = value` pairs.
2. Filename is set by an environment variable.
3. Required variable: `savepath` = path to directory where data is saved
4. Optional variable: `database` = Name of the TinyDB file containing the outputs database. Default = `thesolarsystemmb.db`
5. `user` is required if it is not set by the operating system (e.g. with Windows)

## Input/Output

### 1 System geometry
1. Specify the system geometry either with a time stamp or specifying true anomaly angle, central meridian longitude, etc.
2. Central object (e.g., planet or Sun) for the simulation is fixed
3. StartPoint is either the central object or a satellite of the central object
### 2 Energy distributions
1. Support for user defined sources either as a probability distribution or a user-defined function
### 3 Spatial distributions
1. Support for surface maps in either solar-fixed or body-fixed coordinates
### 4 Saved results
1. Initial conditions specified by plain text input file in the form `parameter = value` or as a JSON file.
2. Inputs will be saved in a NoSQL database 
3. When the database is queried only outputs consistent with the queried inputs are returned.
	* Some input parameters may involve a comparison (e.g., 5º ≤ TAA < 6º)
4. Outputs need to be saved in a format that can be used by packages that allow for larger than memory datasets.
5. There should be a way to include customized source distributions specified by the user.

- When doing fitted models, don't need any of the inputs like packets or Input

## Physics
### 1 Forces
* Gravity
* Radiation pressure

### 2 Loss processes

### 3 Coordinate systems
* Solar-fixed 
    * $\hat{x}$ in planet's (starting point's) equatorial plane toward Sun
    * $\hat{y}$ in planet's (starting point's) equatorial plane duskward
    * $\hat{z}$ points north
    * longitude: angle from $+\hat{x}$ axis to projection of position vector on XY plane. Increases in counter-clockwise direction
        * 0º = sub-solar point; 90º = dusk point, 180º = midnight, 270º = dawn
    * Local time increases counter-clockwise from 0h (midnight).
        $local\_time = ((latitude + 180^\circ) \times \frac{24}{360^\circ}) \mod 24$
    * Latitude ranges from -90º (south pole) to 90º (north pole)
* body-fixed
    * TBD

# Test Requirements
### NexoclomConfig
* 
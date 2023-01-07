# Satellite Simulation Driver

This driver is meant for simulating a satellite transferring keys to two ground stations.

## Install

```
pip install -r requirements.txt
```

## Usage

The driver can simply be run by providing the site ID of remote station. The driver must be run locally on one of the ground stations to work as it uses the `qkdlink.json` to find the relevant info to communicate with the other ground station.

```bash
python3 -m satellite_simulator D # Send key to local and remote site D
```

To see what other arguments are available check the help text.

```bash
python3 -m satellite_simulator --help
```

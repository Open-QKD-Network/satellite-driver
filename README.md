# Satellite Simulation Driver

This driver is meant for simulating a satellite transferring keys to two ground stations.

## Install

```
pip install -r requirements.txt
```

## Usage

The driver can simply be run by providing the site IDs of the two ground stations. The driver must be run locally on one of the ground stations to work as it uses the `qkdlink.json` to find the relevant info to communicate with the other ground station.

```bash
python3 -m satellite_simulator A B # send keys to sites A and B
```

To see what other arguments are available check the help text.

```bash
python3 -m satellite_simulator --help
```

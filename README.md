# OctoPrint PSU Control - Tenda Beli SP3

Adds Tenda Beli SP3 support to OctoPrint-PSUControl as a sub-plugin.

This plugin is based on [OctoPrint PSU Control - Tasmota](https://github.com/kantlivelong/OctoPrint-PSUControl-Tasmota) plugin code by [Shawn Bruce](https://github.com/kantlivelong).

## Setup

- Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL: https://github.com/jgroman/OctoPrint-PSUControl-TendaBeli/archive/master.zip

## Configuration

- Configure this plugin: set smart plug IP address
- Select this plugin as a Switching and/or Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)

## Notes

- Plugin was tested with plugs:
  - HW version EU V1.0, SW version V1.1.0.13(115)_SP3_EU
  - HW version AU V1.0, SW version V1.1.0.13(115)_SP3_AU

- Tenda Beli SP3 smart plug can be configured using official Tenda Beli app.

- If you prefer not connecting your SP3 smart plug to any cloud, it is also possible to provision your device manually:
  1. Unpack new device or reset existing device by holding the Power On/Reset button for more than 6 seconds.
  1. Connect to open WLAN provided by this plug
  1. Find out smart plug IP address (= WLAN gateway)
  1. Run command `curl -X POST http://PLUG-IP:5000/guideDone -d '{"account":"1","key":"YOUR-WLAN-KEY","server":"beli.intranet","ssid":"YOUR-WLAN-SSID"}'`
  1. Smart plug will reset and connect to provided WLAN.

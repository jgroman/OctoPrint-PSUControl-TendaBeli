# coding=utf-8
from __future__ import absolute_import

__author__ = "Jaroslav Groman <jgroman+github@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2021 Jaroslav Groman - Released under terms of the AGPLv3 License"

import requests

import octoprint.plugin

class PSUControl_TendaBeli(octoprint.plugin.RestartNeedingPlugin,
							octoprint.plugin.StartupPlugin,
                            octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.TemplatePlugin):

	def __init__(self):
		self.config = dict()

	##~~ StartupPlugin mixin

	def on_startup(self, host, port):
		'''
		Called just before the server is actually launched.
		'''
		psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
		if 'register_plugin' not in psucontrol_helpers.keys():
			self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
			return

		self._logger.debug("Registering plugin with PSUControl")
		psucontrol_helpers['register_plugin'](self)

	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		'''
		Allows configuration of injected navbar, sidebar, tab and settings templates.
		'''
		return [
			dict(type="settings", custom_bindings=False)
		]

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		''' 
		Retrieves the plugin’s default settings with which the plugin’s settings 
		manager will be initialized. 
		'''
		return dict(
			address = ''
		)

	def on_settings_initialized(self):
		''' 
		Called after the settings have been initialized and - if necessary - also 
		been migrated through a call to func:on_settings_migrate. 
		'''
		self.reload_settings()

	def on_settings_save(self, data):
		'''
		Saves the settings for the plugin, called by the Settings API view 
		in order to persist all settings from all plugins.
		'''
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		self.reload_settings()

	def get_settings_version(self):
		'''
		Retrieves the settings format version of the plugin.
		'''
		return 1

	def on_settings_migrate(self, target, current=None):
		'''
		Called by OctoPrint if it detects that the installed version of the plugin 
		necessitates a higher settings version than the one currently stored 
		in _config.yaml.
		'''
		pass

	##~~ Custom methods

	def reload_settings(self):
		for k, v in self.get_settings_defaults().items():
			if type(v) == str:
				v = self._settings.get([k])
			elif type(v) == int:
				v = self._settings.get_int([k])
			elif type(v) == float:
				v = self._settings.get_float([k])
			elif type(v) == bool:
				v = self._settings.get_boolean([k])

			self.config[k] = v
			self._logger.debug("{}: {}".format(k, v))

	def send(self, path, payload):
		url = ("http://{}:5000/" + path).format(self.config['address'])

		response = None
		try:
			response = requests.post(url, data=payload, timeout=3)
		except (
				requests.exceptions.InvalidURL,
				requests.exceptions.ConnectionError
		):
			self._logger.error("Unable to communicate with device. Check settings.")
		except Exception:
			self._logger.exception("Exception while making API call")
		else:
			self._logger.debug("payload={}, status_code={}, text={}".format(payload, response.status_code, response.text))

		return response

	def change_psu_state(self, state):
		response = self.send('setSta', '{{"status":{}}}'.format(state))

		if not response:
			self._logger.error("Unable to determine status. Check settings.")
			return

		data = response.json()

		status = None
		try:
			status = (data['status'] == 1)
		except KeyError:
			pass

		if status == None:
			self._logger.error("Unable to determine status. Check settings.")
			status = False
			return

		if state != (state == 1):
			self._logger.error("Inconsistent smart plug status. Check settings.")
			status = False
			return

	def turn_psu_on(self):
		self._logger.debug("Switching PSU On")
		self.change_psu_state(1)

	def turn_psu_off(self):
		self._logger.debug("Switching PSU Off")
		self.change_psu_state(0)

	def get_psu_state(self):
		response = self.send('getSta', '')
		if not response:
			return False
		data = response.json()

		status = None
		try:
			status = (data['data']['status'] == 1)
		except KeyError:
			pass

		if status == None:
			self._logger.error("Unable to determine status. Check settings.")
			status = False

		return status

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			psucontrol_tendabeli=dict(
				displayName="PSU Control - Tenda Beli",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="jgroman",
				repo="OctoPrint-PSUControl-TendaBeli",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/jgroman/OctoPrint-PSUControl-TendaBeli/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PSU Control - Tenda Beli"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PSUControl_TendaBeli()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}


#
# WPA Supplicant OMF 5.4 application description
#
defApplication('tutorials:utils:wpa', 'wpa') do |app|
	app.path = "/usr/sbin/omf-wpa"
	app.version(1, 0, 0)
	app.shortDescription = 'WPA Supplicant configurator tool'
	app.description = 'WPA Supplicant configurator tool'

	# Properties
	app.defProperty('wlan', 'Wireless interface', '--wlan', :type => :string)
	app.defProperty('essid', 'Network ESSID', '--essid', :type => :string)
	app.defProperty('duration', 'Duration of the experiment', '--duration', :type => :integer)
end

# Local Variables:
# mode:ruby
# End:
# vim: ft=ruby:sw=2

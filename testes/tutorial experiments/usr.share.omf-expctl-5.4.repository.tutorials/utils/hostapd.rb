#
# Hostapd OMF 5.4 application description
#
defApplication('tutorials:utils:hostapd', 'hostapd') do |app|
	app.path = "/usr/sbin/omf-hostapd"
	app.version(1, 0, 0)
	app.shortDescription = 'Hostapd configurator tool'
	app.description = 'Hostapd configurator tool'

	# Properties
	app.defProperty('wlan', 'Wireless interface', '--wlan', :type => :string)
	app.defProperty('essid', 'Network ESSID', '--essid', :type => :string)
	app.defProperty('channel', 'Wireless channel', '--channel', :type => :integer)
	app.defProperty('type', '802.11 type', '--type', :type => :string)
	app.defProperty('duration', 'Duration of the experiment', '--duration', :type => :integer)
end

# Local Variables:
# mode:ruby
# End:
# vim: ft=ruby:sw=2

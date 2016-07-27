#
# Wlan configurator OMF 5.4 application description
# This application can set the bitrate of interface.
#
defApplication('tutorials:utils:wlanconfig', 'wlanconfig') do |app|
  app.path = "/usr/sbin/omf-wlanconfig"
  app.version(1, 0, 1)
  app.shortDescription = 'Wlan configurator tool'
  app.description = 'Wlan configurator tool'

  # Properties
  app.defProperty('wlan', 'Wireless interface', '--wlan', :type => :string)
  app.defProperty('mode', 'Wireless interface mode', '--mode', :type => :string)
  app.defProperty('type', '802.11 type', '--type', :type => :string)
  app.defProperty('channel', 'Wireless channel', '--channel', :type => :integer)
  app.defProperty('essid', 'Network ESSID', '--essid', :type => :string)
  app.defProperty('ip_address', 'Interface IP address', '--ip_address', :type => :string)
  app.defProperty('netmask', 'Interface netmask', '--netmask', :type => :string)
  app.defProperty('bitrate_type', 'Bitrate type', '--bitrate_type', :type => :string)
  app.defProperty('bitrate_value', 'Bitrate type value', '--bitrate_value', :type => :string)
  app.defProperty('duration', 'Duration of the experiment', '--duration', :type => :integer)
  app.defProperty('tx_power', 'Tx power', '--tx_power', :type => :string)
  app.defProperty('retry', 'Retransmission', '--retry', :type => :integer)
  app.defProperty('noack', 'Disable ack', '--noack', :type => :string)

end

# Local Variables:
# mode:ruby
# End:
# vim: ft=ruby:sw=2

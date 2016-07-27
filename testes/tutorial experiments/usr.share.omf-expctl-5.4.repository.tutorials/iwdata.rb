#
# Application to collect iw data for OMF 5.4
#
defApplication('tutorials:iwdata', 'iwdata') do |app|
  app.path = "/usr/sbin/omf-iwdata"
  app.version(1, 0, 0)
  app.shortDescription = 'iw data collector tool'
  app.description = 'iw data collector tool'

  # Oml properties
  app.defProperty('oml-id', 'Sender identify', '--oml-id', :type => :string)
  app.defProperty('oml-domain', 'Experiment domain', '--oml-domain', :type => :string)
  app.defProperty('oml-collect', 'OML server URI (tcp:ip:port)', '--oml-collect', :type => :string)

  # App properties
  app.defProperty('wlan', 'Wireless interface', '--wlan', :type => :string)
  app.defProperty('duration', 'Duration of the experiment', '--duration', :type => :integer)
end

# Local Variables:
# mode:ruby
# End:
# vim: ft=ruby:sw=2

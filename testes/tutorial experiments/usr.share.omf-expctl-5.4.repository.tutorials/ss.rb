#
# Application to collect ss data of tcp for OMF 5.4
#
defApplication('tutorials:ss', 'ss') do |app|
  app.path = "/usr/sbin/omf-ss"
  app.version(1, 0, 0)
  app.shortDescription = 'Tcp ss collector tool'
  app.description = 'Tcp ss collector tool'

  # Oml properties
  app.defProperty('oml-id', 'Sender identify', '--oml-id', :type => :string)
  app.defProperty('oml-domain', 'Experiment domain', '--oml-domain', :type => :string)
  app.defProperty('oml-collect', 'OML server URI (tcp:ip:port)', '--oml-collect', :type => :string)

  # App properties
  app.defProperty('server', 'Connection in format ip:port to get the socket congestion window', '--server', :type => :string)
  app.defProperty('duration', 'Duration of the experiment', '--duration', :type => :integer)
end

# Local Variables:
# mode:ruby
# End:
# vim: ft=ruby:sw=2

defProperty('server_node','omf.ufg.node8',"ID of server node")
defProperty('client_node','omf.ufg.node1',"ID of client node")
defProperty('runtime', 60, "Time in second for the experiment is to run")
defProperty('iperf_server_address', '192.168.129.2', "Iperf server IP address")
defProperty('iperf_client_address', '192.168.129.1', "Iperf client IP address")
defProperty('iperf_port', 2000, "Iperf port")
defProperty('iperf_interval', '1', "Iperf interval")
defProperty('iperf_isUDP', 'false', "Set Iperf UDP")
defProperty('iperf_bandwidth', '15M', 'Iperf bandwidth')

# Define the resources group 'Server'
defGroup('Server', property.server_node) do |node|
  node.addApplication("tutorials:iperf", :id => 'iperf_server') do |app|
    app.setProperty('server', true)
    app.setProperty('port', property.iperf_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('udp', (property.iperf_isUDP.value == 'true' ? true : false))
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'server')
    app.setProperty('oml-domain', 'wireless_experiment_iperf')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:utils:wlanconfig", :id => 'server_wlanconfig') do |app|
    app.setProperty('wlan', 'wlan0')
    app.setProperty('mode', 'adhoc')
    app.setProperty('type', 'g')
    app.setProperty('channel', 13)
    app.setProperty('essid', 'omf_we')
    app.setProperty('ip_address', property.iperf_server_address)
    app.setProperty('duration', (property.runtime + 20))
  end
end

# Define the resources group 'Client'
defGroup('Client', property.client_node) do |node|
  node.addApplication("tutorials:iperf", :id => 'iperf_client') do |app|
    app.setProperty('client', property.iperf_server_address)
    app.setProperty('port', property.iperf_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('time', property.runtime)
    app.setProperty('udp', (property.iperf_isUDP.value == 'true' ? true : false))
    if property.iperf_isUDP.value == 'true'
      app.setProperty('bandwidth', property.iperf_bandwidth)
    end
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'client')
    app.setProperty('oml-domain', 'wireless_experiment_iperf')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:utils:wlanconfig", :id => 'client_wlanconfig') do |app|
    app.setProperty('wlan', 'wlan0')
    app.setProperty('mode', 'adhoc')
    app.setProperty('type', 'g')
    app.setProperty('channel', 13)
    app.setProperty('essid', 'omf_we')
    app.setProperty('ip_address', property.iperf_client_address)
    app.setProperty('duration', (property.runtime + 20))
  end
end

onEvent(:ALL_UP_AND_INSTALLED) do |event|
  info "Running tutorial 1: Wireless experiment..."
  wait 5
  info "Configuring wireless network between nodes..."
  group("Server").startApplication('server_wlanconfig')
  wait 5
  group("Client").startApplication('client_wlanconfig')
  wait 5
  info "Starting iperf server..."
  group("Server").startApplication('iperf_server')
  wait 5
  info "Starting iperf client..."
  group("Client").startApplication('iperf_client')
  info "Iperf server and client started..."
  wait property.runtime
  info "Stopping iperf server and client..."
  wait 5
  allGroups.stopApplications
  info "Iperf server and client stopped..."
  Experiment.done
end

defProperty('server_node','omf.ufrj.icarus9',"ID of server node")
defProperty('client_icarus2_node','omf.ufrj.icarus2',"ID of client icarus2 node")
defProperty('client_icarus28_node','omf.ufrj.icarus28',"ID of client icarus28 node")
defProperty('runtime', 600, "Time in second for the experiment is to run")
defProperty('iperf_server_address', '192.168.129.9', "Iperf server IP address")
defProperty('iperf_client2_address', '192.168.129.2', "Iperf client icarus2 IP address")
defProperty('iperf_client28_address', '192.168.129.28', "Iperf client icarus28 IP address")
defProperty('iperf_2_port', 2002, "Iperf port")
defProperty('iperf_28_port', 2028, "Iperf port")
defProperty('iperf_interval', '1', "Iperf interval")
defProperty('bitrate_type', 'fixed', 'Interface bitrate type. Can be algorith or fixed')
defProperty('bitrate_value', '11', 'Interface bitrate value. Can be a algorithm name or a fixed value')

defProperty('contr', 'omf.ufrj.icarus2', 'WiSHFUL Controller Node')
defProperty('agent', 'omf.ufrj.icarus2, omf.ufrj.icarus28', 'WiSHUL Agent Node')
defProperty('path','/root/git/masquerade/testes/',"Path to WiSHFUL configuration directory")

defApplication('controller') do |app|
  app.description = 'WiSHFUL Simple Controller Program'
  app.path = property.path+'controller.py'
end
defApplication('agent') do |app|
  app.description = 'WiSHFUL Simple Agent Program'
  app.path = property.path+'agent.py'
end

defGroup('Controllers', property.contr ) do |node|
  info "Controller will be on #{property.contr}."
  node.addApplication( "controller" ) do |app|
  end
end

defGroup('Agents', property.agent ) do |node|
  info "Agent will be on #{property.agent}."
  node.addApplication( "agent" ) do |app|
  end
end
# Define the resources group 'Server'
defGroup('Server', property.server_node) do |node|
  node.addApplication("tutorials:iperf", :id => 'iperf_server_2') do |app|
    app.setProperty('server', true)
    app.setProperty('port', property.iperf_2_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'server_2')
    app.setProperty('oml-domain', 'wmp_prio_iperf2')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:iperf", :id => 'iperf_server_28') do |app|
    app.setProperty('server', true)
    app.setProperty('port', property.iperf_28_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'server_28')
    app.setProperty('oml-domain', 'wmp_prio_iperf28')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:utils:wlanconfig", :id => 'server_wlanconfig') do |app|
    app.setProperty('wlan', 'wlan0')
    app.setProperty('mode', 'master')
    app.setProperty('type', 'b')
    app.setProperty('channel', 6)
    app.setProperty('essid', 'omf_wmp_prio')
    app.setProperty('ip_address', property.iperf_server_address)
    app.setProperty('duration', (property.runtime + 20))
  end
end

# Define the resources group 'Client2' (icarus2)
defGroup('Client_2', property.client_icarus2_node) do |node|
  node.addApplication("tutorials:iperf", :id => 'iperf_client') do |app|
    app.setProperty('client', property.iperf_server_address)
    app.setProperty('port', property.iperf_2_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('time', property.runtime)
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'client_2')
    app.setProperty('oml-domain', 'wmp_prio_iperf2')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:utils:wlanconfig", :id => 'client_wlanconfig') do |app|
    app.setProperty('wlan', 'wlan0')
    app.setProperty('mode', 'managed')
    app.setProperty('essid', 'omf_wmp_prio')
    app.setProperty('ip_address', property.iperf_client2_address)
    app.setProperty('bitrate_type', property.bitrate_type)
    app.setProperty('bitrate_value', (property.bitrate_value).to_s)
    app.setProperty('duration', (property.runtime + 20))
  end

  node.addApplication("tutorials:ss", :id => 'ss') do |app|
    app.setProperty('server', "#{property.iperf_server_address}:#{property.iperf_2_port}")
    app.setProperty('duration', property.runtime)
    app.setProperty('oml-id', 'client')
    app.setProperty('oml-domain', 'tcp_wmp_prio_ss28')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end
end

# Define the resources group 'Client28' (icarus28)
defGroup('Client_28', property.client_icarus28_node) do |node|
  node.addApplication("tutorials:iperf", :id => 'iperf_client') do |app|
    app.setProperty('client', property.iperf_server_address)
    app.setProperty('port', property.iperf_28_port)
    app.setProperty('interval', property.iperf_interval)
    app.setProperty('time', property.runtime)
    app.setProperty('reportstyle', 'o')
    app.setProperty('oml-id', 'client_28')
    app.setProperty('oml-domain', 'wmp_prio_iperf28')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end

  node.addApplication("tutorials:utils:wlanconfig", :id => 'client_wlanconfig') do |app|
    app.setProperty('wlan', 'wlan0')
    app.setProperty('mode', 'managed')
    app.setProperty('essid', 'omf_wmp_prio')
    app.setProperty('ip_address', property.iperf_client28_address)
    app.setProperty('bitrate_type', property.bitrate_type)
    app.setProperty('bitrate_value', (property.bitrate_value).to_s)
    app.setProperty('duration', (property.runtime + 20))
  end

  node.addApplication("tutorials:ss", :id => 'ss') do |app|
    app.setProperty('server', "#{property.iperf_server_address}:#{property.iperf_28_port}")
    app.setProperty('duration', property.runtime)
    app.setProperty('oml-id', 'client')
    app.setProperty('oml-domain', 'tcp_wmp_prio_ss28')
    app.setProperty('oml-collect', 'tcp:10.129.11.200:3004')
  end
end
onEvent(:ALL_UP_AND_INSTALLED) do |event|
  info "Running wmp_prio"
  wait 10
  info "Configuring wireless network between nodes..."
  group("Server").startApplication('server_wlanconfig')
  group("Client_2").startApplication('client_wlanconfig')
  group("Client_28").startApplication('client_wlanconfig')
  wait 20
  info "Starting wishful"
  group("Controllers").startApplication('controller')
  group("Agents").startApplication('agent')
  wait 10
  info "Starting iperf server..."
  group("Server").startApplication('iperf_server')
  wait 10
  info "Starting client_28 iperf client..."
  group("Client_28").startApplication('iperf_client')
  group("Client_28").startApplication('ss')
  info "Starting client_2 iperf client..."
  group("Client_2").startApplication('iperf_client')
  group("Client_2").startApplication('ss')

  info "Iperf server and client started..."
  wait property.runtime
  info "Stopping iperf server and client..."
  wait 5
  allGroups.stopApplications
  info "Iperf server and client stopped..."
  Experiment.done
end

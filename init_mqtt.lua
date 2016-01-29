require('network')
require('telnet')
require('mqttclient')

network.init()
network.waitconnect(nil,
   function ()
      network.info()
      telnet.setupTelnetServer()
      print("Started telnet server")
      mqttclient.start()
end)

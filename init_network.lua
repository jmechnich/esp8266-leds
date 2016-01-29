require('network')
require('telnet')
network.init()
network.waitconnect(nil,
   function ()
      network.info()
      telnet.setupTelnetServer()
      print("Started telnet server")
end)

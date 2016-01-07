dofile('util.lc')
require('network')
network.init()
network.waitconnect(nil,
   function ()
      network.info()
      network.setupTelnetServer()
      print("Started telnet server")
      --remote.restartSleepTimer()
   end
)

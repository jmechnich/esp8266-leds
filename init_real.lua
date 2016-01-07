function reset () node.restart() end
function dump (t)
   if t == nil then
      t = _G
   end
   for k,v in pairs(t) do
      print(k,v)
   end
end

require('mpd')
require('remote')
function mkclickfun (name, cmd)
   return function () print(name); remote.blink() end
end
function mklongfun (name, cmd)
   return function () print(name); remote.blink(2) end
end
remote.buttons = {
   [2]={
      mkclickfun("stop", function() mpd:send("stop") end),
      mklongfun("btn1_long", function() end),
   },
   [1]={
      mkclickfun("previous",   function() mpd:send("previous") end),
      mklongfun("btn2_long", function() end),
   },
   [7]={
      mkclickfun("play/pause", function() mpd:toggle() end),
      mklongfun("btn3_long", function() end),
   },
   [6]={
      mkclickfun("next",       function() mpd:send("next") end),
      mklongfun("btn4_long", function() end),
   },
}
mkclickfun = nil
mklongfun = nil
remote.init_led(8)
remote.init_buttons()

require('network')
network.init()
network.waitconnect(
   function () remote.blink(1) end,
   function ()
      remote.blink(2)
      network.info()
      network.setupTelnetServer()
      print("Started telnet server")
      --remote.restartSleepTimer()
   end
)
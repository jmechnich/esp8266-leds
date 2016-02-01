local P =  {}
network = P

P.networks = nil
P.ssid = nil
P.pass = nil

function P.init(force)
   if wifi.sta.status() == 1 and not force then
      P.ssid, P.pass = wifi.sta.getconfig()
      return
   end
   wifi.setmode(wifi.STATION)
   wifi.sleeptype(wifi.NONE_SLEEP)
   if P.ssid ~= nil then
      if P.pass ~= nil then
         print("Manually selected network "..P.ssid)
         return P.connect()
      elseif P.networks ~= nil then
         for k,v in pairs(P.networks) do
            if k == P.ssid then
               P.pass = v
               print("Selected "..P.ssid.." from known networks")
               return P.connect()
            end
         end
      end
   end
   return P.auto()
end

function P.auto()
   wifi.sta.getap(0,function (aptable)
                     for known_ssid, pass in pairs(P.networks) do
                        for avail_ssid in pairs(aptable) do
                           if avail_ssid == known_ssid then
                              P.ssid = known_ssid
                              P.pass = pass
                              print("Autoconnecting to "..P.ssid)
                              return P.connect()
                           end
                        end
                     end
   end)
end

function P.connect(ssid,pass)
   if ssid ~= nil then P.ssid = ssid end
   if pass ~= nil then P.pass = pass end
   if P.ssid == nil or P.pass == nil then
      print("SSID and/or password not set")
      return
   end
   print("Connecting to "..P.ssid)
   return wifi.sta.config(P.ssid,P.pass)
end

function P.waitconnect( waitfun, connfun, timeoutfun)
   local maxtry = 10
   local try = 0
   tmr.alarm(0, 1000, tmr.ALARM_AUTO, function()
                if wifi.sta.getip() == nil then
                   try = try + 1
                   if try == maxtry then
                      if timeoutfun == nil then
                         print("Connection timeout")
                      else
                         timeoutfun()
                      end
                      maxtry = nil
                      try = nil
                      tmr.unregister(0)
                      return
                   end
                   if waitfun == nil then
                      print("Connecting to AP...")
                   else
                      waitfun()
                   end
                else
                   maxtry = nil
                   try = nil
                   if connfun == nil then
                      print('IP: ',wifi.sta.getip())
                   else
                      connfun()
                   end
                   tmr.unregister(0)
                end
   end)
end

function P.info()
   local ssid, password, bssid_set, bssid=wifi.sta.getconfig()
   local ip, nm, gw = wifi.sta.getip()
   local mac = wifi.sta.getmac()
   print()
   print("Address : ",ip)
   print("Netmask : ",nm)
   print("Gateway : ",gw)
   print("MAC     : ",mac)
   print("SSID    : ",ssid)
   print("BSSID   : ",bssid)
end

return network

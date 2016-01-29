local P =  {}
network = P

P.networks = {}
P.ssid = nil
P.pass = nil

function P.init(ssid,pass)
   wifi.setmode(wifi.STATION)
   wifi.sleeptype(wifi.NONE_SLEEP)
   if ssid == nil then
      if wifi.sta.getip() ~= nil then
         return
      end
      return P.auto()
   end
   P.ssid = ssid
   if pass ~= nil then
      P.pass = pass
      print("Manually selected network "..P.ssid)
      return P.connect()
   end

   for k,v in pairs(P.networks) do
      if k == P.ssid then
         P.pass = v
         print("Selected "..P.ssid.." from known networks")
         return P.connect()
      end
   end
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

function P.connect()
   if P.ssid == nil or P.pass == nil then
      print("SSID and/or password not set")
      return
   end
   print("Connecting to "..P.ssid)
   return wifi.sta.config(P.ssid,P.pass)
end

function P.waitconnect( waitfun, connfun)
   tmr.alarm(0, 1000, 1, function()
                if wifi.sta.getip() == nil then
                   if waitfun == nil then
                      print("Connecting to AP...")
                   else
                      waitfun()
                   end
                else
                   if connfun == nil then
                      print('IP: ',wifi.sta.getip())
                   else
                      connfun()
                   end
                   tmr.stop(0)
                end
   end)
end

function P.info()
   local ssid, password, bssid_set, bssid=wifi.sta.getconfig()
   local ip, nm, gw = wifi.sta.getip()
   local mac = wifi.sta.getmac()
   print("\nAddress : "..ip..
            "\nNetmask : "..nm..
            "\nGateway : "..gw..
            "\nMAC     : "..mac..
            "\nSSID    : "..ssid..
            "\nBSSID   : "..bssid.."\n")
end

return network

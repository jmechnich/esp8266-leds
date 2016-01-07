local P =  {}
network = P

P.networks = {}
P.ssid = nil
P.pass = nil

function P.init(ssid,pass)
   wifi.setmode(wifi.STATION)
   if ssid == nil then
      return P.auto()
   end
   P.ssid = ssid
   if pass ~= nil then
      P.pass = pass
      return P.connect()
   end

   for k,v in pairs(P.networks) do
      if k == P.ssid then
         P.pass = v
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
                              return P.connect()
                           end
                        end
                     end
   end)
end

function P.connect()
   if P.ssid == nil or P.pass == nil then
      return
   end
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

function P.setupTelnetServer()
    local inUse = false
    local function listenFun(sock)
        if inUse then
            sock:send("Already in use.\n")
            sock:close()
            return
        end
        inUse = true

        local function s_output(str)
            if(sock ~=nil) then
                sock:send(str)
            end
        end

        node.output(s_output, 0)

        sock:on("receive",function(sock, input)
                node.input(input)
            end)

        sock:on("disconnection",function(sock)
                node.output(nil)
                inUse = false
            end)

        sock:send("Welcome to NodeMCU world.\n> ")
    end

    local telnetServer = net.createServer(net.TCP, 180)
    telnetServer:listen(23, listenFun)
end

function P.info()
   local ssid, password, bssid_set, bssid=wifi.sta.getconfig()
   print("\nCurrent Station configuration:\nSSID : "..ssid
   .."\nPassword  : "..password
   .."\nBSSID_set  : "..bssid_set
   .."\nBSSID: "..bssid.."\n")
end

return network

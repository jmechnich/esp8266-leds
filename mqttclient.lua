local P = {}
mqttclient = P

P.name = "huzzah"
P.pin  = 1

local function subscribe(conn)
   t = P.name.."/in/#"
   conn:subscribe(t,0, function(conn)
                     print("Subscribed successfully to '"..t.."'")
   end)
end

function P.start()
   if P.host == nil then
      print( "mqttclient: Set hostname first")
      return
   end
   P.client = mqtt.Client(P.name, 120, P.user, P.pass)
   P.client:on("connect", function(con) print("Reconnected to "..P.host); subscribe(conn) end)
   P.client:lwt("/lwt", "offline", 0, 0)
   P.client:on("offline", function(con) print ("Disconnected from "..P.host) end)
   P.client:on("message", function(conn, topic, data)
                  if data == nil then return end
                  if topic == P.name.."/in/leddata" then
                     ws2812.writergb(P.pin,data)
                  elseif topic == P.name.."/in/cmd" then
                     loadstring(data)()
                  else
                     print("Unhandled topic '"..topic.."'")
                  end
   end)
   print("Connecting to "..P.host)
   P.client:connect(P.host, 1883, 0, function(conn)
                       subscribe(conn)
                       print("Connected to "..P.host) end)
end

function P.ack()
   P.client:publish(P.name.."/out/ack","0",0,0)
end

function P.publish(s,topic)
   s = s or "hello"
   topic = topic or "info"
   P.client:publish(P.name.."/out/"..topic,s,0,0, function(conn) print("Message sent") end)
end

function P.stop()
   print("Closing connection to "..P.host)
   P.client:close()
end

return mqttclient

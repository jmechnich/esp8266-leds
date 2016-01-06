local P = {}
mpd = P
P.__index = P

P.host = "localhost"
P.port = 6600

local function printPair(str)
   col  = str:find(":")
   if col ~= nil then
      print( str:sub(1,col-1)..": "..str:sub(col+2))
      return true
   end
   return false
end

function P.send (self,msg,parseFunc)
   if msg  == nil then msg = "status" end
   if parseFunc == nil then parseFunc = printPair end
   local sock = net.createConnection( net.TCP, 0)
   local status = -1
   local function parseReply(sck,str,parseFunc)
      local i = str:find("OK MPD")
      if i == 1 then
         status = 0
      else
         if status < 0 then
            print("Error: "..str)
            return
         end
         local idx = 0
         while true do
            tmr.wdclr()
            local last = str:find("\n",idx+1)
            if last == nil then return end
            local handled = false
            if parseFunc ~= nil then
               handled = parseFunc(str:sub(idx+1, last-1))
            end
            if handled then
               status = 0
            else
               if str:find("OK",idx+1) == idx+1 then
                  status = 0
               elseif str:find("ACK",idx+1) == idx+1 then
                  status = 1
               else
                  status = 2
               end
               if status == 0 then
                  sck:close()
                  return
               else
                  print( status.." "..str:sub(idx+1,last-1))
               end
            end
            idx = last
         end
      end
   end
   sock:on("receive", function(sck, c) parseReply(sck,c,parseFunc) end )
   sock:on("connection", function(sck) sock:send(msg.."\r\n") end)
   sock:connect(self.port,self.host)
end

function P.toggle (self)
   local function togglePlayback (str)
      local col = str:find(":")
      if col ~= nil then
         if str:sub(1,col-1) == "state" then
            local val = str:sub(col+2)
            if val == "stop" or val == "pause" then
               P:send("play")
            else
               P:send("pause")
            end
         end
         return true
      end
      return false
   end
   P:send("status",togglePlayback)
end

return mpd

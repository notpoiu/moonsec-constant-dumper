import re, requests

def dump_constants(script_data):
  match = re.search(r';local e=\w+\(\w+\((\w+)\)\);return e\(\.\.\.\);', script_data)
  if match:
      variable_name = match.group(1)
  else:
      print("Pattern not found.")
      return
  
  print("Variable name: " + variable_name)
  
  script_data = script_data.replace(";return e(...)",f";internal_dump_constants({variable_name});return e(...)")
  dump_constants_script = r"""local function internal_dump_constants(node, tablename, spaces)
  if type(node) == "table" then
      local cache, stack, output = {},{},{}
      local depth = 1
      local space
      if spaces == true or nil then
          space = "\n"
      elseif spaces == nil then
          space = "\n"
      else
          space = ""
      end
      local output_str = "{"..space
      while true do
          local size = 0
          for k,v in pairs(node) do
              size = size + 1
          end
          local cur_index = 1
          for k,v in pairs(node) do
              if (cache[node] == nil) or (cur_index >= cache[node]) then
                  if (string.find(output_str,"}",output_str:len())) then
                      output_str = output_str .. ","..space
                  elseif not (string.find(output_str,space,output_str:len())) then
                      output_str = output_str .. space
                  end
                  table.insert(output,output_str)
                  output_str = ""
                  local key
                  if (type(k) == "number" or type(k) == "boolean") then
                      key = "["..tostring(k).."]"
                  else
                      key = "[\""..tostring(k).."\"]"
                  end

                  if (type(v) == "number" or type(v) == "boolean") then
                      output_str = output_str .. string.rep('\t',depth) .. key .. " = "..tostring(v)
                  elseif (type(v) == "table") then
                      output_str = output_str .. string.rep('\t',depth) .. key .. " = {"..space
                      table.insert(stack,node)
                      table.insert(stack,v)
                      cache[node] = cur_index+1
                      break
                  else
                      output_str = output_str .. string.rep('\t',depth) .. key .. " = \""..tostring(v).."\""
                  end

                  if (cur_index == size) then
                      output_str = output_str .. space .. string.rep('\t',depth-1) .. "}"
                  else
                      output_str = output_str .. ","
                  end
              else
                  if (cur_index == size) then
                      output_str = output_str .. space .. string.rep('\t',depth-1) .. "}"
                  end
              end

              cur_index = cur_index + 1
          end
          if (size == 0) then
              output_str = output_str .. space .. string.rep('\t',depth-1) .. "}"
          end
          if (#stack > 0) then
              node = stack[#stack]
              stack[#stack] = nil
              depth = cache[node] == nil and depth + 1 or depth - 1
          else
              break
          end
      end
      table.insert(output,output_str)
      output_str = table.concat(output)
      if spaces == false then
          output_str = output_str:gsub("    ", "")
          task.wait()
          output_str = output_str:gsub(" ", "")
      end
      if tablename == nil then
          print("local table = " .. output_str)
      else
          print("local "..tostring(tablename).." = " .. output_str)
      end
  else
      print(node)
  end
end
"""

  script_data = f"""-- upio's moonsec dumper
{dump_constants_script}

pcall(function() {script_data} end)
"""

  with open("output_script.lua", "w", encoding="utf-8") as f:
    f.write(script_data)
  
  print("Execute the output_script.lua in roblox studio in order to dump constants")
  print("--------------------------------")

print("MoonSec Constant Dumper by upio")
print("--------------------------------")
print("Type 1 to input path to script")
print("Type 2 to input URL to script")
print("--------------------------------")

choice = input("Input choice: ")

if choice == "1":
  print("Default path is /script.lua")
  path = input("Input path to script (enter for default): ")

  if path.strip() == "":
    path = "/script.lua"
  
  with open(path, "r", encoding="utf-8") as f:
    script_data = f.read()

  dump_constants(script_data)
elif choice == "2":
  url = input("Input URL to script: ")

  script_data = requests.get(url).text

  dump_constants(script_data)
else:
  print("Invalid choice!")

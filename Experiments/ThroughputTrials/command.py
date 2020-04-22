from subprocess import Popen


MOCK = False

def run_command(command, user="", host=""):
  """
  timeout = 0 to wait forever
  return proc handle
  """
  # test
  prefix = ""
  if (len(host)):
    prefix = f"{user}@" if len(user) > 0 else ""
    command = command.replace('"', '\\"')
    command = f'ssh {prefix}{host} "{command}"'


  global MOCK
  if(MOCK):
    print("would run:", command)
    return Popen("echo")

  print(command)
  proc = Popen(command, shell=True)
  return proc
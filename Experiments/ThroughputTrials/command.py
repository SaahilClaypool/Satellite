from subprocess import Popen, DEVNULL, STDOUT


MOCK = False

COMMANDS = []

def run_command(command, host="", wait_remote=False):
  """
  timeout = 0 to wait forever
  return proc handle
  """
  prefix = ""
  if (len(host)):
    command = f"screen -d -m {command}"
    command = command.replace('"', '\\"')
    command = f'ssh {prefix}{host} "{command}"'

  stdout = DEVNULL

  global MOCK
  if(MOCK):
    print("would run:", command)
    return Popen("echo", stderr=stdout)

  print(command)

  global COMMANDS
  COMMANDS.append(command)

  proc = Popen(command, shell=True, stdout=stdout)
  return proc

def dump():
  global COMMANDS
  print('\n-----------------ALL COMMANDS----------------')

  for c in COMMANDS:
    print(c)

  print('\n-----------------END COMMANDS----------------')

def clear():
  global COMMANDS
  COMMANDS.clear()
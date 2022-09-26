import math


class FileStat:
  def __init__(self, cwd: str, entry: bytearray):
    self.cwd = cwd
    self.entry = entry
    fields = entry.decode("utf-8", "ignore").split()
    if len(fields) == 4:
      self.name = fields[0]
      self.type = int(fields[1])
      self.id = int(fields[2])
      self.size = int(fields[3])
      self.blocks = math.ceil(self.size / 512)

  def __repr__(self):
    return "FileStat<cwd=/{} name={} type={} id={} size={} blocks={}>".format(
      self.cwd,
      self.name,
      self.type,
      self.id,
      self.size,
      self.blocks
    )

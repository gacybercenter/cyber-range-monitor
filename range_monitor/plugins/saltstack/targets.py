class SaltTarget:
  def __init__(self, name, function, arguments, target_type, user, start_time):
    self.name = name
    self.function = function
    self.arguments = arguments
    self.target_type = target_type
    self.user = user
    self.start_time = start_time
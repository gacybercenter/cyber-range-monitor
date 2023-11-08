INSERT INTO user (username, password)
VALUES
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO user_permissions (user_id, permission)
VALUES
  (2, 'user');

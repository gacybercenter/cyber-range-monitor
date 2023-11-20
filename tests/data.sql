INSERT INTO user (created, username, password, permission)
VALUES
  (CURRENT_TIMESTAMP,
  'other',
  'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79',
  'user');

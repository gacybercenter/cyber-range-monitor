DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_permissions;
DROP TABLE IF EXISTS guacamole;
DROP TABLE IF EXISTS openstack;
DROP TABLE IF EXISTS saltstack;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  permission TEXT NOT NULL,
  FOREIGN KEY (permission) REFERENCES user_permissions (permission)
);

INSERT INTO user (created, username, password, permission)
VALUES
  (CURRENT_TIMESTAMP,
  'Administrator',
  'scrypt:32768:8:1$OZrgrecSOwvEYxBR$b7b5fc887dc6a227c8eb35e22c602e5a62f9305d8458a898bf42a920b84e03b282d8187410d5ad989af71d1120c7b5213466afb42d1a133100101ea06a02da1e',
  'admin');

CREATE TABLE user_permissions (
  id INTEGER PRIMARY KEY,
  permission TEXT NOT NULL
);

INSERT INTO user_permissions (id, permission)
VALUES
  (1, 'admin'),
  (2, 'user'),
  (3, 'read_only');

CREATE TABLE guacamole (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    datasource TEXT NOT NULL,
    enabled BOOLEAN NOT NULL
);

INSERT INTO guacamole (endpoint, username, password, datasource, enabled)
VALUES
  ("http://localhost:8080/guacamole/",
  'Administrator',
  'Administrator',
  'mysql',
  1);

CREATE TABLE openstack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auth_url TEXT,
    project_name TEXT,
    username TEXT,
    password TEXT,
    user_domain_name TEXT,
    project_domain_name TEXT,
    region_name TEXT,
    identity_api_version TEXT
);

CREATE TABLE saltstack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    username TEXT,
    password TEXT,
    datasource TEXT
);


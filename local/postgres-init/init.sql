DROP DATABASE IF EXISTS blockout_scraper;
DROP USER IF EXISTS 'blockout_scraper_admin'@'localhost';
CREATE database blockout_scraper;
CREATE USER IF NOT EXISTS 'blockout_scraper_admin'@'localhost' IDENTIFIED BY 'admin';
GRANT ALL PRIVILEGES ON blockout_scraper.* TO 'blockout_scraper_admin'@'localhost';
FLUSH PRIVILEGES;
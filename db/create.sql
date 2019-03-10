DROP TABLE IF EXISTS `question`;
CREATE TABLE `question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text,
  `askedby` varchar(255) DEFAULT NULL,
  `edited` text,
  `deleted` int(11) NOT NULL DEFAULT '0',
  `answered` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `ip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`)
);

DROP TABLE IF EXISTS `votes`;
CREATE TABLE `votes` (
  `uid` int(11) DEFAULT NULL,
  `question` int(11) DEFAULT NULL,
  `vote` int(11) DEFAULT NULL,
  KEY `vc` (`question`),
  KEY `vu` (`uid`)
);

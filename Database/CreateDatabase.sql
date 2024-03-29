CREATE DATABASE  IF NOT EXISTS `sgmt` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `sgmt`;

--
-- Table structure for table `BundledGames`
--

DROP TABLE IF EXISTS `BundledGames`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `BundledGames` (
  `AppId` varchar(16) DEFAULT NULL,
  `PackageId` varchar(16) DEFAULT NULL,
  `GameName` varchar(128) DEFAULT NULL,
  `WasBundled` tinyint(1) DEFAULT NULL,
  `WasFree` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Games`
--

DROP TABLE IF EXISTS `Games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Games` (
  `Name` varchar(128) NOT NULL,
  `LinkURL` varchar(256) DEFAULT NULL,
  `Value` smallint(4) DEFAULT '0',
  `Score` tinyint(3) DEFAULT '0',
  `NumOfReviews` mediumint(7) DEFAULT '0',
  PRIMARY KEY (`Name`),
  UNIQUE KEY `GameName_UNIQUE` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Giveaways`
--

DROP TABLE IF EXISTS `Giveaways`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Giveaways` (
  `GiveawayID` varchar(32) NOT NULL,
  `LinkURL` varchar(192) DEFAULT NULL,
  `Creator` varchar(32) DEFAULT NULL,
  `GameName` varchar(128) DEFAULT NULL,
  `Entries` mediumtext,
  `Groups` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`GiveawayID`),
  UNIQUE KEY `GiveawayID_UNIQUE` (`GiveawayID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Groups`
--

DROP TABLE IF EXISTS `Groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Groups` (
  `GroupID` varchar(32) NOT NULL,
  `Users` mediumtext,
  `Giveaways` mediumtext,
  `Name` varchar(128) DEFAULT NULL,
  `Webpage` varchar(192) DEFAULT NULL,
  `Cookies` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`GroupID`),
  UNIQUE KEY `GroupID_UNIQUE` (`GroupID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Users` (
  `UserName` varchar(32) NOT NULL,
  `SteamId` varchar(32) DEFAULT NULL,
  `SteamUserName` varchar(64) DEFAULT NULL,
  `CreationTime` datetime DEFAULT NULL,
  PRIMARY KEY (`UserName`),
  UNIQUE KEY `UserName_UNIQUE` (`UserName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

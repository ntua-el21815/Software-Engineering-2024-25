CREATE DATABASE `toll management system` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `toll management system`;

CREATE TABLE `Toll_Operator` (
  `OpID` varchar(255) NOT NULL,
  `Name` varchar(255) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`OpID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Tag` (
  `tag_ID` int NOT NULL AUTO_INCREMENT,
  `tagRef` varchar(255) NOT NULL,
  `OpID` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`tag_ID`),
  KEY `Toll_OperatorOpID` (`OpID`),
  CONSTRAINT `tag_ibfk_1` FOREIGN KEY (`OpID`) REFERENCES `Toll_Operator` (`OpID`)
) ENGINE=InnoDB AUTO_INCREMENT=1339 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Debt` (
  `Debt_ID` int NOT NULL AUTO_INCREMENT,
  `Operator_ID_1` varchar(255) DEFAULT NULL,
  `Operator_ID_2` varchar(255) DEFAULT NULL,
  `Nominal_Debt` decimal(10,2) DEFAULT NULL,
  `Date` date NOT NULL,
  `Status` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Debt_ID`),
  KEY `Operator_ID_1` (`Operator_ID_1`),
  KEY `Operator_ID_2` (`Operator_ID_2`),
  CONSTRAINT `debt_ibfk_1` FOREIGN KEY (`Operator_ID_1`) REFERENCES `Toll_Operator` (`OpID`),
  CONSTRAINT `debt_ibfk_2` FOREIGN KEY (`Operator_ID_2`) REFERENCES `Toll_Operator` (`OpID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Toll_Station` (
  `TollID` varchar(255) NOT NULL,
  `OpID` varchar(255) DEFAULT NULL,
  `Name` varchar(255) NOT NULL,
  `Locality` varchar(255) DEFAULT NULL,
  `Road` varchar(255) DEFAULT NULL,
  `Lat` decimal(9,6) DEFAULT NULL,
  `Long` decimal(9,6) DEFAULT NULL,
  `PM` varchar(10) DEFAULT NULL,
  `Price1` decimal(10,2) DEFAULT NULL,
  `Price2` decimal(10,2) DEFAULT NULL,
  `Price3` decimal(10,2) DEFAULT NULL,
  `Price4` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`TollID`),
  KEY `Toll_OperatorOpID` (`OpID`),
  CONSTRAINT `Toll_Station_ibfk_1` FOREIGN KEY (`OpID`) REFERENCES `Toll_Operator` (`OpID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Pass` (
  `passID` int NOT NULL AUTO_INCREMENT,
  `tag_ID` int DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  `charge` decimal(10,2) NOT NULL,
  `TollID` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`passID`),
  KEY `TollID` (`TollID`),
  KEY `tag_ID` (`tag_ID`,`timestamp`),
  KEY `passID` (`passID`,`charge`),
  CONSTRAINT `pass_ibfk_1` FOREIGN KEY (`tag_ID`) REFERENCES `Tag` (`tag_ID`),
  CONSTRAINT `pass_ibfk_2` FOREIGN KEY (`TollID`) REFERENCES `Toll_Station` (`TollID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `Settlement` (
  `Settlement_ID` int NOT NULL AUTO_INCREMENT,
  `Operator_ID_1` varchar(255) DEFAULT NULL,
  `Operator_ID_2` varchar(255) DEFAULT NULL,
  `Amount` decimal(10,2) DEFAULT NULL,
  `Date` date NOT NULL,
  PRIMARY KEY (`Settlement_ID`),
  KEY `Operator_ID_1` (`Operator_ID_1`),
  KEY `Operator_ID_2` (`Operator_ID_2`),
  CONSTRAINT `settlement_ibfk_1` FOREIGN KEY (`Operator_ID_1`) REFERENCES `Toll_Operator` (`OpID`),
  CONSTRAINT `settlement_ibfk_2` FOREIGN KEY (`Operator_ID_2`) REFERENCES `Toll_Operator` (`OpID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

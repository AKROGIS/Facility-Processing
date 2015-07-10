USE [akr_facility]
GO

/****** Object:  View [gis].[Building_Photo_Points]    Script Date: 7/9/2015 6:17:17 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [gis].[Building_Photo_Points] AS SELECT P.OBJECTID
           ,P.[Unit]
		   ,P.[Filename]
		   ,P.PhotoDate
		   ,CONCAT('http://akrgis.nps.gov/apps/bldgs/photos/web/'
		           ,P.[Unit], '/', P.[Filename]) AS FilePath
	   	   ,D.Common_Name
		   ,L.FMSS_ID
		   ,L.Park_ID
		   ,B.[Is_Sensitive]
		   ,B.Building_ID
		   ,B.[SHAPE]
	  FROM [akr_facility].[gis].[PHOTOS] AS P
	  JOIN [akr_facility].[gis].[BUILDING_LINK] AS L
	    ON P.Location_Id = L.FMSS_ID
	  JOIN [akr_facility].[gis].[BUILDING_POINT] AS B
	    ON L.Building_ID = B.Building_ID
	  JOIN [akr_facility].[gis].[BUILDING] AS D
	    ON L.Building_ID = D.Building_ID
	 WHERE B.Point_Type = 0
	   AND (P.Asset_Code = '4300' OR P.Asset_Code = '4100')
GO



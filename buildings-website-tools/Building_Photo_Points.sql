USE [akr_facility]
GO

/****** Object:  View [gis].[Building_Photo_Points]    Script Date: 7/27/2015 11:28:19 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [gis].[Building_Photo_Points] AS SELECT P.OBJECTID
           ,P.[Unit]
		   ,P.[Filename]
		   ,P.PhotoDate
		   ,CONCAT('http://akrgis.nps.gov/fmss/photos/web/'
		           ,P.[Unit], '/', P.[Filename]) AS FilePath
	   	   ,D.Common_Name
		   ,L.FMSS_ID
		   ,L.Park_ID
		   ,B.[Is_Sensitive]
		   ,B.Building_ID
		   ,B.[SHAPE]
	  FROM [akr_facility].[gis].[Photos_evw] AS P
	  JOIN [akr_facility].[gis].[Building_Link_evw] AS L
	    ON P.Location_Id = L.FMSS_ID
	  JOIN [akr_facility].[gis].[Building_Point_evw] AS B
	    ON L.Building_ID = B.Building_ID
	  JOIN [akr_facility].[gis].[Building_evw] AS D
	    ON L.Building_ID = D.Building_ID
	 WHERE B.Point_Type = 0
	   AND (P.Asset_Code = '4300' OR P.Asset_Code = '4100')

GO



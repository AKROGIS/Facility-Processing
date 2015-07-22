USE [akr_facility]
GO

/****** Object:  View [gis].[Existing_FMSS_Buildings_For_Website]    Script Date: 7/22/2015 8:45:45 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO




CREATE VIEW [gis].[Existing_FMSS_Buildings_For_Website] AS

	 SELECT P.Shape.Lat AS Latitude,  P.Shape.Long AS Longitude, L.FMSS_ID as FMSS_Id, F.[Description] AS [Desc],
	        COALESCE(FORMAT(F.CRV, 'C', 'en-us'), 'unknown') AS Cost,
			COALESCE(FORMAT(F.Qty, '0,0 Sq Ft', 'en-us'), 'unknown') AS Size, F.[Status] AS [Status], 
			COALESCE(F.YearBlt, 'unknown') AS [Year], COALESCE(F.Occupant, 'unknown') AS Occupant, 
			B.Common_Name AS [Name], L.Park_ID AS Park_Id
       FROM gis.Building_Point_evw as P
  LEFT JOIN gis.Building_evw as B
         ON B.Building_ID = P.Building_ID
  LEFT JOIN gis.BUILDING_LINK_evw as L
         ON L.Building_ID = P.Building_ID
  LEFT JOIN gis.FMSSEXPORT as F
         ON F.Location = L.FMSS_ID
	  WHERE P.Point_Type = 0 AND P.Is_Extant = 'Y' AND L.FMSS_ID IS NOT NULL


GO



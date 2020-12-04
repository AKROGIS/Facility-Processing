USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Duplicates_All]    Script Date: 7/14/2015 2:40:01 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



ALTER VIEW [gis].[Building_QC_Duplicates_All] AS --Duplicates
-- duplicate Building IDs
SELECT 'Building_ID in Building' AS Duplicate, Building_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_evw] group by Building_ID having count(*) > 1
UNION
SELECT 'Building_ID in Building_Link' AS Duplicate, Building_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Link_evw] group by Building_ID having count(*) > 1
UNION
SELECT 'Building_ID in Extant Building_Point' AS Duplicate, Building_ID AS ID, Point_Type as Geom_Type 
  FROM [akr_facility].[gis].[Building_Point_evw] where Is_Extant = 'Y' group by Building_ID, Point_Type having count(*) > 1 
UNION
SELECT 'Building_ID in Extant Building_Polygon' AS Duplicate, Building_ID AS ID, 1000 + Polygon_Type as Geom_Type
  FROM [akr_facility].[gis].[Building_Polygon_evw] where Is_Extant = 'Y' group by Building_ID, Polygon_Type having count(*) > 1 
UNION
-- Duplicate Geometry IDs
SELECT 'GeometryID in Building_Point' AS Duplicate, GeometryID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Point_evw] group by GeometryID having count(*) > 1 
UNION
SELECT 'GeometryID in Building_Polygon' AS Duplicate, GeometryID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Polygon_evw] group by GeometryID having count(*) > 1 
UNION
-- Duplicate FMSS_ID
SELECT 'FMSS_ID in Building_Link' AS Duplicate, FMSS_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Link_evw] WHERE FMSS_ID IS NOT NULL group by FMSS_ID having count(*) > 1
UNION
SELECT 'Location ID in FMSSEXPORT' AS Duplicate, Location AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[FMSSEXPORT] group by Location having count(*) > 1
UNION
-- Duplicate FMSS_ID
SELECT 'LCS_ID in Building_Link' AS Duplicate, LCS_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Link_evw] WHERE LCS_ID IS NOT NULL group by LCS_ID having count(*) > 1
UNION
SELECT 'LCS_ID in LCSEXPORT' AS Duplicate, LCS_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[LCSEXPORT] group by LCS_ID having count(*) > 1
UNION
-- Duplicate ASMIS_ID
SELECT 'ASMIS_ID in Building_Link' AS Duplicate, ASMIS_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Link_evw] WHERE ASMIS_ID IS NOT NULL group by ASMIS_ID having count(*) > 1
UNION
-- Duplicate Park_ID
SELECT 'Park_ID in Building_Link' AS Duplicate, Park_ID AS ID, NULL as Geom_Type
  FROM [akr_facility].[gis].[Building_Link_evw] WHERE Park_ID IS NOT NULL group by Park_ID having count(*) > 1


GO



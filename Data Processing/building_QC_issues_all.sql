USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Issues_All]    Script Date: 7/10/2015 10:18:22 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [gis].[Building_QC_Issues_All] AS 
   select 'Buildings without a Building Center' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POINT as P
       on B.Building_ID = P.Building_ID AND P.Point_Type = 0
    where P.Building_ID IS NULL
UNION
   select 'Building_Point without a Building' as Problem, P.Building_ID as ID
     from akr_facility.gis.BUILDING_POINT as P
left join akr_facility.gis.BUILDING as B
       on B.Building_ID = P.Building_ID
    where B.Building_ID IS NULL
UNION
   select 'Building_Polygon without a Building' as Problem, P.Building_ID as ID
     from akr_facility.gis.BUILDING_POLYGON as P
left join akr_facility.gis.BUILDING as B
       on B.Building_ID = P.Building_ID
    where B.Building_ID IS NULL
UNION
   select 'Building_Link without a Building' as Problem, P.Building_ID as ID
     from akr_facility.gis.BUILDING_LINK as P
left join akr_facility.gis.BUILDING as B
       on B.Building_ID = P.Building_ID
    where B.Building_ID IS NULL
UNION
   select 'Building with Unit Code without a Building_Link' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_LINK as P
       on B.Building_ID = P.Building_ID 
    where P.Building_ID IS NULL and B.Unit_Code IS NOT NULL
UNION
   select 'FMSS_ID in Building_Link without a FMSS Record' as Problem, L.FMSS_ID as ID
     from akr_facility.gis.BUILDING_LINK as L
left join akr_facility.gis.FMSSEXPORT as F
       on L.FMSS_ID = F.Location
    where F.Location IS NULL
UNION
   select 'Operating FMSS_ID in FMSSExport without Building_Link' as Problem, F.Location as ID
     from akr_facility.gis.FMSSEXPORT as F
left join akr_facility.gis.BUILDING_LINK as L
       on L.FMSS_ID = F.Location
    where L.FMSS_ID IS NULL AND F.[Status] = 'OPERATING'
UNION
   select 'LCS_ID in Building_Link without a LCS Record' as Problem, L.LCS_ID as ID
     from akr_facility.gis.BUILDING_LINK as L
left join akr_facility.gis.LCSEXPORT as F
       on L.LCS_ID = F.LCS_ID
    where F.LCS_ID IS NULL AND L.LCS_ID IS NOT NULL
UNION
-- Produces about 250 problems
   select 'LCS_ID in LCSExport without Building_Link' as Problem, F.LCS_ID as ID
     from akr_facility.gis.LCSEXPORT as F
left join akr_facility.gis.BUILDING_LINK as L
       on L.LCS_ID = F.LCS_ID
    where L.LCS_ID IS NULL

--  PHOTOS
UNION
-- Produces about 300 problems
   select 'Buildings with Unit Code without a Photo' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_LINK as L
       on B.Building_ID = L.Building_ID
left join akr_facility.gis.PHOTOS as P
       on L.FMSS_ID = P.Location_Id
    where P.Location_Id IS NULL AND B.Unit_Code IS NOT NULL
UNION
-- Produces about 550 problems
   select 'Buildings with less than 5 photos' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_LINK as L
       on B.Building_ID = L.Building_ID
left join akr_facility.gis.PHOTOS as P
       on L.FMSS_ID = P.Location_Id
	WHERE P.Location_ID IS NOT NULL
 group by B.Building_ID
   having count(*) < 5
UNION
   select 'Buildings with no photo in the last 10 years ' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_LINK as L
       on B.Building_ID = L.Building_ID
left join akr_facility.gis.PHOTOS as P
       on L.FMSS_ID = P.Location_Id
	WHERE P.PhotoDate IS NOT NULL
 group by B.Building_ID
   having max(P.PhotoDate) < dateadd(year, -10, getdate())
UNION 
   select 'Photos of Building without a Location Record Number' as Problem, Unit + '/' + [Filename] as ID
     from akr_facility.gis.PHOTOS
    where Asset_Code = '4100' AND Location_Id IS NULL 
UNION
   select 'Photos of Building without a Building_Link' as Problem, P.Unit + '/' + P.[Filename] as ID
     from akr_facility.gis.PHOTOS AS P
left join akr_facility.gis.BUILDING_LINK as L
       on P.Location_Id = L.FMSS_ID
    where P.Asset_Code = '4100' AND L.FMSS_ID IS NULL


--GPS ISSUES
UNION
-- about 300 problems
   select 'Buildings with unit code without a Building Entrance' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POINT as P
       on B.Building_ID = P.Building_ID AND P.Point_Type = 2
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NULL
UNION
-- about 200 problems
   select 'Buildings with unit code without a Building Perimeter' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POLYGON as P
       on B.Building_ID = P.Building_ID AND P.Polygon_Type = 0
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NULL
UNION
-- about 100 problems
   select 'Buildings with unit code without a GPS Building Entrance' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POINT as P
       on B.Building_ID = P.Building_ID AND P.Point_Type = 2
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NOT NULL AND P.Map_Method <> 'AGPS' AND P.Map_Method <> 'DGPS'
UNION
-- about 600 problems
   select 'Buildings with unit code without a GPS Building Perimeter' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POLYGON as P
       on B.Building_ID = P.Building_ID AND P.Polygon_Type = 0
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NOT NULL AND P.Map_Method <> 'AGPS' AND P.Map_Method <> 'DGPS'
UNION
-- about 300 problems
   select 'Buildings with unit code with a GARMIN Building Entrance' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POINT as P
       on B.Building_ID = P.Building_ID AND P.Point_Type = 2
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NOT NULL AND P.Map_Method = 'AGPS'
UNION
   select 'Buildings with unit code with a GARMIN Building Perimeter' as Problem, B.Building_ID as ID
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_POLYGON as P
       on B.Building_ID = P.Building_ID AND P.Polygon_Type = 0
    where B.Unit_Code IS NOT NULL AND P.Building_ID IS NOT NULL AND P.Map_Method = 'AGPS'


GO



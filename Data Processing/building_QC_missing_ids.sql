USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Missing_Ids]    Script Date: 7/10/2015 10:18:06 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [gis].[Building_QC_Missing_Ids] AS select 'Building without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING where Building_ID IS NULL
union
select 'Building_Link without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING_LINK where Building_ID IS NULL
union
select 'Building_Point without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING_Point where Building_ID IS NULL
union
select 'Building_Point without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING_POLYGON where Building_ID IS NULL
union
select 'Building_Point without a GeometryID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING_POINT where GeometryID IS NULL
union
select 'Building_Polygon without a GeometryID' as Problem, OBJECTID as OID
from akr_facility.gis.BUILDING_POLYGON where GeometryID IS NULL
GO



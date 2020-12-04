USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Missing_Ids]    Script Date: 7/14/2015 2:38:54 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO



ALTER VIEW [gis].[Building_QC_Missing_Ids] AS select 'Building without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_evw where Building_ID IS NULL
union
select 'Building_Link without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_Link_evw where Building_ID IS NULL
union
select 'Building_Point without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_Point_evw where Building_ID IS NULL
union
select 'Building_Polygon without a Building_ID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_Polygon_evw where Building_ID IS NULL
union
select 'Building_Point without a GeometryID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_Point_evw where GeometryID IS NULL
union
select 'Building_Polygon without a GeometryID' as Problem, OBJECTID as OID
from akr_facility.gis.Building_Polygon_evw where GeometryID IS NULL


GO



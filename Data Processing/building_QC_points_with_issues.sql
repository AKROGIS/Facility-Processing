USE [akr_facility]
GO

/****** Object:  View [gis].[Builidng_QC_Points_with_Issues]    Script Date: 7/14/2015 2:42:34 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


ALTER VIEW [gis].[Builidng_QC_Points_with_Issues] AS select b.Unit_Code, b.Building_ID, I.Problem, B.Common_Name, L.FMSS_ID, P.Shape
from akr_facility.gis.building_qc_issues_Fixme as I
join akr_facility.gis.building_point as P
on I.id = P.building_id and P.Point_Type = 0
join akr_facility.gis.building as b
on b.Building_ID = P.Building_ID
left join akr_facility.gis.Building_Link_evw as l
on b.Building_ID = l.Building_ID

GO



USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_No_GIS_Location_for_FMSS_Operating]    Script Date: 7/14/2015 2:34:15 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [gis].[Building_QC_No_GIS_Location_for_FMSS_Operating] AS    select  F.Park, F.Location, F.Description
     from akr_facility.gis.FMSSEXPORT as F
left join akr_facility.gis.Building_Link_evw as L
       on L.FMSS_ID = F.Location
    where L.FMSS_ID IS NULL AND F.[Status] = 'OPERATING' AND F.Asset_Code = 4100

GO



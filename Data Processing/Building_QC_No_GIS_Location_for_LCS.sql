USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_No_GIS_Location_for_LCS]    Script Date: 7/14/2015 2:35:00 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO


CREATE VIEW [gis].[Building_QC_No_GIS_Location_for_LCS] AS    select  F.Park, F.LCS_ID, F.Preferred_Structure_Name
     from akr_facility.gis.LCSEXPORT as F
left join akr_facility.gis.Building_Link_evw as L
       on L.LCS_ID = F.LCS_ID
    where L.LCS_ID IS NULL

GO



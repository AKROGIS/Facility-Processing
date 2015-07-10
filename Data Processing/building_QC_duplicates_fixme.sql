USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Duplicates_Fixme]    Script Date: 7/9/2015 6:15:45 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [gis].[Building_QC_Duplicates_Fixme] AS SELECT D.Duplicate, D.ID, D.[Geom_Type]
  FROM [akr_facility].[gis].[Building_QC_Duplicates_All] as D
  LEFT JOIN [akr_facility].[gis].[Building_QC_Duplicates_Explained] as E
  ON D.Duplicate = E.Duplicate and D.ID = E.ID and (D.[Geom_Type] IS NULL OR D.[Geom_Type] = E.[Geom_Type])
  where E.ID IS NULL
GO



USE [akr_facility]
GO

/****** Object:  View [gis].[Building_QC_Issues_Fixme]    Script Date: 7/10/2015 10:18:49 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [gis].[Building_QC_Issues_Fixme] AS SELECT I.Problem, I.ID
  FROM [akr_facility].[gis].[Building_QC_Issues_All] as I
  LEFT JOIN [akr_facility].[gis].[Building_QC_Issues_Explained] as E
  ON I.Problem = E.Problem and I.ID = E.ID
  where E.ID IS NULL
GO



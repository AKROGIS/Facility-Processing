USE [akr_facility]
GO

/****** Object:  View [gis].[QC_Photo_Problems]    Script Date: 7/21/2015 9:01:26 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE VIEW [gis].[QC_Photo_Problems] AS  select 'Photo not in Database' AS Problem, f.Folder AS Unit, f.[Filename]
  from dbo.Photos_in_filesystem as f
  left join gis.Photos_evw as p
  on f.Folder = p.Unit and f.[Filename] = p.[Filename]
  where p.Filename is null
UNION
  select 'Photo not in Filesystem' AS Problem, p.Unit, p.[Filename]
  from gis.Photos_evw as p
  left join dbo.Photos_in_filesystem as f
  on f.folder = p.Unit and f.[Filename] = p.[Filename]
  where f.[Filename] is null
GO



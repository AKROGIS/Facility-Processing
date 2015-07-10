
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


-- Buildings without entrance
-- Buildings without footprint
-- Entrance is not GPS
-- Entrance is not Trimble
-- Footprint is not GPS
-- Footprint is not Trimble

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
-- Produces about 300 problems
   select 'Buildings with Unit Code without a Photo' as Problem, B.Building_ID as ID, count(*)
     from akr_facility.gis.BUILDING as B
left join akr_facility.gis.BUILDING_LINK as L
       on B.Building_ID = L.Building_ID
left join akr_facility.gis.PHOTOS as P
       on L.FMSS_ID = P.Location_Id
 group by B.Building_ID
   having count(*) < 5
    where P.Location_Id IS NULL AND B.Unit_Code IS NOT NULL
-- Photo without buildings
-- Buildings with less than 5 photos
-- Buildings with photos over 5 years old

select 'Building without a Building_ID' as Problem
from akr_facility.gis.BUILDING where Building_ID IS NULL
union
select 'Building_Link without a Building_ID' as Problem
from akr_facility.gis.BUILDING_LINK where Building_ID IS NULL
union
select 'Building_Point without a Building_ID' as Problem
from akr_facility.gis.BUILDING_Point where Building_ID IS NULL
union
select 'Building_Point without a Building_ID' as Problem
from akr_facility.gis.BUILDING_POLYGON where Building_ID IS NULL
union
select 'Building_Point without a GeometryID' as Problem
from akr_facility.gis.BUILDING_POINT where GeometryID IS NULL
union
select 'Building_Polygon without a GeometryID' as Problem
from akr_facility.gis.BUILDING_POLYGON where GeometryID IS NULL

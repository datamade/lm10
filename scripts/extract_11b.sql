COPY (
  SELECT
    a.file_name,
    ST_Distance(a.wkb_geometry, b.wkb_geometry),
    a.page_num,
    b.text
  FROM
    blocks AS a
  INNER JOIN blocks as b USING (file_name, page_num)
  WHERE
    a.text LIKE '%11.b.%'
    AND b.wkb_geometry |>> a.wkb_geometry
    AND b.wkb_geometry &< a.wkb_geometry
    AND b.wkb_geometry &> a.wkb_geometry
    AND b.blocktype = 'LINE'
  GROUP BY
    a.file_name,
    a.page_num,
    b.text,
    a.wkb_geometry,
    b.wkb_geometry
  ORDER BY
    a.file_name,
    a.page_num,
    ST_Distance(a.wkb_geometry, b.wkb_geometry)
) TO stdout WITH CSV HEADER;

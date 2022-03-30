COPY (
  SELECT
    replace(replace(a.file_name, 'textract_responses/', ''), '.json', '.pdf') as file_name,
    a.page_num + 1 as page_num,
    RANK () OVER (PARTITION BY a.file_name, a.page_num
                  ORDER BY ST_Distance(a.wkb_geometry, b.wkb_geometry)) AS item_order,
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
    AND b.text NOT LIKE '%or expenditure%'
) TO stdout WITH CSV HEADER;

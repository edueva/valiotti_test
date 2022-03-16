-- In case of larger amount of names
-- One should use more sophisticated approaches
-- https://towardsdatascience.com/transpositions-in-sql-c1cf724dfa2a
-- https://www.sqlshack.com/multiple-options-to-transposing-rows-into-columns/
    
SELECT Name,
       avg(CASE
                WHEN Name = 'A' THEN Val
            END) AS 'A',
       avg(CASE
                WHEN Name = 'B' THEN Val
            END) AS 'B',
        avg(CASE
                WHEN Name = 'C' THEN Val
            END) AS 'C',
FROM A
GROUP BY ID;

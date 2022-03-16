SELECT Month_cohort,
       ROUND(100*DayOneRetention/MonthTot, 2) AS DayOneRetention,
       ROUND(100*DayThreeRetention/MonthTot, 2) AS DayThreeRetention,
       ROUND(100*DaySevenRetention/MonthTot, 2) AS DaySevenRetention
FROM
  (SELECT toStartOfMonth(EventDate) AS Month_cohort,
          uniqExact(CASE
                        WHEN TimeDelta = 0 THEN user_id
                    END) AS MonthTot,
          uniqExact(CASE
                        WHEN TimeDelta = 1 THEN user_id
                    END) AS DayOneRetention,
          uniqExact(CASE
                        WHEN TimeDelta = 3 THEN user_id
                    END) AS DayThreeRetention,
          uniqExact(CASE
                        WHEN TimeDelta = 7 THEN user_id
                    END) AS DaySevenRetention
   FROM
     (SELECT l.user_id AS user_id,
             CAST(l.created_at AS Date) AS EventDate,
             r.BirthDate AS BirthDate,
             EventDate - BirthDate AS TimeDelta
      FROM client_session AS l
      LEFT JOIN
        (SELECT user_id, installed_at AS BirthDate,
         FROM user) AS r ON l.user_id = r.user_id
      WHERE BirthDate >= '2020-01-01') AS TEMP
   GROUP BY Month_cohort) AS ret;
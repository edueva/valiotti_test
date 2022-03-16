SELECT city AS city_with_min_population
FROM city_population
WHERE population = (SELECT MIN(population)
                    FROM city_population)
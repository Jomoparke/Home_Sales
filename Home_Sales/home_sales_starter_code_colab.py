# -*- coding: utf-8 -*-
"""Home_Sales_starter_code_colab.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1aJfCCa9xWNtMeZk8xsZHJ8WbQBt0IZdU
"""

import os
# Find the latest version of spark 3.x  from http://www.apache.org/dist/spark/ and enter as the spark version
# For example:
# spark_version = 'spark-3.4.0'
spark_version = 'spark-3.4.3'
os.environ['SPARK_VERSION']=spark_version

# Install Spark and Java
!apt-get update
!apt-get install openjdk-11-jdk-headless -qq > /dev/null
!wget -q http://www.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz
!tar xf $SPARK_VERSION-bin-hadoop3.tgz
!pip install -q findspark

# Set Environment Variables
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["SPARK_HOME"] = f"/content/{spark_version}-bin-hadoop3"

# Start a SparkSession
import findspark
findspark.init()

# Import packages
from pyspark.sql import SparkSession
import time

# Create a SparkSession
spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

# 1. Read in the AWS S3 bucket into a DataFrame.
from pyspark import SparkFiles
url = "https://2u-data-curriculum-team.s3.amazonaws.com/dataviz-classroom/v1.2/22-big-data/home_sales_revised.csv"
spark.sparkContext.addFile(url)
df = spark.read.csv(SparkFiles.get("home_sales_revised.csv"), header=True, inferSchema=True, quote="\"", escape="\"")

# Show DataFrame
df.show()

# 2. Create a temporary view of the DataFrame.
df.createOrReplaceTempView('home_sales')

# 3. What is the average price for a four bedroom house sold per year, rounded to two decimal places?

from pyspark.sql.functions import year, col

df_with_year = df.withColumn("year", year(col("date")))

df_with_year.createOrReplaceTempView("home_sales")

query = """
SELECT
    year,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales
WHERE
    bedrooms = 4
GROUP BY
    year
ORDER BY
    year
"""
result = spark.sql(query)
result.show()

# 4. What is the average price of a home for each year the home was built,
# that have 3 bedrooms and 3 bathrooms, rounded to two decimal places?

df_with_year_built = df.withColumnRenamed("date_built", "year_built")

df_with_year_built.createOrReplaceTempView("home_sales")

query = """
SELECT
    year_built,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales
WHERE
    bedrooms = 3 AND bathrooms = 3
GROUP BY
    year_built
ORDER BY
    year_built
"""

result = spark.sql(query)

result.show()

# 5. What is the average price of a home for each year the home was built,
# that have 3 bedrooms, 3 bathrooms, with two floors,
# and are greater than or equal to 2,000 square feet, rounded to two decimal places?

query = """
SELECT
    year_built,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales
WHERE
    bedrooms = 3
    AND bathrooms = 3
    AND floors = 2
    AND sqft_living >= 2000
GROUP BY
    year_built
ORDER BY
    year_built
"""

# Execute the query
result = spark.sql(query)

# Show the result
result.show()

# 6. What is the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000? Order by descending view rating.
# Although this is a small dataset, determine the run time for this query.
query = """
SELECT
    view,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales
GROUP BY
    view
HAVING
    AVG(price) >= 350000
ORDER BY
    view DESC
"""

start_time = time.time()

result = spark.sql(query)

end_time = time.time()

result.show()

print("--- %s seconds ---" % (time.time() - start_time))

# 7. Cache the the temporary table home_sales.
spark.catalog.cacheTable("home_sales")

# 8. Check if the table is cached.
spark.catalog.isCached('home_sales')

# 9. Using the cached data, run the last query above, that calculates
# the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000.
# Determine the runtime and compare it to the uncached runtime.

query = """
SELECT
    view,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales
GROUP BY
    view
HAVING
    AVG(price) >= 350000
ORDER BY
    view DESC
"""

# Measure the runtime for the query using cached data
start_time = time.time()

# Execute the query
result = spark.sql(query)

# Measure the end time
end_time = time.time()

result.show()

print("--- %s seconds ---" % (time.time() - start_time))

# 10. Partition by the "date_built" field on the formatted parquet home sales data
output_path = "/path/to/output/home_sales_partitioned.parquet"

df_with_year_built.write.partitionBy("year_built").parquet(output_path)

# 11. Read the parquet formatted data.
output_path

# 12. Create a temporary table for the parquet data.
df_parquet = spark.read.parquet(output_path)

df_parquet.createOrReplaceTempView("home_sales_parquet")

# 13. Using the parquet DataFrame, run the last query above, that calculates
# the average price of a home per "view" rating, rounded to two decimal places,
# having an average home price greater than or equal to $350,000.
# Determine the runtime and compare it to the cached runtime.

df_parquet.createOrReplaceTempView("home_sales_parquet")

# Define the query to calculate the average price per view rating
query = """
SELECT
    view,
    ROUND(AVG(price), 2) AS avg_price
FROM
    home_sales_parquet
GROUP BY
    view
HAVING
    AVG(price) >= 350000
ORDER BY
    view DESC
"""

# Measure the runtime for the query using Parquet data
start_time = time.time()

# Execute the query
result = spark.sql(query)

# Measure the end time
end_time = time.time()

result.show()

print("--- %s seconds ---" % (time.time() - start_time))

# 14. Uncache the home_sales temporary table.
spark.catalog.uncacheTable("home_sales")

is_cached = spark.catalog.isCached("home_sales")

is_cached


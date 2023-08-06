import psycopg2
from scrapy.exceptions import DropItem


class PostgreSQLPipeline:

    def __init__(self, postgres_host, postgres_db, postgres_user, postgres_password, postgres_port):
        self.postgres_host = postgres_host
        self.postgres_db = postgres_db
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_port = postgres_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            postgres_host=crawler.settings.get('POSTGRES_HOST'),
            postgres_db=crawler.settings.get('POSTGRES_DB'),
            postgres_user=crawler.settings.get('POSTGRES_USER'),
            postgres_password=crawler.settings.get('POSTGRES_PASSWORD'),
            postgres_port=crawler.settings.get('POSTGRES_PORT'),
        )

    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host=self.postgres_host,
            database=self.postgres_db,
            user=self.postgres_user,
            password=self.postgres_password,
            port=self.postgres_port,
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        # Prepare the data dictionary for insertion
        data = {
            'name': item['name'],
            'linkedin_url': item['linkedin_url'],
            'industry': item['industry'],
            'tagline': item['tagline'],
            'phone': item['phone'],
            'company_url': item['company_url'],
            'founded': item['founded'],
            'linkedin_followers': item['linkedin_followers'],
            'employees': item['employees'],
            'country_code': item['country_code'],
            'geographicArea': item['geographicArea'],
            'postal_code': item['postal_code'],
            'city': item['city'],
            'line1': item['line1'],
            'line2': item['line2'],
        }

        # SQL query to insert data into the table (replace with your own table name)
        insert_query = """
            INSERT INTO linkedin_company
            (name, linkedin_url, industry, tagline, phone, company_url,
            founded, linkedin_followers, employees, country_code, geographicArea,
            postal_code, city, line1, line2)
            VALUES
            (%(name)s, %(linkedin_url)s, %(industry)s, %(tagline)s, %(phone)s,
            %(company_url)s, %(founded)s, %(linkedin_followers)s,
            %(employees)s, %(country_code)s, %(geographicArea)s, %(postal_code)s,
            %(city)s, %(line1)s, %(line2)s)
        """

        try:
            # Execute the INSERT query with the data dictionary
            self.cursor.execute(insert_query, data)
            self.connection.commit()
        except Exception as e:
            # Log any error that occurs during the insertion and drop the item
            spider.logger.error(f"Error inserting data: {e}")
            self.connection.rollback()
            raise DropItem("Failed to insert item into PostgreSQL database")

        return item

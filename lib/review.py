# from __init__ import CURSOR, CONN
# from department import Department
# from employee import Employee


# class Review:

#     # Dictionary of objects saved to the database.
#     all = {}

#     def __init__(self, year, summary, employee_id, id=None):
#         self.id = id
#         self.year = year
#         self.summary = summary
#         self.employee_id = employee_id

#     def __repr__(self):
#         return (
#             f"<Review {self.id}: {self.year}, {self.summary}, "
#             + f"Employee: {self.employee_id}>"
#         )

#     @classmethod
#     def create_table(cls):
#         """ Create a new table to persist the attributes of Review instances """
#         sql = """
#             CREATE TABLE IF NOT EXISTS reviews (
#             id INTEGER PRIMARY KEY,
#             year INT,
#             summary TEXT,
#             employee_id INTEGER,
#             FOREIGN KEY (employee_id) REFERENCES employee(id))
#         """
#         CURSOR.execute(sql)
#         CONN.commit()

#     @classmethod
#     def drop_table(cls):
#         """ Drop the table that persists Review  instances """
#         sql = """
#             DROP TABLE IF EXISTS reviews;
#         """
#         CURSOR.execute(sql)
#         CONN.commit()

#     def save(self):
#         """ Insert a new row with the year, summary, and employee id values of the current Review object.
#         Update object id attribute using the primary key value of new row.
#         Save the object in local dictionary using table row's PK as dictionary key"""
#         pass

#     @classmethod
#     def create(cls, year, summary, employee_id):
#         """ Initialize a new Review instance and save the object to the database. Return the new instance. """
#         pass
   
#     @classmethod
#     def instance_from_db(cls, row):
#         """Return an Review instance having the attribute values from the table row."""
#         # Check the dictionary for  existing instance using the row's primary key
#         pass
   

#     @classmethod
#     def find_by_id(cls, id):
#         """Return a Review instance having the attribute values from the table row."""
#         pass

#     def update(self):
#         """Update the table row corresponding to the current Review instance."""
#         pass

#     def delete(self):
#         """Delete the table row corresponding to the current Review instance,
#         delete the dictionary entry, and reassign id attribute"""
#         pass

#     @classmethod
#     def get_all(cls):
#         """Return a list containing one Review instance per table row"""
#         pass








from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            f"Employee: {self.employee_id}>"
        )

    # ---- Property Methods ----

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Check that the employee exists in the database
        if isinstance(value, int) and Employee.find_by_id(value):
            self._employee_id = value
        else:
            raise ValueError("employee_id must reference a persisted Employee")

    # ---- ORM Methods ----

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances."""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances."""
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """
        Insert a new row with the year, summary, and employee_id values of the current Review object.
        Update the object's id attribute using the primary key value of the new row.
        Save the object in the local dictionary using the table row's PK as key.
        """
        sql = """
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
        CONN.commit()
        self.id = CURSOR.lastrowid
        Review.all[self.id] = self

    @classmethod
    def create(cls, year, summary, employee_id):
        """
        Initialize a new Review instance, save it to the database, and return the new instance.
        """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """
        Return a Review instance having the attribute values from the table row.
        If an instance with that id already exists in the cache, update its attributes.
        """
        review_id = row[0]
        if review_id in cls.all:
            review = cls.all[review_id]
            # Update attributes in case they changed in the DB
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            review = cls(row[1], row[2], row[3], id=review_id)
            cls.all[review_id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """
        Return a Review instance corresponding to the row in the "reviews" table with the given id.
        Return None if no such row exists.
        """
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """
        Update the table row corresponding to the current Review instance.
        """
        if self.id is None:
            raise Exception("Review must be saved before it can be updated.")
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """
        Delete the table row corresponding to the current Review instance,
        remove the instance from the cache, and set the instance's id to None.
        """
        if self.id is None:
            raise Exception("Review is not saved.")
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """
        Return a list containing one Review instance per table row.
        """
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

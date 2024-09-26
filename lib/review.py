from __init__ import CURSOR, CONN

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
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Review instances"""
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Review instances"""
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update a row in the reviews table"""
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            ''', (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            CURSOR.execute('''
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            ''', (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Initialize a new Review instance and save it to the database"""
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance with attributes from the table row"""
        return cls(row[1], row[2], row[3], row[0])

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance with the specified id"""
        CURSOR.execute('SELECT * FROM reviews WHERE id = ?', (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the review's attributes in the database"""
        if self.id is None:
            raise ValueError("Cannot update a review that hasn't been saved.")
        self.save()

    def delete(self):
        """Delete the review from the database and local dictionary"""
        if self.id is None:
            raise ValueError("Cannot delete a review that hasn't been saved.")
        CURSOR.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
        del Review.all[self.id]
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances"""
        CURSOR.execute('SELECT * FROM reviews')
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int) or not self._is_valid_employee_id(value):
            raise ValueError("Employee ID must be an integer and exist in the employees table.")
        self._employee_id = value

    @staticmethod
    def _is_valid_employee_id(employee_id):
        """Check if the employee_id exists in the employees table"""
        CURSOR.execute('SELECT COUNT(*) FROM employees WHERE id = ?', (employee_id,))
        return CURSOR.fetchone()[0] > 0

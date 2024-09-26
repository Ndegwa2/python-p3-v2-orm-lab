from __init__ import CURSOR, CONN
from department import Department

class Employee:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return (
            f"<Employee {self.id}: {self.name}, {self.job_title}, " +
            f"Department ID: {self.department_id}>"
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name):
            self._name = name
        else:
            raise ValueError(
                "Name must be a non-empty string"
            )

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, job_title):
        if isinstance(job_title, str) and len(job_title):
            self._job_title = job_title
        else:
            raise ValueError(
                "Job title must be a non-empty string"
            )

    @property
    def department_id(self):
        return self._department_id

    @department_id.setter
    def department_id(self, department_id):
        if type(department_id) is int and Department.find_by_id(department_id):
            self._department_id = department_id
        else:
            raise ValueError(
                "Department ID must reference a department in the database")

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Employee instances"""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Employee instances"""
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert or update a row in the employees table"""
        if self.id is None:
            CURSOR.execute("""
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """, (self.name, self.job_title, self.department_id))
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            CURSOR.execute("""
                UPDATE employees
                SET name = ?, job_title = ?, department_id = ?
                WHERE id = ?
            """, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def update(self):
        """Update the employee's attributes in the database"""
        if self.id is None:
            raise ValueError("Cannot update an employee that hasn't been saved.")
        self.save()

    def delete(self):
        """Delete the employee from the database and local dictionary"""
        if self.id is None:
            raise ValueError("Cannot delete an employee that hasn't been saved.")
        CURSOR.execute('DELETE FROM employees WHERE id = ?', (self.id,))
        del Employee.all[self.id]
        self.id = None
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department_id):
        """Initialize a new Employee instance and save it to the database"""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        """Return an Employee instance with attributes from the table row"""
        if row[0] in cls.all:
            return cls.all[row[0]]
        employee = cls(row[1], row[2], row[3], row[0])
        cls.all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        """Return a list of all Employee instances"""
        CURSOR.execute('SELECT * FROM employees')
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Return an Employee instance with the specified id"""
        CURSOR.execute('SELECT * FROM employees WHERE id = ?', (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return an Employee instance with the specified name"""
        CURSOR.execute('SELECT * FROM employees WHERE name = ?', (name,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def reviews(self):
        """Return a list of reviews associated with the current employee"""
        from review import Review
        CURSOR.execute('SELECT * FROM reviews WHERE employee_id = ?', (self.id,))
        rows = CURSOR.fetchall()
        return [Review.instance_from_db(row) for row in rows]

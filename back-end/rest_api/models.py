from database.db_config import db

# Toll Operator Table
class TollOperator(db.Model):
    __tablename__ = 'Toll_Operator'
    OpID = db.Column(db.String(255), primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Toll Station Table
class TollStation(db.Model):
    __tablename__ = 'Toll_Station'
    TollID = db.Column(db.String(255), primary_key=True)
    OpID = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))
    Name = db.Column(db.String(255), nullable=False)
    Locality = db.Column(db.String(255))
    Road = db.Column(db.String(255))
    Lat = db.Column(db.Float)
    Long = db.Column(db.Float)
    PM = db.Column(db.String(50))
    Price1 = db.Column(db.Float)
    Price2 = db.Column(db.Float)
    Price3 = db.Column(db.Float)
    Price4 = db.Column(db.Float)

# Tag Table
class Tag(db.Model):
    __tablename__ = 'Tag'
    tag_ID = db.Column(db.Integer, primary_key=True)
    tagRef = db.Column(db.String(255), nullable=False)
    OpID = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))

# Pass Table
class Pass(db.Model):
    __tablename__ = 'Pass'
    passID = db.Column(db.Integer, primary_key=True)
    tag_ID = db.Column(db.Integer, db.ForeignKey('Tag.tag_ID'))
    timestamp = db.Column(db.DateTime, nullable=False)
    charge = db.Column(db.Float, nullable=False)
    TollID = db.Column(db.String(255), db.ForeignKey('Toll_Station.TollID'))

# Debt Table
class Debt(db.Model):
    __tablename__ = 'Debt'
    Debt_ID = db.Column(db.Integer, primary_key=True)
    Operator_ID_1 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))
    Operator_ID_2 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))
    Nominal_Debt = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(50))

# Settlement Table
class Settlement(db.Model):
    __tablename__ = 'Settlement'
    Settlement_ID = db.Column(db.Integer, primary_key=True)
    Operator_ID_1 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))
    Operator_ID_2 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.OpID'))
    Amount = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)
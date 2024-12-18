from database.db_config import db

# Toll Operator Table
class TollOperator(db.Model):
    __tablename__ = 'Toll_Operator'
    Operator_ID = db.Column(db.String(255), primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Toll Station Table
class TollStation(db.Model):
    __tablename__ = 'Toll_Station'
    Toll_Station_ID = db.Column(db.Integer, primary_key=True)
    Toll_OperatorOperator_ID = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))
    Name = db.Column(db.String(255), nullable=False)
    Locality = db.Column(db.String(255))
    Road = db.Column(db.String(255))
    Latitude = db.Column(db.Float)
    Longitude = db.Column(db.Float)
    Type = db.Column(db.String(50))
    Price1 = db.Column(db.Float)
    Price2 = db.Column(db.Float)
    Price3 = db.Column(db.Float)
    Price4 = db.Column(db.Float)

# Tag Table
class Tag(db.Model):
    __tablename__ = 'Tag'
    tag_ID = db.Column(db.Integer, primary_key=True)
    tagRef = db.Column(db.String(255), nullable=False)
    tagHomeID = db.Column(db.String(255))
    Toll_OperatorOperator_ID = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))

# Pass Table
class Pass(db.Model):
    __tablename__ = 'Pass'
    passID = db.Column(db.Integer, primary_key=True)
    tag_ID = db.Column(db.Integer, db.ForeignKey('Tag.tag_ID'))
    timestamp = db.Column(db.DateTime, nullable=False)
    charge = db.Column(db.Float, nullable=False)
    Toll_Station_ID = db.Column(db.Integer, db.ForeignKey('Toll_Station.Toll_Station_ID'))

# Debt Table
class Debt(db.Model):
    __tablename__ = 'Debt'
    Debt_ID = db.Column(db.Integer, primary_key=True)
    Operator_ID_1 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))
    Operator_ID_2 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))
    Nominal_Debt = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(50))

# Settlement Table
class Settlement(db.Model):
    __tablename__ = 'Settlement'
    Settlement_ID = db.Column(db.Integer, primary_key=True)
    Operator_ID_1 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))
    Operator_ID_2 = db.Column(db.String(255), db.ForeignKey('Toll_Operator.Operator_ID'))
    Amount = db.Column(db.Float)
    Date = db.Column(db.Date, nullable=False)
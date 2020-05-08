from flask import Flask, jsonify
import numpy as np
from sqlalchemy import and_
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base=automap_base()
base.prepare(engine,reflect=True)
Measurement=base.classes.measurement
Station=base.classes.station




app=Flask(__name__)

@app.route("/")
def welcome ():
    """List of all available api routes"""
    return(f"Available routes:<br/> "
           f"/api/v1.0/precipitation <br/> "
           f"/api/v1.0/stations <br/>"
           f"/api/v1.0/tobs")

#Convert the query results to a dictionary using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    result={}
    for date, prcp in date_prcp:
        result[date]=prcp

    return jsonify(result)

# Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_date=session.query(Station.station).all()
    session.close()
    result=list(np.ravel(station_date))
    return jsonify(result)

#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    station_temp = session.query(Measurement.station, Measurement.tobs).filter(and_(Measurement.station == 'USC00519281',
             Measurement.date >= (dt.datetime.strptime(last_day[0], '%Y-%m-%d') - dt.timedelta(days=366)))).all()
    session.close()
    result_temp = list(np.ravel(station_temp))

    return jsonify(result_temp )

if __name__== '__main__':
    app.run(debug=True)

from flask import Flask, request, render_template
import calendar
import time
import datetime
import sys
import Adafruit_DHT
import arrow
import sqlite3
import plotly.plotly as py
from plotly.graph_objs import *


app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

@app.route("/lab_temp")
def lab_temp():
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
	if humidity is not None and temperature is not None:
		return render_template("lab_temp.html",temp=temperature,hum=humidity)
	else:
		return render_template("no_sensor.html")

@app.route("/lab_env_db", methods=['GET'])  #Add date limits in the URL #Arguments: from=2015-03-04&to=2015-03-05
def lab_env_db():
    temperatures, humidities, timezone, from_date_str, to_date_str = get_records()
    print ("QUERY STRING: %s" % request.query_string)
	# Create new record tables so that datetimes are adjusted back to the user browser's time zone.
    time_adjusted_temperatures = []
    time_adjusted_temperatures_2 = []
    time_adjusted_humidities = []
    time_adjusted_humidities_2 = []


    for record in temperatures:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm:ss").to(timezone)
        time_adjusted_temperatures.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])
        #time_adjusted_temperatures_2.append([time.mktime(datetime.datetime.strptime(local_timedate.format('YYYY-MM-DD HH:mm:ss'), "%Y-%m-%d %H:%M:%S").timetuple()), round(record[2],2)])
        time_adjusted_temperatures_2.append([calendar.timegm(time.strptime(local_timedate.format('YYYY-MM-DD HH:mm:SS'), "%Y-%m-%d %H:%M:%S")) * 1000, round(record[2],2)])
	
	
	
	#calendar.timegm(time.strptime('Jul 9, 2009 @ 20:02:58 UTC', '%b %d, %Y @ %H:%M:%S UTC'))

    #s="2018-11-29 20:45"
    #time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").timetuple())

    

    for record in humidities:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
        time_adjusted_humidities.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(record[2],2)])
        #time_adjusted_humidities_2.append([time.mktime(datetime.datetime.strptime(local_timedate.format('YYYY-MM-DD HH:mm'), "%Y-%m-%d %H:%M").timetuple()), round(record[2],2)])
        time_adjusted_humidities_2.append([calendar.timegm(time.strptime(local_timedate.format('YYYY-MM-DD HH:mm:SS'), "%Y-%m-%d %H:%M:%S")) * 1000, round(record[2],2)])	

    print ("rendering lab_env_db.html with: %s, %s, %s" % (timezone, from_date_str, to_date_str))

    range_h_form	= request.args.get('range_h','');  #This will return a string, if field range_h exists in the request
    range_h_int 	= "nan"  #initialise this variable with not a number
    try:
	    range_h_int	= int(range_h_form)
    except:
	    range_h_int = 3

    return render_template("lab_env_db_3.html",	timezone		= timezone,
												range_h_int		= range_h_int,
												temp 			= time_adjusted_temperatures,
												temp2			= time_adjusted_temperatures_2,
												hum 			= time_adjusted_humidities,
												hum2 			= time_adjusted_humidities_2,
												from_date 		= from_date_str,
												to_date 		= to_date_str,
												temp_items 		= len(temperatures),
												query_string	= request.query_string, #This query string is used
																						#by the Plotly link
												hum_items 		= len(humidities))

def get_records():
	from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
	to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	timezone 		= request.args.get('timezone','Etc/UTC');
	range_h_form	= request.args.get('range_h','');  #This will return a string, if field range_h exists in the request
	range_h_int 	= "nan"  #initialise this variable with not a number

	print ("REQUEST:")
	print (request.args)

	try:
		range_h_int	= int(range_h_form)
	except:
		print ("range_h_form not a number")


	print ("Received from browser: %s, %s, %s, %s" % (from_date_str, to_date_str, timezone, range_h_int))

	if not validate_date(from_date_str):			# Validate date before sending it to the DB
		from_date_str 	= time.strftime("%Y-%m-%d 00:00")
	if not validate_date(to_date_str):
		to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB
	print ('2. From: %s, to: %s, timezone: %s' % (from_date_str,to_date_str,timezone))
	# Create datetime object so that we can convert to UTC from the browser's local time
	from_date_obj       = datetime.datetime.strptime(from_date_str,'%Y-%m-%d %H:%M')
	to_date_obj         = datetime.datetime.strptime(to_date_str,'%Y-%m-%d %H:%M')

	# If range_h is defined, we don't need the from and to times
	if isinstance(range_h_int,int):
		arrow_time_from = arrow.utcnow().replace(hours=-range_h_int)
		arrow_time_to   = arrow.utcnow()
		from_date_utc   = arrow_time_from.strftime("%Y-%m-%d %H:%M")
		to_date_utc     = arrow_time_to.strftime("%Y-%m-%d %H:%M")
		from_date_str   = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
		to_date_str	    = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
	else:
		#Convert datetimes to UTC so we can retrieve the appropriate records from the database
		from_date_utc   = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
		to_date_utc     = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

	conn 			    = sqlite3.connect('/var/www/lab_app/lab_app.db')
	curs 			    = conn.cursor()
	curs.execute("SELECT * FROM temperatures WHERE rDateTime BETWEEN ? AND ? order by rDateTime", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
	temperatures 	    = curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE rDateTime BETWEEN ? AND ? order by rDateTime", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
	humidities 		    = curs.fetchall()
	conn.close()

	return [temperatures, humidities, timezone, from_date_str, to_date_str]

@app.route("/to_plotly", methods=['GET'])  #This method will send the data to ploty.
def to_plotly():
	temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

	# Create new record tables so that datetimes are adjusted back to the user browser's time zone.
	time_series_adjusted_temperatures   = []
	time_series_adjusted_humidities 	= []
	time_series_temperature_values 	    = []
	time_series_humidity_values 		= []

	for record in temperatures:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_temperatures.append(local_timedate.format('YYYY-MM-DD HH:mm'))
		time_series_temperature_values.append(round(record[2],2))

	for record in humidities:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_humidities.append(local_timedate.format('YYYY-MM-DD HH:mm')) #Best to pass datetime in text
																						  #so that Plotly respects it
		time_series_humidity_values.append(round(record[2],2))

	temp = Scatter(
        		x     = time_series_adjusted_temperatures,
        		y     = time_series_temperature_values,
        		name  = 'Temperature'
    				)
	hum = Scatter(
        		x     = time_series_adjusted_humidities,
        		y     = time_series_humidity_values,
        		name  = 'Humidity',
        		yaxis = 'y2'
    				)

	data = Data([temp, hum])

	layout = Layout(
					title  = "Temperature and humidity",
				    xaxis  = XAxis(
				        type      = 'date',
				        autorange = True
				    ),
				    yaxis          = YAxis(
				    	title      = 'Celsius',
				        type       = 'linear',
				        autorange  = True
				    ),
				    yaxis2 = YAxis(
				    	title      = 'Percent',
				        type       = 'linear',
				        autorange  = True,
				        overlaying = 'y',
				        side       = 'right'
				    )

					)
	fig      = Figure(data = data, layout = layout)
	plot_url = py.plot(fig, filename = 'lab_temp_hum')

	return plot_url
	
@app.route("/to_plotly2", methods=['GET'])  #This method will send the data to ploty.
def to_plotly2():
	temperatures, humidities, timezone, from_date_str, to_date_str = get_records()

	# Create new record tables so that datetimes are adjusted back to the user browser's time zone.
	time_series_adjusted_temperatures   = []
	time_series_adjusted_humidities 	= []
	time_series_temperature_values 	    = []
	time_series_humidity_values 		= []

	for record in temperatures:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_temperatures.append(local_timedate.format('YYYY-MM-DD HH:mm'))
		time_series_temperature_values.append(round(record[2],2))

	for record in humidities:
		local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
		time_series_adjusted_humidities.append(local_timedate.format('YYYY-MM-DD HH:mm')) #Best to pass datetime in text
																						  #so that Plotly respects it
		time_series_humidity_values.append(round(record[2],2))

	temp = Scatter(
        		x     = time_series_adjusted_temperatures,
        		y     = time_series_temperature_values,
        		name  = 'Temperature'
    				)
	hum = Scatter(
        		x     = time_series_adjusted_humidities,
        		y     = time_series_humidity_values,
        		name  = 'Humidity',
        		yaxis = 'y2'
    				)

	data = Data([temp, hum])

	layout = Layout(
					title  = "Temperature and humidity",
				    xaxis  = XAxis(
				        type      = 'date',
				        autorange = True
				    ),
				    yaxis          = YAxis(
				    	title      = 'Celsius',
				        type       = 'linear',
				        autorange  = True
				    ),
				    yaxis2 = YAxis(
				    	title      = 'Percent',
				        type       = 'linear',
				        autorange  = True,
				        overlaying = 'y',
				        side       = 'right'
				    )

					)
	fig      = Figure(data = data, layout = layout)
	plot_url = py.plot(fig, filename = 'lab_temp_hum')

	return render_template("redirectPlot.html",plot_url=plot_url)


def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

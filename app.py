from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
	# import packages for chart
	from pandas_datareader import data
	from datetime import datetime, timedelta
	from bokeh.plotting import figure, show, output_file
	from bokeh.embed import components
	from bokeh.resources import CDN

	# import the data
	symbol = "GOOG"
	end = datetime.today()
	start = end - timedelta(days = 30)
	df = data.DataReader(name  = symbol, data_source = "yahoo", start = start, end = end)

	# create new columns for viz
	df["center"] = (df["Open"] + df["Close"])/2
	df["abs_change"] = abs(df["Open"] - df["Close"])

	# create the bokeh plot
	p = figure(width = 1000, height = 300, sizing_mode = "scale_width",
	           title = symbol + ": "+ str(start)[0:10] + " to " + str(end)[0:10],x_axis_type = "datetime")

	p.grid.grid_line_alpha = .3

	# add the segment glyph
	p.segment(x0 = df.index, y0 = df["High"], x1 = df.index, y1 = df["Low"], color = "black")

	# with of candlesticks is 12 hours. In milliseconds
	hours_12 = 12 * 60 * 60 * 1000

	# create the green (bullish) candlesticks
	green_dates = df.index[df["Close"] > df["Open"]]
	green_center = df["center"].loc[green_dates]
	green_height = df["abs_change"].loc[green_dates]

	# add the green candlestick glyph
	p.rect(x = green_dates, y = green_center,
	       width = hours_12, height = green_height,
	       color = "green", line_color = "black")

	# create the red (bearish) candlesticks
	red_dates = df.index[df["Close"] <= df["Open"]]
	red_center = df["center"].loc[red_dates]
	red_height = df["abs_change"].loc[red_dates]

	# add the red candlestick glyph
	p.rect(x = red_dates, y = red_center,
	       width = hours_12, height = red_height,
	       color = "red", line_color = "black")

	# to embed into web
	script1, div1 = components(p)
	cdn_js = CDN.js_files[0]
	cdn_css = CDN.css_files[0]

	# render html
	return render_template("home.html", script1 = script1, div1 = div1, cdn_css = cdn_css, cdn_js = cdn_js)

@app.route("/about")
def about():
	return render_template("about.html")

if __name__ == "__main__":
	app.run(debug = True)
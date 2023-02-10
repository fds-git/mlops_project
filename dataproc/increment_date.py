from datetime import datetime, timedelta
import argparse


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Start date increment")
	parser.add_argument("-d", dest="nb_days", help="number of days", required=True, type=int)
	parser.add_argument("-date", dest="start_date", help="2022-04-01", required=True, type=str)
	args = parser.parse_args()

	nb_days = args.nb_days
	start_date = args.start_date
	increment = timedelta(days=nb_days)

	date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
	new_date_object = date_object + increment
	new_date_str = new_date_object.strftime("%Y-%m-%d")
	print(new_date_str)

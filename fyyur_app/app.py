#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (Flask, 
                   render_template,
                   request,
                   Response,
                   flash,
                   redirect,
                   url_for,
                   jsonify)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
from models import db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.all()

  # make a list of city/state pairs
  city_state_pairs = []  

  for venue in venues:
    city = venue.city
    state = venue.state
    if (city, state) not in city_state_pairs:
      city_state_pairs.append((city, state))

    venue_id = venue.id
    name = venue.name

    num_upcoming_shows = 0
    shows = db.session.query(Show).join(Venue, Show.venue_id==venue.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    if len(data) == 0:
      location = {'city': city,
                  'state': state,
                  'venues': [{
                    'id': venue_id,
                    'name': name,
                    'num_upcoming_shows': num_upcoming_shows
                  }]
                  }
      data.append(location)
      continue

    else:
      for d in data:
        if d['city'] == city and d['state'] == state:
          location = {'id': venue_id,
                      'name': name,
                      'num_upcoming_shows': num_upcoming_shows}
          d['venues'].append(location)
          break

        else:
          location = {'city': city,
                  'state': state,
                  'venues': [{
                    'id': venue_id,
                    'name': name,
                    'num_upcoming_shows': num_upcoming_shows
                  }]
                  }
          data.append(location)
          break

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  req = request.form['search_term']

  search_query = f'%{req}%'
  venues = Venue.query.filter(Venue.name.ilike(search_query)).all()

  data = []
  for venue in venues:

    num_upcoming_shows = 0
    shows = db.session.query(Show).join(Venue, Show.venue_id==venue.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    temp_venue = {'id': venue.id,
                  'name': venue.name,
                  'num_upcoming_shows': num_upcoming_shows}
    data.append(temp_venue)

  response = {'count': len(venues),
              'data': data}

  return render_template('pages/search_venues.html', results=response,
    search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows = []
  shows = db.session.query(Show).join(Venue, Show.venue_id==venue.id)

  for show in shows:
    show_data = {'artist_id': show.artist_id,
                 'artist_name': show.artist.name,
                 'artist_image_link': show.artist.image_link,
                 'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")}
    if show.start_time > datetime.now():
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  venue_data = vars(venue)
  venue_data['past_shows'] = past_shows
  venue_data['upcoming_shows'] = upcoming_shows
  venue_data['past_shows_count'] = len(past_shows)
  venue_data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  name = form.name.data  

  if not form.validate():
    flash(f'Venue {form.name.data} was unsuccessfully listed...')
    print(form.errors)
    return render_template('pages/home.html')

  try:
    # cannot use **form.data because of csrf_token that is passed along
    # with the form
    venue = Venue(name = form.name.data,
                  genres = form.genres.data,
                  city = form.city.data,
                  state = form.state.data,
                  address = form.address.data,
                  phone = form.phone.data,
                  website_link = form.website_link.data,
                  image_link = form.image_link.data,
                  facebook_link = form.facebook_link.data,
                  seeking_talent = form.seeking_talent.data,
                  seeking_description = form.seeking_description.data)

    db.session.add(venue)
    db.session.commit()
    flash(f'Venue {form.name.data} was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Venue {form.name.data} was unsuccessfully listed...')
    print(form.errors)
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  name = venue.name
  try:
    # shows will be deleted because of the cascade 'delete-orphan'
    db.session.delete(venue)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if error:
    print(f'Unable to delete venue {name}...')
    flash(f'Unable to delete venue {name}...')
    return jsonify({'success':False})
  else:
    flash(f'Successfully deleted venue {name}!')
    print(f'Successfully deleted venue {name}!')

    return jsonify({'success':True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  req = request.form['search_term']

  search_query = f'%{req}%'
  artists = Artist.query.filter(Artist.name.ilike(search_query)).all()

  data = []
  for artist in artists:

    num_upcoming_shows = 0
    shows = db.session.query(Show).join(Artist, Show.venue_id==artist.id)
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    temp_artist = {'id': artist.id,
                  'name': artist.name,
                  'num_upcoming_shows': num_upcoming_shows}
    data.append(temp_artist)

  response = {'count': len(artists),
              'data': data}

  return render_template('pages/search_artists.html', results=response,
    search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  
  past_shows = []
  upcoming_shows = []

  shows = db.session.query(Show).join(Artist, Show.venue_id==artist.id)
  for show in shows:
    show_data = {'venue_id': show.venue_id,
                 'venue_name': show.venue.name,
                 'venue_image_link': show.venue.image_link,
                 'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")}
    if show.start_time > datetime.now():
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  artist_data = vars(artist)
  artist_data['past_shows'] = past_shows
  artist_data['upcoming_shows'] = upcoming_shows
  artist_data['past_shows_count'] = len(past_shows)
  artist_data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  artist = Artist.query.get(artist_id)
  name = artist.name

  if form.validate():
    try:
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.commit()

    except:
      error = True
      print(sys.exc_info())
      db.session.rollback()

    finally:
      db.session.close()

  else:
    error = True

  if error:
    flash(f'Could not update artist {name}...')
    print(form.errors)
  else:
    flash(f'Successfully updated artist {name}!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  name = venue.name

  if form.validate():
    try:
      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.address = form.address.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.website_link = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.image_link = form.image_link.data
      db.session.commit()

    except:
      error = True
      print(sys.exc_info())
      db.session.rollback()

    finally:
      db.session.close()

  else:
    error = True

  if error:
    flash(f'Could not update venue {name}...')
    print(form.errors)
  else:
    flash(f'Successfully updated venue {name}!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  if not form.validate():
    flash(f'Artist {form.name.data} was unsuccessfully listed...')
    print(form.errors)
    return render_template('pages/home.html')
  
  try:
    # cannot use **form.data because of csrf_token that is passed along
    # with the form
    artist = Artist(name = form.name.data,
                    city = form.city.data,
                    state = form.state.data,
                    phone = form.phone.data,
                    genres = form.genres.data,
                    image_link = form.image_link.data,
                    facebook_link = form.facebook_link.data,
                    website_link = form.website_link.data,
                    seeking_venue = form.seeking_venue.data,
                    seeking_description = form.seeking_description.data)

    db.session.add(artist)
    db.session.commit()  
    flash(f'Artist {form.name.data} was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Artist {form.name.data} was unsuccessfully listed...')
    print(form.errors)

  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows = Show.query.all()
  shows_data = []
  for show in shows:
    venue_id = show.venue.id
    venue_name = Venue.query.get(venue_id).name

    artist_id = show.artist.id
    artist_name = Artist.query.get(artist_id).name
    artist_image_link = Artist.query.get(artist_id).image_link

    start_time = show.start_time.strftime("%m/%d/%Y, %H:%M")

    show_data = {'venue_id': venue_id,
                 'venue_name': venue_name,
                 'artist_id': artist_id,
                 'artist_name': artist_name,
                 'artist_image_link': artist_image_link,
                 'start_time': start_time}
    shows_data.append(show_data)

  return render_template('pages/shows.html', shows=shows_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)

  if not form.validate():
    flash('An error occurred. Show could not be listed...')
    print(form.errors)
    return render_template('pages/home.html')

  try:
    # cannot use **form.data because of csrf_token that is passed along
    # with the form
    show = Show(artist_id = form.artist_id.data,
                venue_id = form.venue_id.data,
                start_time = form.start_time.data)

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully lsited!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed...')
    print(form.errors)

  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0")

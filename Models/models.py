from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Track(DB.Model):

    # required variables
    id = DB.Column(DB.String, primary_key=True, nullable=False)
    preference = DB.Column(DB.Boolean, nullable=False)
    name = DB.Column(DB.String, nullable=False)
    artists = DB.Column(DB.String, nullable=False)
    vector = DB.Column(DB.PickleType, nullable=False)

    # variable to be updated when user asks for recommendations
    recommend = DB.Column(DB.Float)

    def __repr__(self):
        as_string = f'{self.name} - {self.artists}'
        # for testing:
        # as_string = f'{self.name} - {self.artists} - {self.vector}'
        # if self.recommend and self.preference is False:
        #     as_string += f' - {self.recommend}'
        return as_string

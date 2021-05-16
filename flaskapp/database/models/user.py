from . import db
import jwt
import datetime
from flaskapp import app
class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True)
  password = db.Column(db.String())

  def __repr__(self) -> str:
    return  '<User {}>'.format(self.username)

  def encode_auth_token(self, user_id):
    # generates the Auth Token
    try:
      payload = {
        # 'exp':datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=1, seconds=0),
        'iat': datetime.datetime.utcnow(),
        'sub':user_id
      }
      auth_token =  jwt.encode(
        payload,
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
      )
      whitelist_token = WhiteListToken(token=auth_token)
      
      db.session.add(whitelist_token)
      db.session.commit()
      return whitelist_token.token
    except Exception as e:
      return e
    
  @staticmethod
  def decode_auth_token(auth_token):
    # validate the auth token
    try:
      payload =jwt.decode(auth_token,  app.config.get("SECRET_KEY"), algorithms='HS256')
      is_whitelisted_token = WhiteListToken.check_whitelist(auth_token)

      if not is_whitelisted_token:
        return 'Token is not in whitelistedToken table'
      elif is_whitelisted_token:
        print(is_whitelisted_token)
        return is_whitelisted_token
      
    except jwt.InvalidTokenError:
      return 'Invalid token'



class WhiteListToken(db.Model):
  """
  Token Model for storing JWT tokens which are still valid
  """

  __tablename__ = "whitelist_tokens"

  id = db.coid = db.Column(db.Integer, primary_key=True, autoincrement=True)
  token = db.Column(db.String(500), unique=True, nullable=False)
  whitelisted_on = db.Column(db.DateTime, nullable=False)

  def __init__(self, token):
    self.token = token
    self.whitelisted_on = datetime.datetime.now()

  def __repr__(self):
    return '<id: token: {}'.format(self.token)
  
  @staticmethod
  def check_whitelist(auth_token):
    #check whether auth token has been whitelisted
    res:WhiteListToken = WhiteListToken.query.filter_by(token=str(auth_token)).first()

    if res:
      return True
    else:
      return False
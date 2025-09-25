from main import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from datetime import datetime

db = SQLAlchemy(app)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    fullname = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    fullname = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    instagram = db.Column(db.Boolean, nullable=False, default=False)
    facebook = db.Column(db.Boolean, nullable=False, default=False)
    youtube = db.Column(db.Boolean, nullable=False, default=False)
    linkedin = db.Column(db.Boolean, nullable=False, default=False)
    niche = db.Column(db.String, nullable=False, default="N/A")
    aboutyou = db.Column(db.String, nullable=False, default="N/A")
    profilepic = db.Column(db.Boolean, default=False)
    file_extension = db.Column(db.String, nullable=False, default="N/A")
    likes = db.Column(db.Integer, default=0)
    flag = db.Column(db.Boolean, nullable=False, default=False)

    feedbackdata = db.relationship('InfluencerFeedbackData', backref='influencer', lazy=True, cascade='all, delete-orphan')
    completed_campaigns = db.relationship('CompletedCampaigns', backref='influencer', lazy=True, cascade='all, delete-orphan')
    my_data = db.relationship('InfluencerData', backref='influencer', lazy=True, cascade='all, delete-orphan')
    ongoing_events = db.relationship('Ongoingevents', backref='influencer', lazy=True, cascade='all, delete-orphan')
    influencer_requests = db.relationship('InfluencerRequests', backref='influencer', lazy=True, cascade='all, delete-orphan')
    sponsor_requests = db.relationship('SponsorRequests', backref='influencer', lazy=True, cascade='all, delete-orphan')
    negotiates = db.relationship('Negotiate', backref='influencer', lazy=True, cascade='all, delete-orphan')

class InfluencerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    insta_fol = db.Column(db.Integer, nullable=False, default=0)
    facebook_fol = db.Column(db.Integer, nullable=False, default=0)
    youtube_fol = db.Column(db.Integer, nullable=False, default=0)
    linkedin_fol = db.Column(db.Integer, nullable=False, default=0)
    insta_link = db.Column(db.String, default="#")
    facebook_link = db.Column(db.String, default="#")
    youtube_link = db.Column(db.String, default="#")
    linkedin_link = db.Column(db.String, default="#")

class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    companyname = db.Column(db.String, nullable=False)
    industrysector = db.Column(db.String, nullable=False)
    companybackground = db.Column(db.String, nullable=False)
    profilepic = db.Column(db.Boolean, default=False)
    file_extension = db.Column(db.String, nullable=False, default="N/A")
    flag = db.Column(db.Boolean, nullable=False, default=False)
    
    negotiations = db.relationship('Negotiate', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    feedbackdata = db.relationship('SponsorFeedbackData', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    completed_campaigns = db.relationship('CompletedCampaigns', backref='sponsor', lazy=True)
    carddetail = db.relationship('SponsorCardDetails', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    ongoing_events = db.relationship('Ongoingevents', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    influencer_requests = db.relationship('InfluencerRequests', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    sponsor_requests = db.relationship('SponsorRequests', backref='sponsor', lazy=True, cascade='all, delete-orphan')

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    typeofcampaign = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    audience = db.Column(db.String, nullable=False)
    communication = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False, default=datetime.now())
    deadline = db.Column(db.DateTime, nullable=False)
    companyname = db.Column(db.String, nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    flag = db.Column(db.Boolean, nullable=False, default=False)

    completed_campaigns = db.relationship('CompletedCampaigns', backref='campaign', lazy=True, cascade='all, delete-orphan')
    influencer_requests = db.relationship('InfluencerRequests', backref='campaign', lazy=True, cascade='all, delete-orphan')
    sponsor_requests = db.relationship('SponsorRequests', backref='campaign', lazy=True, cascade='all, delete-orphan')
    ongoing_events = db.relationship('Ongoingevents', backref='campaign', lazy=True, cascade='all, delete-orphan')
    negotiates = db.relationship('Negotiate', backref='campaign', lazy=True, cascade='all, delete-orphan')    

class Ongoingevents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    budget = db.Column(db.Integer, nullable=False, default=0)
    progress = db.Column(db.Integer, nullable=False, default=5)

class InfluencerRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)

class SponsorRequests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)

class Negotiate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    budget = db.Column(db.Integer, nullable=False)

class CompletedCampaigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    completeddate = db.Column(db.DateTime, default=datetime.now())
    influencer_like = db.Column(db.Boolean, default=False)
    campaign_like = db.Column(db.Boolean, default=False)

class SponsorCardDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    bank = db.Column(db.String, nullable=False)
    cardnumber = db.Column(db.Integer, nullable=False)
    cvv = db.Column(db.Integer, nullable=False)

class InfluencerFeedbackData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    camp_exp = db.Column(db.String, default="N/A")
    suggestions = db.Column(db.String, default="N/A")

class SponsorFeedbackData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    camp_exp = db.Column(db.String, default="N/A")
    suggestions = db.Column(db.String, default="N/A")

with app.app_context():
    db.create_all()
    admin = Admin.query.first()
    if not admin:
        passhash = generate_password_hash('admin')
        admin = Admin(username='admin', passhash=passhash, fullname='Admin', email='admin@gmail.com', is_admin=True)
        db.session.add(admin)
        db.session.commit()

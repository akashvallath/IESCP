from main import app
from flask import render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Influencer, Sponsor, Campaign, InfluencerRequests, SponsorCardDetails
from models import Ongoingevents, SponsorRequests, InfluencerData, Negotiate, CompletedCampaigns
from models import InfluencerFeedbackData, SponsorFeedbackData
from functools import wraps
from datetime import datetime, timedelta
import os

# decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        influencer = Influencer.query.filter_by(username=session['username']).first()
        sponsor = Sponsor.query.filter_by(username=session['username']).first()
        admin = Admin.query.filter_by(username=session['username']).first()
        if sponsor or influencer or admin:
            return func(*args, **kwargs)
        session.pop('username')
        return redirect(url_for('login'))
    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash("You need to login first")
            return redirect(url_for('login'))
        user = Admin.query.filter_by(username=session['username']).first()
        if not user:
            session.pop('username')
            return redirect(url_for('login'))
        if not user.is_admin:
            flash("You are not authorized to visit this page")
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    if 'username' in session:
        admin = Admin.query.filter_by(username = session['username']).first()
        if admin:
            return redirect(url_for('adminhome', id=admin.id))
        sponsor = Sponsor.query.filter_by(username=session['username']).first()
        if sponsor:
            return redirect(url_for('sponsorhome', id = sponsor.id))
        influencer = Influencer.query.filter_by(username=session['username']).first()
        if influencer:
            return redirect(url_for('influencerhome', id = influencer.id))
    return render_template('loginpage.html')

@app.route('/adminhome/<int:id>')
@admin_required
def adminhome(id):
    admin  = Admin.query.get(id)
    total_campaigns = len(Campaign.query.all())
    total_influencers = len(Influencer.query.all())
    total_sponsors = len(Sponsor.query.all())
    flaggedinfluencers = Influencer.query.filter_by(flag=True).all()
    flaggedsponsors = Sponsor.query.filter_by(flag=True).all()
    flaggedcampaigns = Campaign.query.filter_by(flag=True).all()
    return render_template('adminhome.html', admin=admin, total_campaigns=total_campaigns,
                           total_influencers=total_influencers, total_sponsors=total_sponsors, 
                           flaggedinfluencers=flaggedinfluencers, flaggedsponsors=flaggedsponsors, 
                           flaggedcampaigns=flaggedcampaigns)

@app.route('/admin/<int:id>/find/influencers')
@admin_required
def find_influencersforadmin(id):
    admin = Admin.query.get(id)
    niche = request.args.get('niche')
    if niche:
        influencers = Influencer.query.filter_by(niche=niche).all()
        return render_template('admin_findinfluencers.html', influencers=influencers, admin=admin)
    influencers = Influencer.query.all()
    return render_template('admin_findinfluencers.html', influencers=influencers, admin=admin)

@app.route('/admin/<int:id>/influencerprofile/<int:influencer_id>')
@admin_required
def influencerprofileforadmin(id, influencer_id):
    admin = Admin.query.get(id)
    influencer = Influencer.query.get(influencer_id)
    ongoing_campaigns = influencer.ongoing_events
    return render_template('influencerprofileforadmin.html', admin=admin, influencer=influencer, ongoing_campaigns=ongoing_campaigns)

@app.route('/admin/<int:id>/find/sponsors')
@admin_required
def find_sponsorsforadmin(id):
    admin = Admin.query.get(id)
    industrysector = request.args.get('industrysector')
    if industrysector:
        sponsors = Sponsor.query.filter_by(industrysector=industrysector).all()
        return render_template('admin_findsponsors.html', admin=admin, sponsors=sponsors)
    sponsors = Sponsor.query.all()
    return render_template('admin_findsponsors.html', admin=admin, sponsors=sponsors)

@app.route('/admin/<int:id>/sponsorprofile/<int:sponsor_id>')
@admin_required
def sponsorprofileforadmin(id, sponsor_id):
    admin = Admin.query.get(id)
    sponsor = Sponsor.query.get(sponsor_id)
    typeofcampaign = request.args.get('type')
    if typeofcampaign:
        campaigns = Campaign.query.filter_by(typeofcampaign=typeofcampaign, sponsor_id=sponsor.id).all()
        return render_template('sponsorprofileforadmin.html', admin=admin, sponsor=sponsor, campaigns=campaigns)
    campaigns = sponsor.campaigns
    return render_template('sponsorprofileforadmin.html', admin=admin, sponsor=sponsor, campaigns=campaigns)

@app.route('/admin/<int:id>/campaign/<int:campaign_id>')
@admin_required
def campaigndetailsforadmin(id, campaign_id):
    admin = Admin.query.get(id)
    campaign = Campaign.query.get(campaign_id)
    ongoing_events = Ongoingevents.query.filter_by(campaign_id=campaign.id).all()
    return render_template('campaigndetailsforadmin.html', admin=admin, campaign=campaign, ongoing_events=ongoing_events)

@app.route('/admin/<int:id>/flag/<int:campaign_id>/campaign')
@admin_required
def flagcampaign(id, campaign_id):
    admin = Admin.query.get(id)
    campaign = Campaign.query.get(campaign_id)
    campaign.flag = True
    db.session.add(campaign)
    db.session.commit()
    flash('flagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/admin/<int:id>/UNflag/<int:campaign_id>/campaign')
@admin_required
def unflagcampaign(id, campaign_id):
    admin = Admin.query.get(id)
    campaign = Campaign.query.get(campaign_id)
    campaign.flag = False
    db.session.add(campaign)
    db.session.commit()
    flash('UNflagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/admin/<int:id>/UNflag/<int:influencer_id>/influencer')
@admin_required
def unflaginfluencer(id, influencer_id):
    admin = Admin.query.get(id)
    influencer = Influencer.query.get(influencer_id)
    influencer.flag = False
    db.session.add(influencer)
    db.session.commit()
    flash('UNflagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/admin/<int:id>/flag/<int:influencer_id>/influencer')
@admin_required
def flaginfluencer(id, influencer_id):
    admin = Admin.query.get(id)
    influencer = Influencer.query.get(influencer_id)
    influencer.flag = True
    db.session.add(influencer)
    db.session.commit()
    flash('flagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/admin/<int:id>/flag/<int:sponsor_id>/sponsor')
@admin_required
def flagsponsor(id, sponsor_id):
    admin = Admin.query.get(id)
    sponsor = Sponsor.query.get(sponsor_id)
    sponsor.flag = True
    db.session.add(sponsor)
    db.session.commit()
    flash('flagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/admin/<int:id>/UNflag/<int:sponsor_id>/sponsor')
@admin_required
def unflagsponsor(id, sponsor_id):
    admin = Admin.query.get(id)
    sponsor = Sponsor.query.get(sponsor_id)
    sponsor.flag = False
    db.session.add(sponsor)
    db.session.commit()
    flash('UNflagged!', 'success')
    return redirect(url_for('adminhome', id=admin.id))

@app.route('/guidelines')
def guideline():
    return render_template('guidelines.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('loginpage.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login', methods=['post'])
def loginpost():
    username = request.form.get('username')
    password = request.form.get('password')
    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.passhash, password):
        session['username'] = username
        return redirect(url_for('adminhome', id=admin.id))
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor and check_password_hash(sponsor.passhash, password):
        session['username'] = username
        return redirect(url_for('sponsorhome', id=sponsor.id))
    influencer = Influencer.query.filter_by(username=username).first()
    if influencer and check_password_hash(influencer.passhash, password):
        session['username'] = username
        return redirect(url_for('influencerhome', id = influencer.id))
    flash("Incorrect username or password")
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    return redirect(url_for('login'))

@app.route('/sponsorregister')
def sponsorregister():
    return render_template('sponsorregisterpage.html')

@app.route('/sponsorregister', methods=['POST'])
def sponsorregisterpost():
    username = request.form.get('username')
    if not username:
        flash('Please provide a username!')
        return redirect(url_for('sponsorregister'))
    if ' ' in username:
        flash('username should not contain space.you can use _ instead!')
        return redirect(url_for('sponsorregister'))
    sponsor = Sponsor.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()
    if sponsor or influencer or admin:
        flash("This username is taken.")
        return redirect(url_for('sponsorregister'))
    
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    email = request.form.get('email')

    sponsor = Sponsor.query.filter_by(email=email).first()
    if sponsor:
        flash("This email is already linked with an sponsor account!")
        return redirect(url_for('sponsorregister'))
    
    companyname = request.form.get('companyname')
    industrysector = request.form.get('industrysector')
    companybackground = request.form.get('cbackground')

    if not password or not confirm :
        flash("please enter the password!")
        return redirect(url_for('sponsorregister'))
    if not email:
        flash("Enter your Email!")
        return redirect(url_for('sponsorregister'))
    if not companyname:
        flash("please enter the company name!")
        return redirect(url_for('sponsorregister'))
    if not industrysector:
        flash("please select your industry sector")
        return redirect(url_for('sponsorregister'))
    if not companybackground:
        flash("Please enter your company background!")
        return redirect(url_for('sponsorregister'))
    if password != confirm:
        flash("You have not confirmed the password correctly!")
        return redirect(url_for('sponsorregister'))
    if len(password) < 8:
        flash("Password must have atleast 8 characters!")
        return redirect(url_for('sponsorregister'))
    passhash = generate_password_hash(password)
    profilepic = request.files['profilepic']
    if profilepic.filename != '':
        file_extension = os.path.splitext(profilepic.filename)[1]
        filename = str(username) + str(file_extension)
        profilepic.save(os.path.join(os.getcwd(), 'static', 'profilepics', filename))
        newsponsor = Sponsor(username=username, passhash=passhash, email=email,
                         companyname=companyname, industrysector=industrysector, 
                         companybackground=companybackground, profilepic=True, file_extension=file_extension)
    else:
        newsponsor = Sponsor(username=username, passhash=passhash, email=email,
                            companyname=companyname, industrysector=industrysector, 
                            companybackground=companybackground)
    db.session.add(newsponsor)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/campaigndetails')
def campaigndetail():
    return render_template('aboutcampaign.html')

@app.route('/create/<int:id>/campaign')
@login_required
def createcampaign(id):
    sponsor = Sponsor.query.get(id)
    if sponsor.flag:
        flash('You have been flaggeg! please contact admin!')
        return redirect(url_for('sponsorhome', id=sponsor.id))
    return render_template('createcampaign.html', sponsor=sponsor)

@app.route('/create/<int:id>/campaign', methods=['POST'])
@login_required
def createcampaign_post(id):
    sponsor = Sponsor.query.get(id)
    nameofcampaign = request.form.get('name')
    typeofcampaign = request.form.get('campaigntype')
    budget = request.form.get('budget')
    description = request.form.get('description')
    goals = request.form.get('goals')
    audience = request.form.get('target') 
    deadline = request.form.get('deadline')
    communication = request.form.get('communicationtype')
    if not nameofcampaign:
        flash("Please give a suitable name for your campaign !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not typeofcampaign:
        flash("Please select the campaign type !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not budget:
        flash("You have not provided the Budget !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not description:
        flash("Please provide the description of your campaign !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not goals:
        flash("Please provide the goals for your campaign !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not audience:
        flash("Please provide the target audience !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    if not deadline:
        flash("Please provide the deadline to complete your campaign !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    deadline_date_obj = datetime.strptime(deadline, '%Y-%m-%d').date()
    if not communication:
        flash("Do you want this campaign to be publicly visible or private? !")
        return redirect(url_for('createcampaign', id=sponsor.id))
    newcampaign = Campaign(name=nameofcampaign, typeofcampaign=typeofcampaign, 
                        budget=budget, description=description, 
                        audience=audience,communication=communication,
                        deadline=deadline_date_obj, goals=goals, 
                        companyname=sponsor.companyname, sponsor_id=sponsor.id)
    db.session.add(newcampaign)
    db.session.commit()
    return redirect(url_for('sponsorhome', id = sponsor.id))
    
@app.route('/influencerregister')
def influencerregister():
    return render_template('influencerregisterpage.html')

@app.route('/influencerregister', methods=['POST'])
def influencerregister_post():
    username = request.form.get('username')
    if not username:
        flash('Please provide a username!')
        return redirect(url_for('influencerregister'))
    if ' ' in username:
        flash('username should not contain space. you can use _ instead!')
        return redirect(url_for('influencerregister'))
    influencer = Influencer.query.filter_by(username=username).first()
    sponsor = Sponsor.query.filter_by(username=username).first()
    admin = Admin.query.filter_by(username=username).first()
    if influencer or sponsor or admin:
        flash('This username  already exist! Please try another one')
        return redirect(url_for('influencerregister'))
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    if not password or not confirm:
        flash('Complete the password fields!')
        return redirect(url_for('influencerregister'))
    if password != confirm:
        flash('Incorrect password confirmed!')
        return redirect(url_for('influencerregister'))
    if len(password) < 8:
        flash("Password must have atleast 8 characters!")
        return redirect(url_for('influencerregister'))
    fullname = request.form.get('fullname')
    if not fullname:
        flash('Please provide your full name.')
        return redirect(url_for('influencerregister'))
    email = request.form.get('email')
    if not email:
        flash('Please provide your email.')
        return redirect(url_for('influencerregister'))
    social_media_handles = request.form.getlist('social_media[]')
    print(social_media_handles)
    if not social_media_handles:
        flash('Please select atleast one social media platform!.If You dont have an social media account just create one!')
        return redirect(url_for('influencerregister'))
    instagram = 'instagram' in social_media_handles
    facebook = 'facebook' in social_media_handles
    youtube = 'youtube' in social_media_handles
    linkedin = 'linkedin' in social_media_handles
    passhash = generate_password_hash(password)
    niche = request.form.get('niche') 
    if not niche:
        flash('Please select your Niche!')
        return redirect(url_for('influencerregister'))
    profilepic = request.files['profilepic']
    if profilepic and profilepic.filename != '':
        file_extension = os.path.splitext(profilepic.filename)[1]
        filename = str(username) + str(file_extension)
        profilepic.save(os.path.join(os.getcwd(), 'static', 'profilepics', filename))
        newinfluencer = Influencer(username=username, passhash=passhash, fullname=fullname, 
                                email=email, instagram=instagram, facebook=facebook, 
                                youtube=youtube, linkedin=linkedin, niche=niche, 
                                profilepic=True, file_extension=file_extension)
    else:
       newinfluencer = Influencer(username=username, passhash=passhash, fullname=fullname, 
                                email=email, instagram=instagram, facebook=facebook, 
                                youtube=youtube, linkedin=linkedin, niche=niche) 
    db.session.add(newinfluencer)
    db.session.commit()
    newinfluencer_data = InfluencerData(influencer_id=newinfluencer.id)
    db.session.add(newinfluencer_data)
    db.session.commit()
    return redirect(url_for('login'))
    
@app.route('/sponsor/<int:id>/home')
@login_required
def sponsorhome(id):
    sponsor = Sponsor.query.get(id)
    influencer_requests = InfluencerRequests.query.filter_by(sponsor_id=id).all()
    my_requests = SponsorRequests.query.filter_by(sponsor_id=id).all()
    negotiations = sponsor.negotiations
    pending_payments = CompletedCampaigns.query.filter_by(sponsor_id=sponsor.id, payment_status=False).all()
    total_campaigns = len(Campaign.query.filter_by(sponsor_id=id).all())
    active_campaigns = len(Ongoingevents.query.filter_by(sponsor_id=sponsor.id).all())
    unique_contestants = db.session.query(Ongoingevents.influencer_id).filter(Ongoingevents.sponsor_id == sponsor.id).distinct()
    total_contestants = len(unique_contestants.all())
    return render_template('sponsorhome.html', sponsor=sponsor, tcamp=total_campaigns, negotiations=negotiations,
                           tcont=total_contestants, influencer_requests=influencer_requests, pending_payments=pending_payments,
                           my_requests=my_requests, active_campaigns=active_campaigns)

@app.route('/sponsor/<int:id>/my_campaigns')
@login_required
def sponsor_mycampaigns(id):
    sponsor = Sponsor.query.get(id)
    public_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id, communication="public").all()
    private_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id, communication="private").all()
    return render_template('sponsor_mycampaigns.html', sponsor=sponsor, public_campaigns=public_campaigns,
                           private_campaigns=private_campaigns)

@app.route('/influencer/<int:id>/home')
@login_required
def influencerhome(id):
    influencer = Influencer.query.get(id)
    pending_requests = influencer.influencer_requests
    negotiations = influencer.negotiates
    sponsor_requests = influencer.sponsor_requests
    completed_campaigns = CompletedCampaigns.query.filter_by(influencer_id=influencer.id).all()
    pending_payments = CompletedCampaigns.query.filter_by(influencer_id=influencer.id, payment_status=False).all()
    my_campaigns = Ongoingevents.query.filter_by(influencer_id=id).all()
    latest_campaigns = Campaign.query.filter_by(communication="public").all()
    if len(latest_campaigns) > 10:
        latest_campaigns = list(latest_campaigns.reverse())[:10]
    today = datetime.today()
    last_2week_start = today - timedelta(days=today.weekday() + 7)

    # Query campaigns created within the date range
    campaignthisweek = Campaign.query.filter((Campaign.created_on >= last_2week_start) & (Campaign.communication == "public")).all()
    return render_template('influencerhomepage.html', influencer=influencer, my_campaigns=my_campaigns, negotiations=negotiations,
                           sponsor_requests=sponsor_requests, pending_requests=pending_requests, completed_campaigns=completed_campaigns,
                           latest_campaigns=latest_campaigns, campaignthisweek=campaignthisweek, pending_payments=pending_payments)

@app.route('/sponsor/<int:id>/influencers')
@login_required
def find_influencers_for_sponsor(id):
    sponsor = Sponsor.query.get(id)
    niche = request.args.get('niche')
    if niche:
        influencers = Influencer.query.filter_by(niche=niche).all()
        return render_template('find_influencers_for_sponsor.html', sponsor=sponsor, influencers=influencers)
    influencers = Influencer.query.all()
    return render_template('find_influencers_for_sponsor.html', sponsor=sponsor, influencers=influencers)

@app.route('/influencer/<int:id>/find_campaign')
@login_required
def influencer_find_campaign(id):
    company = request.args.get('company')
    budget = request.args.get('budget')
    campaigntype = request.args.get('campaigntype')
    campaign_name = request.args.get('query')

    companies = Sponsor.query.all()
    influencer = Influencer.query.get(id)
    if not company and not budget and not campaigntype and not campaign_name:
        campaigns = Campaign.query.filter_by(communication="public").all()
        return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
    else:
        if campaign_name:
            campaigns  = Campaign.query.filter((Campaign.name.ilike(f'%{campaign_name}%')) & (Campaign.communication == "public")).all()
            return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
        if company:
            if budget:
                if campaigntype:
                    campaigns = Campaign.query.filter((Campaign.companyname==company) & (Campaign.budget >= budget) & (Campaign.typeofcampaign == campaigntype) & (Campaign.communication == "public")).all()
                    return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
                campaigns = Campaign.query.filter((Campaign.companyname==company) & (Campaign.budget >= budget) & (Campaign.communication == "public")).all()
                return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
            campaigns = Campaign.query.filter((Campaign.companyname==company) & (Campaign.communication == "public")).all()
            return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
        if budget:
            if campaigntype:
                campaigns = Campaign.query.filter((Campaign.budget >= budget) & (Campaign.typeofcampaign == campaigntype) & (Campaign.communication == "public")).all()
                return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
            campaigns = Campaign.query.filter((Campaign.budget >= budget) & (Campaign.communication == "public")).all()
            return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
        campaigns = Campaign.query.filter((Campaign.typeofcampaign == campaigntype) & (Campaign.communication == "public")).all()
        return render_template('influencer_campaign_search.html', influencer=influencer, campaigns=campaigns, companies=companies)
    
@app.route('/campaign/<int:infid>/<int:cmpid>')
@login_required
def campaign(cmpid, infid):
    campaign = Campaign.query.get(cmpid)
    sponsor = campaign.sponsor
    influencer = Influencer.query.get(infid)
    negotiate = Negotiate.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).first()
    completed_button = False
    update_progress = False
    accept = False
    progress = request.args.get('progress')
    if progress:
        progress = int(progress)
        event = Ongoingevents.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).first()
        event.progress = progress
        db.session.commit()
        update_progress = True
        if progress == 100:
            update_progress = False
            completed_button = True
        flash('updated progress succesfully', 'success')
        return render_template('campaign.html', campaign = campaign, influencer=influencer, sponsor=sponsor, negotiate=negotiate,
                           update_progress=update_progress, accept=accept, completed_button=completed_button, ongoing_event=event)
    budget = request.args.get('budget')
    if budget:
        influencer_request = InfluencerRequests.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).first()
        if influencer_request:
            db.session.delete(influencer_request)
            db.session.commit()
        if_negoatiate = Negotiate.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).first()
        if if_negoatiate:
            if_negoatiate.budget = budget
            db.session.commit()
            flash('You can wait till sponsor reply or continue with that budget!', 'success')
            return render_template('campaign.html', campaign = campaign, influencer=influencer, sponsor=sponsor,
                                   update_progress=update_progress, accept=accept, negotiate=negotiate)
        new_negotiate = Negotiate(campaign_id=campaign.id, influencer_id=influencer.id, budget=budget, sponsor_id=sponsor.id)
        db.session.add(new_negotiate)
        db.session.commit()
        flash('You can wait till sponsor reply or continue with that budget!', 'success')
        return render_template('campaign.html', campaign = campaign, influencer=influencer, sponsor=sponsor,
                           update_progress=update_progress, accept=accept, negotiate=negotiate)
    ongoing_event = Ongoingevents.query.filter_by(campaign_id=campaign.id,influencer_id=influencer.id).first()
    if ongoing_event:
        current_progress = ongoing_event.progress
        if current_progress == 100:
            completed_button = True
            update_progress = False
        else:
            completed_button = False
            update_progress = True
    sponsor_request = SponsorRequests.query.filter_by(campaign_id=campaign.id,influencer_id=influencer.id).first()
    if sponsor_request:
        accept = True
    return render_template('campaign.html', campaign = campaign, influencer=influencer, sponsor=sponsor, negotiate=negotiate,
                           update_progress=update_progress, accept=accept, ongoing_event=ongoing_event, completed_button=completed_button)

@app.route('/influencer/request/<int:campaign_id>/<int:influencer_id>')
@login_required
def influencer_request(campaign_id, influencer_id):
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)
    if influencer.flag:
        flash('You have been flagged! please contact admin.')
        return redirect(url_for('influencerhome', id=influencer.id))
    if campaign.flag:
        flash('This campaign is flagged! You can\'t send request!')
        return redirect(url_for('influencerhome', id=influencer.id))
    requested = InfluencerRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    negotiate = Negotiate.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    ongoing = Ongoingevents.query.filter_by(campaign_id=campaign_id).first()
    if ongoing:
        flash('You are already part of this campaign!', 'success')
        return redirect(url_for('influencerhome', id=influencer_id))
    if negotiate:
        flash('You have already negotiated for this campaign!')
        return redirect(url_for('influencerhome', id=influencer_id))
    if not requested:
        request = InfluencerRequests(campaign_id=campaign_id, influencer_id=influencer_id, sponsor_id=campaign.sponsor_id)
        db.session.add(request)
        db.session.commit()
        flash('Request sent successfully', category='success')
        return redirect(url_for('influencerhome', id=influencer_id))
    flash('Request has already been sent!')
    return redirect(url_for('influencerhome', id=influencer_id))

@app.route('/sponsor/campaingacceptreject/<operation>/<int:campaign_id>/<int:influencer_id>/<int:sponsor_id>')
@login_required
def sponsor_campaign_accept_reject(operation, campaign_id, influencer_id, sponsor_id):
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)
    sponsor = Sponsor.query.get(sponsor_id)
    if operation == "reject":
        request = InfluencerRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
        db.session.delete(request)
        db.session.commit()
        return redirect(url_for('sponsorhome', id=sponsor_id))
    elif operation == "accept":
        if influencer.flag:
            flash('This Influencer is flagged!')
            return redirect(url_for('sponsorhome', id=influencer_id))
        if sponsor.flag:
            flash('You are flagged!')
            return redirect(url_for('sponsorhome', id=influencer_id))
        if campaign.flag:
            flash('This campaign is flagged!')
            return redirect(url_for('influencerhome', id=influencer_id))
        event = Ongoingevents.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
        if not event:
            event = Ongoingevents(campaign_id=campaign_id, influencer_id=influencer_id, sponsor_id=sponsor_id, budget=campaign.budget)
            db.session.add(event)
            request = InfluencerRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
            sponsor_request = SponsorRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
            if sponsor_request:
                db.session.delete(sponsor_request)
            db.session.delete(request)
            db.session.commit()
            flash('done :)', category='success')
            return redirect(url_for('sponsorhome', id=sponsor_id))
        flash('This event is already running!')
        return redirect(url_for('sponsorhome', id=sponsor_id))
    
@app.route('/sponsor/edit/<int:id>/<int:sponsor_id>')
@login_required
def editcampaign(id, sponsor_id):
    campaign = Campaign.query.get(id)
    if campaign.flag:
        flash('You have been flagged! please contact admin')
        return redirect(url_for('sponsorhome', id=sponsor.id))
    sponsor = Sponsor.query.get(sponsor_id)
    if sponsor.flag:
        flash('You have been flagged! please contact admin')
        return redirect(url_for('sponsorhome'), id=sponsor.id)
    ongoingevent = Ongoingevents.query.filter_by(campaign_id=campaign.id).first()
    return render_template('editcampaign.html', campaign=campaign, sponsor=sponsor, ongoingevent=ongoingevent)

@app.route('/sponsor/edit/<int:id>/<int:sponsor_id>', methods=['POST'])
@login_required
def editcampaign_post(id, sponsor_id):
    campaign = Campaign.query.get(id)
    sponsor = Sponsor.query.get(sponsor_id)
    budget = request.form.get('budget')
    description = request.form.get('objective')
    goals = request.form.get('goals')
    deadline = request.form.get('deadline')
    communication = request.form.get('communication')
    if budget:
        campaign.budget = budget
    if description:
        campaign.description = description
    if goals:
        campaign.goals = goals
    if deadline:
        deadline_date_obj = datetime.strptime(deadline, '%Y-%m-%d').date()
        campaign.deadline = deadline_date_obj
    if communication:
        campaign.communication = communication
    db.session.commit()
    return redirect(url_for('sponsorhome', id=sponsor.id))

@app.route('/sponsor/delete/<int:id>/<int:sponsor_id>')
@login_required
def deletecampaign(id, sponsor_id):
    sponsor = Sponsor.query.get(id)
    if sponsor.flag:
        flash('You have been flagged! contact admin')
        return redirect(url_for('sponsorhome', id=sponsor_id))
    campaign = Campaign.query.get(id)
    if campaign.flag:
        flash('This campaign is flagged! contact admin!')
        return redirect(url_for('sponsorhome', id=sponsor_id))
    ongoingevent = Ongoingevents.query.filter_by(campaign_id=campaign.id).first()
    if not ongoingevent:
        db.session.delete(campaign)
        db.session.commit()
        flash('campaign deleted !', category='success')
        return redirect(url_for('sponsorhome', id=sponsor_id))
    flash('There are ongoing events for this campaign. you can delete it when the deadline is over or you can contact admin!', category='message')
    return redirect(url_for('sponsorhome', id=sponsor_id))

@app.route('/sponsor/<int:id>/campaign')
@login_required
def camapign_details_forsponsor(id):
    niche = request.args.get('niche')
    campaign = Campaign.query.get(id)
    sponsor = campaign.sponsor
    ongoing_events = campaign.ongoing_events
    pending_payments = CompletedCampaigns.query.filter_by(campaign_id=campaign.id, payment_status=False).all()
    requests = campaign.influencer_requests
    influencer_negotiated = Negotiate.query.filter_by(campaign_id=id).all()
    if niche:
        influencers = Influencer.query.filter_by(niche=niche).all()
    else:
        influencers = Influencer.query.all()
    return render_template('sponsorcampaign.html', ongoing_events=ongoing_events, sponsor=sponsor, 
                           campaign=campaign, requests=requests, influencers=influencers, 
                           influencer_negotiated=influencer_negotiated, pending_payments=pending_payments)

@app.route('/influencer/<int:id>/<int:campaign_id>/delete/request')
@login_required
def influencer_delete_request(id, campaign_id):
    request = InfluencerRequests.query.filter_by(influencer_id=id, campaign_id=campaign_id).first()
    db.session.delete(request)
    db.session.commit()
    flash('Deleted!')
    return redirect(url_for('influencerhome', id=id))

@app.route('/sponsor/<int:id>/<int:campaign_id>/delete/request')
@login_required
def sponsor_delete_request(id, campaign_id):
    request = SponsorRequests.query.filter_by(sponsor_id=id, campaign_id=campaign_id).first()
    db.session.delete(request)
    db.session.commit()
    flash('Deleted!')
    return redirect(url_for('sponsorhome', id=id))

@app.route('/sponsor/<int:id>/profile')
@login_required
def sponsor_myprofile(id):
    sponsor = Sponsor.query.get(id)
    stats = False
    if sponsor.campaigns:
        stats = True
    add_card = True
    carddetail = SponsorCardDetails.query.filter_by(sponsor_id=sponsor.id).first()
    if carddetail:
        add_card = False
    return render_template('sponsor_myprofile.html', stats=stats, sponsor=sponsor, add_card=add_card)

@app.route('/sponsor/<int:id>/editprofile')
@login_required
def sponsor_editprofile(id):
    sponsor = Sponsor.query.get(id)
    if sponsor.flag:
        flash('You have been flagged! contact admin')
        return redirect(url_for('sponsor_myprofile', id=sponsor.id))
    return render_template('sponsoreditprofile.html', sponsor=sponsor)

@app.route('/sponsor/<int:id>/editprofile', methods=['POST'])
@login_required
def sponsor_edit_profile_post(id):
    sponsor = Sponsor.query.get(id)
    username = request.form.get('username')
    oldusername = sponsor.username
    username_changed = False
    if sponsor.username != username and username:
        if oldusername != username:
            user = Sponsor.query.filter_by(username=username).first()
            if user:
                flash('This username already exist!')
                return redirect(url_for('sponsor_editprofile', id=sponsor.id))
            sponsor.username = username
            username_changed = True
            session['username'] = username
    email = request.form.get('email')
    if sponsor.email != email and email:
        sponsor.email = email
    companyname = request.form.get('companyname')
    if sponsor.companyname != companyname and companyname:
        sponsor.companyname = companyname
    profilepic = request.files['profilepic']
    if profilepic and profilepic.filename != '':
        file_extension = os.path.splitext(profilepic.filename)[1]
        if username_changed:
            filename = str(username) + str(file_extension)
        else:
            filename = str(oldusername) + str(file_extension)
        if sponsor.profilepic:
            filetoremove = oldusername + sponsor.file_extension
            os.remove(os.path.join(os.getcwd(), 'static', 'profilepics',filetoremove))
        profilepic.save(os.path.join(os.getcwd(), 'static', 'profilepics', filename))
        sponsor.profilepic = True
        sponsor.file_extension = file_extension
    else:
        if username_changed:
            oldfilename = oldusername + sponsor.file_extension
            newfilename = username + sponsor.file_extension
            oldpath = os.path.join(os.getcwd(), 'static', 'profilepics', oldfilename)
            newpath = os.path.join(os.getcwd(), 'static', 'profilepics', newfilename)
            os.rename(oldpath, newpath)
    companybackground = request.form.get('cbackground')
    if companybackground and companybackground != sponsor.companybackground:
        sponsor.companybackground = companybackground
    db.session.commit()
    return redirect(url_for('sponsor_myprofile', id=sponsor.id))

@app.route('/influencer/<int:id>/profile')
@login_required
def influencer_myprofile(id):
    influencer = Influencer.query.get(id)
    stats = False
    if influencer.ongoing_events or influencer.completed_campaigns:
        stats = True
    return render_template('influencer_myprofile.html', stats=stats, influencer=influencer)

@app.route('/influencer/<int:id>/editprofile')
@login_required
def influencer_editprofile(id):
    influencer = Influencer.query.get(id)
    return render_template('influencereditprofile.html', influencer=influencer)

@app.route('/influencer/<int:id>/editprofile', methods=['POST'])
@login_required
def influencer_editprofile_post(id):
    influencer = Influencer.query.get(id)
    influencer_data = InfluencerData.query.filter_by(influencer_id=id).first()
    username = request.form.get('username')
    oldusername = influencer.username
    username_changed = False
    if influencer.username != username and username:
        if oldusername != username:
            user = influencer.query.filter_by(username=username).first()
            if user:
                flash('This username already exist!')
                return redirect(url_for('influencer_editprofile', id=influencer.id))
            influencer.username = username
            username_changed = True
            session['username'] = username
    fullname = request.form.get('fullname')
    if influencer.fullname != fullname and fullname:
        influencer.fullname = fullname
    email = request.form.get('email')
    if influencer.email != email and email:
        influencer.email = email
    profilepic = request.files['profilepic']
    if profilepic and profilepic.filename != '':
        file_extension = os.path.splitext(profilepic.filename)[1]
        if username_changed:
            filename = str(username) + str(file_extension)
        else:
            filename = str(oldusername) + str(file_extension)
        if influencer.profilepic:
            filetoremove = oldusername + influencer.file_extension
            os.remove(os.path.join(os.getcwd(), 'static', 'profilepics',filetoremove))
        profilepic.save(os.path.join(os.getcwd(), 'static', 'profilepics', filename))
        influencer.profilepic = True
        influencer.file_extension = file_extension
    else:
        if username_changed:
            oldfilename = oldusername + influencer.file_extension
            newfilename = username + influencer.file_extension
            oldpath = os.path.join(os.getcwd(), 'static', 'profilepics', oldfilename)
            newpath = os.path.join(os.getcwd(), 'static', 'profilepics', newfilename)
            os.rename(oldpath, newpath)
    aboutme = request.form.get('aboutme')
    if influencer.aboutyou != aboutme and aboutme:
        influencer.aboutyou = aboutme
    insta_link = request.form.get('insta_link')
    if influencer_data.insta_link != insta_link and insta_link:
        influencer_data.insta_link = insta_link
    facebook_link = request.form.get('facebook_link')
    if influencer_data.facebook_link != facebook_link and facebook_link:
        influencer_data.facebook_link = facebook_link
    youtube_link = request.form.get('youtube_link')
    if influencer_data.youtube_link != youtube_link and youtube_link:
        influencer_data.youtube_link = youtube_link
    linkedin_link = request.form.get('linkedin_link')
    if influencer_data.linkedin_link != linkedin_link and linkedin_link:
        influencer_data.linkedin_link = linkedin_link
    instafoll = request.form.get('instafoll')
    if influencer_data.insta_fol != instafoll and instafoll:
        influencer_data.insta_fol = instafoll
    facebook_fol = request.form.get('facebook_fol')
    if influencer_data.facebook_fol != facebook_fol and facebook_fol:
        influencer_data.facebook_fol = facebook_fol
    youtube_fol = request.form.get('youtube_fol')
    if influencer_data.youtube_fol != youtube_fol and youtube_fol:
        influencer_data.youtube_fol = youtube_fol
    linkedin_fol = request.form.get('linkedin_fol')
    if influencer_data.linkedin_fol != linkedin_fol and linkedin_fol:
        influencer_data.linkedin_fol = linkedin_fol
    db.session.commit()
    flash('Your changes have been saved succesfully!', 'success')
    return redirect(url_for('influencer_myprofile', id=influencer.id))

@app.route('/sponsor/<int:id>/<int:campaign_id>/<int:influencer_id>/sendrequest')
@login_required
def sponsor_send_request(id, campaign_id, influencer_id):
    influencer = Influencer.query.get(influencer_id)
    sponsor = Sponsor.query.get(id)
    if sponsor.flag:
        flash('You are flagged! contact admin.')
        return redirect(url_for('sponsorhome', id=sponsor.id))
    campaign = Campaign.query.get(campaign_id)
    if campaign.flag:
        flash('This campaign is flagged! You can\'t request for this campaign.')
        return redirect(url_for('sponsorhome', id=sponsor.id))
    influencer = Influencer.query.get(influencer_id)
    if influencer.flag:
        flash('This influencer is flagged! you can\'t request him!')
        return redirect(url_for('sponsorhome', id=sponsor.id))
    
    request = SponsorRequests.query.filter_by(sponsor_id=id, campaign_id=campaign_id, 
                                              influencer_id=influencer_id).first()
    ongoingevent = Ongoingevents.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if request:
        flash('You have already requested this influencer!')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    if ongoingevent:
        flash('This influencer has already accepted the campaign!')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    newrequest = SponsorRequests(sponsor_id=id, campaign_id=campaign_id, influencer_id=influencer_id)
    db.session.add(newrequest)
    db.session.commit()
    flash('Request send succesfully!', 'success')
    return redirect(url_for('camapign_details_forsponsor', id=campaign_id))

@app.route('/sponsor/<int:id>/<int:influencer_id>/profile')
@login_required
def influencerprofileforsponsor(id, influencer_id):
    sponsor = Sponsor.query.get(id)
    influencer = Influencer.query.get(influencer_id)
    return render_template('influencerprofileforsponsor.html', sponsor=sponsor, influencer=influencer)

@app.route('/influencer/campaingacceptreject/<operation>/<int:campaign_id>/<int:influencer_id>/<int:sponsor_id>')
@login_required
def influencer_campaign_accept_reject(operation, campaign_id, influencer_id, sponsor_id):
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)
    sponsor = Sponsor.query.get(sponsor_id)
    if operation == "reject":
        request = SponsorRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
        db.session.delete(request)
        db.session.commit()
        return redirect(url_for('influencerhome', id=influencer_id))
    elif operation == "accept":
        if influencer.flag:
            flash('You have been flagged! You cant accept anymore request\'s.')
            return redirect(url_for('influencerhome', id=influencer_id))
        if sponsor.flag:
            flash('This sponsor has been flagged!')
            return redirect(url_for('influencerhome', id=influencer_id))
        if campaign.flag:
            flash('This campaign is flagged!')
            return redirect(url_for('influencerhome', id=influencer_id))
        event = Ongoingevents.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
        if not event:
            event = Ongoingevents(campaign_id=campaign_id, influencer_id=influencer_id, sponsor_id=sponsor_id, budget=campaign.budget)
            db.session.add(event)
            sponsor_request = SponsorRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
            db.session.delete(sponsor_request)
            influencer_request = InfluencerRequests.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
            if influencer_request:
                db.session.delete(influencer_request)
            db.session.delete(sponsor_request)
            db.session.commit()
            flash('done :)', category='success')
            return redirect(url_for('influencerhome', id=influencer_id))
        flash('This event is already running!')
        return redirect(url_for('influencerhome', id=influencer_id))
    flash('You provide an incorrect operation')
    return redirect(url_for('influencerhome', id=influencer_id))
    
@app.route('/influencer/<int:id>/<int:sponsor_id>/profile')
@login_required
def sponsorprofileforinfluencer(id, sponsor_id):
    influencer = Influencer.query.get(id)
    sponsor = Sponsor.query.get(sponsor_id)
    campaign_type = request.args.get('type')
    if campaign_type:
        campaigns = Campaign.query.filter((Campaign.sponsor_id==sponsor.id) & (Campaign.typeofcampaign==campaign_type) & (Campaign.communication=="public")).all()
        return render_template('sponsorprofileforinfluencer.html', influencer=influencer, sponsor=sponsor, campaigns=campaigns)
    campaigns = Campaign.query.filter((Campaign.sponsor_id==sponsor.id) & (Campaign.communication=="public")).all()
    return render_template('sponsorprofileforinfluencer.html', influencer=influencer, sponsor=sponsor, campaigns=campaigns)

@app.route('/influencer/<int:id>/<int:campaign_id>/deletenegotiation')
@login_required
def deletenegotiation(id, campaign_id):
    influencer = Influencer.query.get(id)
    campaign = Campaign.query.get(id)
    negotiate = Negotiate.query.filter_by(influencer_id = influencer.id, campaign_id=campaign.id).first()
    db.session.delete(negotiate)
    db.session.commit()
    flash('request deleted successfully!', 'success')
    return redirect(url_for('campaign', cmpid=campaign.id, infid=influencer.id))

@app.route('/sponsor/<int:id>/<int:campaign_id>/<int:influencer_id>/acceptnegotiation')
@login_required
def acceptnegotiation(id, campaign_id, influencer_id):
    sponsor = Sponsor.query.get(id)
    influencer = Influencer.query.get(influencer_id)
    campaign = Campaign.query.get(campaign_id)
    if sponsor.flag:
        flash('You are flagged!')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    if campaign.flag:
        flash('This campaign is flagged!')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    if influencer.flag:
        flash('This influencer is flagged! you cant accept his request.')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    naggot = Negotiate.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    ongoing_event = Ongoingevents.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    if ongoing_event:
        ongoing_event.budget = naggot.budget
        db.session.add(ongoing_event)
        db.session.delete(naggot)
        db.session.commit()
        flash('updated the ongoing event!', 'success')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    else:
        ongoing_event = Ongoingevents(campaign_id=campaign_id, influencer_id=influencer_id, 
                                      sponsor_id=sponsor.id, budget=naggot.budget)
        db.session.add(ongoing_event)
        db.session.delete(naggot)
        db.session.commit()
        flash('Created new ongoing event!', 'success')
        return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
    
@app.route('/sponsor/<int:id>/<int:campaign_id>/<int:influencer_id>/rejectnegotiation')
@login_required
def rejectnegotiation(id, campaign_id, influencer_id):
    naggot = Negotiate.query.filter_by(campaign_id=campaign_id, influencer_id=influencer_id).first()
    db.session.delete(naggot)
    db.session.commit()
    flash('Rejected!', 'message')
    return redirect(url_for('camapign_details_forsponsor', id=campaign_id))
        
@app.route('/influencer/<int:id>/<int:influencer_id>/completedcampaign')
@login_required
def campaign_completed(id, influencer_id):
    ongoing_event = Ongoingevents.query.get(id)
    completedevent = CompletedCampaigns(campaign_id=ongoing_event.campaign_id, influencer_id=ongoing_event.influencer_id, 
                                        budget=ongoing_event.budget, sponsor_id=ongoing_event.sponsor_id)
    db.session.add(completedevent)
    db.session.delete(ongoing_event)
    db.session.commit()
    flash('Please wait for the payment!')
    return redirect(url_for('influencerhome', id=influencer_id))

@app.route('/influencer/<int:id>/completedcampaigns')
@login_required
def influencer_completed_campaigns(id):
    influencer = Influencer.query.get(id)
    completedcampaigns = CompletedCampaigns.query.filter_by(influencer_id=id).all()
    return render_template('influencercompletedcampaigns.html', completedcampaigns=completedcampaigns, 
                           influencer=influencer)

@app.route('/sponsor/<int:id>/campaign/<int:campaign_id>/paynow')
@login_required
def dopayment(id, campaign_id):
    sponsor = Sponsor.query.get(id)
    completedcampaign = CompletedCampaigns.query.get(campaign_id)
    carddetail = SponsorCardDetails.query.filter_by(sponsor_id=sponsor.id).first()
    if carddetail:
        return render_template('paymentportal.html', sponsor=sponsor, completedcampaign=completedcampaign)
    flash('please provide your payment details')
    return redirect(url_for('updatecarddetails', id=sponsor.id))

@app.route('/sponsor/<int:id>/campaign/<int:campaign_id>/paynow', methods=['POST'])
@login_required
def post_dopayment(id, campaign_id):
    sponsor = Sponsor.query.get(id)
    completedcampaign = CompletedCampaigns.query.get(campaign_id)
    carddetail = SponsorCardDetails.query.filter_by(sponsor_id=sponsor.id).first()
    cardnumber = request.form.get('cardnumber')
    cvv = request.form.get('cvv')
    password = request.form.get('password')
    if not password:
        flash('Please provide your password')
        return redirect(url_for('dopayment', id=sponsor.id, campaign_id=completedcampaign.id))
    if not cardnumber or not cvv:
        flash('please provide the card details')
        return redirect(url_for('dopayment', id=sponsor.id, campaign_id=completedcampaign.id))
    if not check_password_hash(sponsor.passhash, password):
        flash('You entered wrong password!')
        return redirect(url_for('dopayment', id=sponsor.id, campaign_id=completedcampaign.id))
    if((int(cardnumber) == carddetail.cardnumber) and (int(cvv) == carddetail.cvv)):
        completedcampaign.payment_status = True
        db.session.add(completedcampaign)
        db.session.commit()
        flash('payment successfull!', 'success')
        return redirect(url_for('camapign_details_forsponsor', id=completedcampaign.campaign_id))

@app.route('/sponsor/<int:id>/updatecarddetails')
@login_required
def updatecarddetails(id):
    sponsor = Sponsor.query.get(id)
    return render_template('updatecarddetails.html', sponsor=sponsor)

@app.route('/sponsor/<int:id>/updatecarddetails', methods=['POST'])
@login_required
def post_updatecarddetails(id):
    sponsor = Sponsor.query.get(id)
    bank = request.form.get('bank')
    cardnumber = request.form.get('cardnumber')
    cvv = request.form.get('cvv')
    password = request.form.get('password')
    if not password:
        flash('Please provide your password')
        return redirect(url_for('updatecarddetails', id=sponsor.id))
    if not bank or not cardnumber or not cvv:
        flash('please provide all details')
        return redirect(url_for('updatecarddetails', id=sponsor.id))
    if not check_password_hash(sponsor.passhash, password):
        flash('You entered wrong password!')
        return redirect(url_for('updatecarddetails', id=sponsor.id))
    if len(cvv) != 3:
        flash('cvv should be a 3 digit number!')
        return redirect(url_for('updatecarddetails', id=sponsor.id))
    if len(cardnumber) != 16:
        flash('wrong cardnumber!')
        return redirect(url_for('updatecarddetails', id=sponsor.id))
    carddetail = SponsorCardDetails(sponsor_id=sponsor.id, bank=bank, cardnumber=cardnumber, cvv=cvv)
    db.session.add(carddetail)
    db.session.commit()
    flash('Payment details added successfully!', 'success')
    return redirect(url_for('sponsorhome', id=sponsor.id))
    
@app.route('/sponsor<int:id>/stats')
@login_required
def sponsor_stats(id):
    sponsor = Sponsor.query.get(id)
    total_campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    total_campaigns_completed = sponsor.completed_campaigns
    totalcampaign_type_chart_data = dict()
    completedcampaign_type_chart_data = dict()
    tc_type_data = dict()
    tc_type_data['labels'] = []
    tc_type_data['data'] = []
    if total_campaigns:
        for campaign in total_campaigns:
            if campaign.typeofcampaign in totalcampaign_type_chart_data:
                totalcampaign_type_chart_data[campaign.typeofcampaign] += 1
            else:
                totalcampaign_type_chart_data[campaign.typeofcampaign] = 1
        tc_type_data['labels'] = list(totalcampaign_type_chart_data.keys())
        tc_type_data['data'] = list(totalcampaign_type_chart_data.values())
    cc_type_data = dict()
    cc_type_data['data'] = []
    cc_type_data['labels'] = []
    if total_campaigns_completed:
        for campaign in total_campaigns_completed:
            if campaign.campaign.typeofcampaign in completedcampaign_type_chart_data:
                completedcampaign_type_chart_data[campaign.campaign.typeofcampaign] += 1
            else:
                completedcampaign_type_chart_data[campaign.campaign.typeofcampaign] = 1
        cc_type_data['labels'] = list(completedcampaign_type_chart_data.keys())
        cc_type_data['data'] = list(completedcampaign_type_chart_data.values())
    return render_template('sponsorstats.html', total_campaigns=total_campaigns,
                        total_campaigns_completed=total_campaigns_completed,
                        tc_type_data=tc_type_data, cc_type_data=cc_type_data, sponsor=sponsor)

@app.route('/influencer/<int:id>/stats')
@login_required
def influencer_stats(id):
    influencer = Influencer.query.get(id)
    total_campaigns = Ongoingevents.query.filter_by(influencer_id=influencer.id).all()
    tc_chart_data = dict()
    if total_campaigns:
        for event in total_campaigns:
            if event.campaign.typeofcampaign in tc_chart_data:
                tc_chart_data[event.campaign.typeofcampaign] += 1
            else:
                tc_chart_data[event.campaign.typeofcampaign] = 1

    completed_campaigns = CompletedCampaigns.query.filter_by(influencer_id=influencer.id).all()
    if completed_campaigns:
        for event in completed_campaigns:
            if event.campaign.typeofcampaign in tc_chart_data:
                tc_chart_data[event.campaign.typeofcampaign] += 1
            else:
                tc_chart_data[event.campaign.typeofcampaign] = 1

    tccdata = dict()
    tccdata['labels'] = list(tc_chart_data.keys())
    tccdata['data'] = list(tc_chart_data.values())

    tc_joined = sum(tccdata['data'])
    return render_template('influencerstats.html', influencer=influencer, tccdata=tccdata, tc_joined=tc_joined)

@app.route('/admin/<int:id>stats')
@admin_required
def admin_stats(id):
    admin = Admin.query.get(id)
    all_campaigns = Campaign.query.all()
    all_cc_data = dict()
    allc = 0
    acc_data = dict() #all_campaigns_chart_data
    acc_data['labels'] = []
    acc_data['data'] = []
    if all_campaigns:
        for campaign in all_campaigns:
            if campaign.typeofcampaign in all_cc_data:
                all_cc_data[campaign.typeofcampaign] += 1
            else:
                all_cc_data[campaign.typeofcampaign] = 1

        acc_data['labels'] = list(all_cc_data.keys())
        acc_data['data'] = list(all_cc_data.values())
        allc = sum(acc_data['data'])

    total_campaigns = Ongoingevents.query.all()
    tc_chart_data = dict()
    if total_campaigns:
        for event in total_campaigns:
            if event.campaign.typeofcampaign in tc_chart_data:
                tc_chart_data[event.campaign.typeofcampaign] += 1
            else:
                tc_chart_data[event.campaign.typeofcampaign] = 1

    completed_campaigns = CompletedCampaigns.query.all()
    if completed_campaigns:
        for event in completed_campaigns:
            if event.campaign.typeofcampaign in tc_chart_data:
                tc_chart_data[event.campaign.typeofcampaign] += 1
            else:
                tc_chart_data[event.campaign.typeofcampaign] = 1

    tccdata = dict()
    tccdata['labels'] = list(tc_chart_data.keys())
    tccdata['data'] = list(tc_chart_data.values())
    tc_joined = sum(tccdata['data'])

    return render_template('adminstats.html', admin=admin, acc_data=acc_data,
                           tccdata=tccdata, tc_joined=tc_joined, allc=allc)

@app.route('/influencer/<int:id>/feedback')
@login_required
def influencer_feedback(id):
    influencer = Influencer.query.get(id)
    return render_template('influencerfeedback.html', influencer=influencer)

@app.route('/influencer/<int:id>/feedback', methods=['POST'])
@login_required
def post_influencer_feedback(id):
    influencer = Influencer.query.get(id)
    camp_exp = request.form.get('campaignexperience')
    suggestions = request.form.get('suggestion')
    if not camp_exp or not suggestions:
        flash('Not provided the required Info!')
        return redirect(url_for('influencer_feedback', id=influencer.id))
    newfeedback = InfluencerFeedbackData(influencer_id=influencer.id, camp_exp=camp_exp, suggestions=suggestions)
    db.session.add(newfeedback)
    db.session.commit()
    return redirect(url_for('influencerhome', id=influencer.id))

@app.route('/sponsor/<int:id>/feedback')
@login_required
def sponsor_feedback(id):
    sponsor = Sponsor.query.get(id)
    return render_template('sponsorfeedback.html', sponsor=sponsor)

@app.route('/sponsor/<int:id>/feedback', methods=['POST'])
@login_required
def post_sponsor_feedback(id):
    sponsor = Sponsor.query.get(id)
    camp_exp = request.form.get('campaignexperience')
    suggestions = request.form.get('suggestion')
    if not camp_exp or not suggestions:
        flash('Not provided the required Info!')
        return redirect(url_for('sponsor_feedback', id=sponsor.id))
    newfeedback = SponsorFeedbackData(sponsor_id=sponsor.id, camp_exp=camp_exp, suggestions=suggestions)
    db.session.add(newfeedback)
    db.session.commit()
    return redirect(url_for('sponsorhome', id=sponsor.id))

@app.route('/admin/<int:id>/influencer/feedback')
@admin_required
def influencer_fb(id):
    admin = Admin.query.get(id)
    feedback = InfluencerFeedbackData.query.all()
    return render_template('admininfluencerfb.html', admin=admin, feedback=feedback)

@app.route('/admin/<int:id>/sponsor/feedback')
@admin_required
def sponsor_fb(id):
    admin = Admin.query.get(id)
    feedback = SponsorFeedbackData.query.all()
    return render_template('adminsponsorfb.html', admin=admin, feedback=feedback)
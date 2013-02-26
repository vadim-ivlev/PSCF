from google.appengine.ext import db

class fiscal_data(db.Model):
    iso=db.StringProperty()
    currency=db.StringProperty()
    year=db.IntegerProperty()
    debt_exports=db.FloatProperty()
    public_plus_private_debt_gdp=db.FloatProperty()
    domestic_plus_external_debt_gdp=db.FloatProperty()
    debt_gnp=db.FloatProperty()
    currency_crisis=db.IntegerProperty()
    inflation_crisis=db.IntegerProperty()
    stock_market_crash=db.IntegerProperty()
    soverign_debt_crisis_domestic=db.IntegerProperty()
    sovereign_debt_crisis_external=db.IntegerProperty()
    banking_crisis=db.IntegerProperty()
    crisis_tally=db.IntegerProperty()
    gov_revenue=db.FloatProperty()
    gov_spending=db.FloatProperty()
    gov_debt=db.FloatProperty()
    int_on_gov_debt=db.FloatProperty()
    Short_term_interest_rate=db.FloatProperty()
    gdp=db.FloatProperty()
    gov_bond_yield=db.FloatProperty()
    price_index=db.FloatProperty()
    int_revenue=db.FloatProperty()
    outstanding_bond=db.FloatProperty()
    avg_maturity=db.FloatProperty()
    int_expense_general=db.FloatProperty()
    gov_revenue_general=db.FloatProperty()
    gov_spending_general=db.FloatProperty()
    source=db.TextProperty()
    income_tax_revenue=db.FloatProperty()
    consumption_tax_revenue=db.FloatProperty()
    military_spending=db.FloatProperty()
    social_insurance_spending=db.FloatProperty()
    health_expenditure=db.FloatProperty()
    comments=db.TextProperty()
    user_comment=db.TextProperty()
    domestic_debt=db.FloatProperty()
    foreign_debt=db.FloatProperty()



class countries(db.Model):
    iso=db.StringProperty()
    country=db.StringProperty()
 
class currencies(db.Model):
    currency_iso=db.StringProperty()
    currency_name=db.StringProperty()
    euro_conversion=db.FloatProperty()
 
class data_source(db.Model):
    iso=db.StringProperty()
    period=db.StringProperty()
    series=db.TextProperty()
    sources=db.TextProperty()
    value=db.FloatProperty()
 
class commentator_comments(db.Model):
    id=db.IntegerProperty()
    page=db.StringProperty()
    name=db.StringProperty()
    email=db.StringProperty()
    uri=db.StringProperty()
    ip=db.TextProperty()
    timestamp=db.IntegerProperty()
    comment=db.TextProperty()
    notify=db.IntegerProperty()
    spam=db.IntegerProperty()
 


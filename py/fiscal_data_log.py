import logging
from google.appengine.ext import webapp
from google.appengine.api import memcache
import db
from google.appengine.api import users
import json





class MainHandler(webapp.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        id=self.request.get('id')

        (conn,cursor)=db.getConnection()
        jsonString=db.executeSelect(cursor,"SELECT * FROM fiscal_data_log  WHERE id=%s ORDER BY change_date"  % id)
        self.response.out.write( jsonString )
        conn.close()






    def post(self):
       #if the user is not logined in return
        if not users.get_current_user():
            return

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'


        id=self.request.get('id')
        jsonStringRequest=self.request.body

        request_dictionary=db.fromJsonString(jsonStringRequest)[0]
        active=request_dictionary.get('active')
        status=request_dictionary.get('status')

        (conn,cursor)=db.getConnection()

        # check if the user is a moderator
        if db.isModerator(cursor,users.get_current_user().nickname())==False :
            return


        # set all records in fiscal_data_log as not active if this is activation
        if active == 'yes':
            cursor.execute("UPDATE fiscal_data_log SET active='no' WHERE id=%s  " % id)

        #add verification_date

        # update record in the _log table
        (id_value,updateQuery)=db.buildUpdateQuery('fiscal_data_log','log_id','verified_by',users.get_current_user().nickname(), jsonStringRequest)
        cursor.execute(updateQuery)

        # fetch saved record
        json_updated_log_record=db.executeSelect( cursor ,"SELECT *  FROM fiscal_data_log  WHERE log_id=%s" % id_value)

        list=db.fromJsonString(json_updated_log_record)
        updated_log_dictionary=list[0]


        # update fiscal_data
        if active=='yes':
            #delete redundant fields
            if 'log_id' in updated_log_dictionary: del updated_log_dictionary['log_id']
            if 'verified_by' in updated_log_dictionary: del updated_log_dictionary['verified_by']
            if 'verification_date' in updated_log_dictionary: del updated_log_dictionary['verification_date']
            if 'active' in updated_log_dictionary: del updated_log_dictionary['active']

            #!!!!!! set action to switch off update trigger on fiscal_data
            updated_log_dictionary['action']='verify'

            #make json string
            s=json.dumps(list)

            # build query
            (id_val,fiscal_data_updateQuery)=db.buildUpdateQuery('fiscal_data','id',None,None, s)
            logging.info(  fiscal_data_updateQuery)
            cursor.execute(fiscal_data_updateQuery)

        else:
            # it is active (present in fiscal_data table)
            # and status changed then update fiscal_data
            if updated_log_dictionary.get("active")=='yes' and status is not None:
                #update record in fiscal_data
                cursor.execute("UPDATE fiscal_data SET action='verify', status='%s'   WHERE id=%s" % (status,id) )



        # extract iso from fiscal_data_log record
        dict=db.fromJsonString(json_updated_log_record)[0]
        iso=dict['iso']

        #refresh mem cache
        memcache.delete('iso_'+iso)
        jsonString=db.executeSelect(cursor,"SELECT *  FROM fiscal_data  WHERE iso=\"%s\"" % iso)
        if len (jsonString)<990000:
            memcache.add('iso_'+iso, jsonString)

        # should write ??
        # {"success":true,"message":"Updated User 2","data":{"id":2,"first":"Wilma","last":"Flintstone","email":"wilma@flintstone.comd"}}
        self.response.out.write( json_updated_log_record )

        conn.close()




app = webapp.WSGIApplication([('/fiscal_data_log.*', MainHandler)],
                             debug=True)


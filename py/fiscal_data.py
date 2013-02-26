import logging
from google.appengine.ext import webapp
from google.appengine.api import memcache
import db
from google.appengine.api import users





class MainHandler(webapp.RequestHandler):

#    def executeSelect(self,cursor,selectQuery ):
#        '''
#        Executes selectQuery and  returns database recordset
#        serialized into JSON string.
#        '''
#        cursor.execute(selectQuery)
#        columns_description = cursor.description
#        rows=cursor.fetchall()
#        jsonString=db.getJsonString(rows,columns_description )
#        return jsonString


    def get(self):
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        iso=self.request.get('iso')
        format=self.request.get('format')

        # try to fetch json string from mem cache
        jsonString = memcache.get('iso_'+iso)
#        if jsonString is not None:
#            self.response.out.write( jsonString )
#            logging.info("DATA FROM CACHE: %s Size=%s bytes." % (iso, len(jsonString) ) )
#            return

        # if mem cache is empty, get it from database
        if jsonString is None:
            (conn,cursor)=db.getConnection()

            jsonString=db.executeSelect(cursor,"SELECT * FROM fiscal_data f  WHERE f.iso=\"%s\" "  % iso)
            conn.close()

            if len (jsonString)<990000:
                memcache.add('iso_'+iso, jsonString)

        if format=="csv":
            self.response.headers['Content-Type'] = 'application/csv'
            self.response.headers['Content-Disposition'] = str("attachment; filename=fiscal_data_%s.csv" % iso)
            self.response.out.write( db.jsonToCSV(jsonString) )
        elif format=="html":
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write( db.jsonToHTML(jsonString) )
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write( jsonString )







    def post(self):

        #if the user is not logined in return
        if not users.get_current_user():
            return;

        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'

        iso=self.request.get('iso')
        jsonStringRequest=self.request.body

        (conn,cursor)=db.getConnection()

        # check if the user is a spammer
        if db.isSpammer(cursor,users.get_current_user().nickname()):
            return

        # update query
        (id_value,updateQuery)=db.buildUpdateQuery('fiscal_data','id','changed_by',users.get_current_user().nickname(), jsonStringRequest)

        cursor.execute(updateQuery)

        # fetch saved record
        jsonStringOneRecord=db.executeSelect( cursor ,"SELECT *  FROM fiscal_data f  WHERE f.id=%s" % id_value)

        # should write ??
        # {"success":true,"message":"Updated User 2","data":{"id":2,"first":"Wilma","last":"Flintstone","email":"wilma@flintstone.comd"}}
        self.response.out.write( jsonStringOneRecord )

        #refresh mem cache
        memcache.delete('iso_'+iso)
        jsonString=db.executeSelect(cursor,"SELECT *  FROM fiscal_data f  WHERE f.iso=\"%s\"" % iso)
        if len (jsonString)<990000:
            memcache.add('iso_'+iso, jsonString)

        conn.close()




app = webapp.WSGIApplication([('/fiscal_data.*', MainHandler)],
                             debug=True)


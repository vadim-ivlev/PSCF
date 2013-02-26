from google.appengine.ext import webapp
import db




class MainHandler(webapp.RequestHandler):
    def get(self):
#        conn = db.getConnectionOnly()
#        cursor = conn.cursor()
        (conn,cursor)=db.getConnection()

        cursor.execute("""
            SELECT distinct c.*
            FROM countries c, fiscal_data f
            WHERE c.iso=f.iso
            ORDER BY c.country
            """)


        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Access-Control-Allow-Origin'] = '*'



        columns_description = cursor.description
        rows=cursor.fetchall()
        self.response.out.write( db.getJsonString(rows,columns_description ))
        conn.close()


#        self.response.headers['Content-Type'] = 'application/json'
#        self.response.headers['Access-Control-Allow-Origin'] = '*'
#
#        (conn,cursor)=db.getConnection()
#        jsonString=db.executeSelect(cursor,"""
#            SELECT distinct countries.country, countries.iso
#            FROM countries, fiscal_data
#            WHERE countries.iso=fiscal_data.iso
#            ORDER BY country
#            """)
#
#        self.response.out.write(jsonString)
#        conn.close()


app = webapp.WSGIApplication([('/countries', MainHandler)],
                             debug=True)

